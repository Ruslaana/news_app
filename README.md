# news_channel

A Telegram bot for automatically fetching, parsing, and delivering the latest news articles, with anti-flooding controls.

## Features

- **Automated News Fetching**: Periodically scrapes news articles from a configured news source.
- **Telegram Bot**: Sends news previews and full articles to users upon request, including images.
- **Anti-Flood Middleware**: Protects against spam and flooding by muting or banning users who exceed rate limits.
- **Scheduler**: Uses APScheduler to run news fetching tasks at specific times.
- **Configurable via Environment**: All API tokens, webhook URLs, and runtime parameters are configurable using environment variables.

## How It Works

1. **Scheduler** triggers fetching of the latest news at scheduled hours (customizable).
2. **News Extraction**: Scrapes news articles, extracting title, content, publication time, author, and images.
3. **Telegram Delivery**: On `/start`, users receive a preview with an option to "Read More". Full article text is split and sent if too long.
4. **Anti-Flood Protection**: Limits repeated user interactions using a middleware. Temporarily or permanently bans repeat offenders.

## Getting Started

### Prerequisites

- Python 3.10+
- Telegram Bot Token

### Installation

```bash
git clone https://github.com/BevarUkraine/news_channel.git
cd news_channel
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and fill in the necessary values:

- `TOKEN` — Your Telegram bot token
- `WEBHOOK_URL`, `WEBHOOK_PATH`, `WEBAPP_HOST`, `WEBAPP_PORT` — Webhook configuration
- `NEWS_SOURCE_URL` — Source URL for news scraping
- `BAN_TIME`, `MAX_MESSAGES`, `TIME_WINDOW` — Anti-flood settings

### Running

```bash
python main.py
```

The bot will start, set up webhooks, and begin fetching and delivering news.


## Customization

- **News Source**: Change the `NEWS_SOURCE_URL` in your `.env` to scrape from another compatible news site.
- **Scheduler Times**: Edit the `HOURS` list in `configs/news_conf.py` to control when news is fetched.
- **Anti-Flood Parameters**: Adjust `BAN_TIME`, `MAX_MESSAGES`, `TIME_WINDOW` in the environment for custom rate limits.
