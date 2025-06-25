import asyncio
import logging
import requests
import boto3

from bs4 import BeautifulSoup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from collections import defaultdict
from configs.news_conf import BAN_TIME, TIME_WINDOW, MAX_MESSAGES, NEWS_SOURCE_URL, HEADERS, HOURS, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types
from datetime import datetime, timedelta
from aiogram.dispatcher.handler import CancelHandler
from model.news_model import NewsModel
from googletrans import Translator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

flood_control = defaultdict(list)
banned_users = {}
warned_users = set()
perma_banned_users = set()
first_run_done = False
last_run_time = None
cooldown_minutes = 5
translator = Translator()

translate_client = boto3.client(
    service_name='translate',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def translate_to_ukrainian(text: str) -> str:
    if not text:
        return ""

    try:
        response = translate_client.translate_text(
            Text=text,
            SourceLanguageCode='da',
            TargetLanguageCode='uk'
        )
        return response.get('TranslatedText', text)
    except Exception as e:
        logger.error(f"❌ AWS Translate error: {e}")
        return text

def first_lunch_handler():
    global first_run_done, last_run_time
    url = extract_latest_news_url()
    latest_new = extract_new(url)
    if latest_new:
        first_run_done = True
        last_run_time = datetime.now()
        logger.info(f"First launch: {latest_new.title} done.")
        return latest_new
    else:
        logger.error("Error while first start.")
        return None
    
async def run_scheduled_task():
    global last_run_time
    now = datetime.now()
    if last_run_time and (now - last_run_time) < timedelta(minutes=cooldown_minutes):
        logger.info("Skipping scheduler-planer (too fast after last run).")
        return

    logger.info("Starting scheduled task...")
    url = extract_latest_news_url()
    latest_new = extract_new(url)

    if latest_new:
        last_run_time = now
        logger.info(f"✅ Scheduled: {latest_new.title}")
        return latest_new
    else:
        logger.error("Error parsing new.")
        return None

def start_scheduler():
    scheduler = AsyncIOScheduler()
    for hour in HOURS:
        trigger = CronTrigger(hour=hour, minute=0)
        scheduler.add_job(run_scheduled_task, trigger)

    scheduler.start()
    logger.info("Scheduler started.")

def extract_latest_news_url():
    response = requests.get(NEWS_SOURCE_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    teaser = soup.select_one("div.teaser.teaser--with-image")
    if not teaser:
        return None
    title_tag = teaser.select_one("h4.teaser__title a")
    if not title_tag:
        return None
    link = title_tag["href"]
    full_link = f"https://www.berlingske.dk{link}" if link.startswith("/") else link
    return full_link

def extract_new(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        title_tag = soup.find('h2', class_='article-header__title')
        image_tag = soup.find('img', class_='article-top-media__image')
        content_tag = soup.find('article', id='articleBody')
        pub_time_tag = soup.find('div', class_="article-byline__date")
        author_tag = soup.find('p', class_="article-byline__author-name")
        title = title_tag.get_text(strip=True) if title_tag else ""
        image_url = image_tag['src'] if image_tag else None
        content = ' '.join(p.get_text(strip=True) for p in content_tag.find_all('p')) if content_tag else ""
        pub_time = pub_time_tag.get_text(strip=True) if pub_time_tag else None
        author = author_tag.get_text(strip=True) if author_tag else url
        logger.info(f"📰 {title[:60]}... ({len(content)} символів)")
        return NewsModel(
            source=url,
            title=title,
            content=content,
            image_url=image_url,
            publication_time=pub_time,
            author=author,
            related_links=[]
        )

    except Exception as e:
        logger.error(f"❌ scrape_news помилка: {e}")
        return None

async def unban_task(user_id, banned_users, bot):
    await asyncio.sleep(int(BAN_TIME))
    if user_id in banned_users:
        del banned_users[user_id]
        await bot.send_message(
            user_id,
            "Час бану закінчено. Наступного разу він може бути вічним."
        )
        logger.info(f"✅ User {user_id} unbloked.")

class AntiFloodMiddleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        user_id = message.from_user.id
        now = datetime.now()

        if user_id in perma_banned_users:
            logger.warning(f"⛔ User {user_id} blocked permanently!")
            raise CancelHandler()

        if user_id in banned_users and banned_users[user_id] > now:
            logger.warning(f"⛔ User {user_id} is in mute.")
            raise CancelHandler()

        flood_control[user_id] = [
            t for t in flood_control[user_id]
            if now - t < timedelta(seconds=int(TIME_WINDOW))
        ]
        
        flood_control[user_id].append(now)

        if len(flood_control[user_id]) > int(MAX_MESSAGES):
            if user_id not in warned_users:
                warned_users.add(user_id)
                await message.answer("⚠️ Виявлено флуд. Якщо продовжуватимеш - отримаеш бан.")
                logger.info(f"⚠️ User {user_id} received message about flood.")
            elif user_id not in perma_banned_users:
                banned_users[user_id] = now + timedelta(seconds=int(BAN_TIME))
                await message.answer(f"🚫 Тебе заблокировано за флуд на {int(BAN_TIME)} секунд.")
                logger.warning(f"🚫 User {user_id} received mute for {int(BAN_TIME)} sec.")
                asyncio.create_task(unban_task(user_id, banned_users, message.bot))
                raise CancelHandler()
            else:
                perma_banned_users.add(user_id)
                await message.answer("🚨 Ти отримав бан на тривалий час.")
                logger.critical(f"⛔ User {user_id} banned permanently.")
                raise CancelHandler()
            