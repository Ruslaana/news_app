# TODO

"""
из-за того что нету реального обращения к БД, нужно имплементировать кастомные методы CRUD
"""

# реализовать метод добавления новости в коллекцию

# реализовать мтод получения новости из коллекции

# реализовать метод удаления ОДНОЙ новости из коллекции

import json
import os
from collections import deque

news_collection = deque(maxlen=2)
SUBSCRIBERS_FILE = "subscribers.json"

# --- NEWS ---


def add_news(news: dict):
    news_collection.append(news)


def get_all_news():
    return list(news_collection)


def get_latest_news():
    return news_collection[-1] if news_collection else None


def delete_latest_news():
    if news_collection:
        news_collection.pop()

# --- SUBSCRIBERS ---


def load_subscribers():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_subscribers(subs: list):
    with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
        json.dump(subs, f, indent=2)


def add_subscriber(chat_id: int):
    subs = load_subscribers()
    if chat_id not in subs:
        subs.append(chat_id)
        save_subscribers(subs)


def get_subscribers():
    return load_subscribers()
