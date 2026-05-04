import logging
import json
import os

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

with open('config/config.json', 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

with open('config/templates.json', 'r', encoding='utf-8') as templates_file:
    templates = json.load(templates_file)

logging.basicConfig(level=config['loggingLevel'])

proxy = config.get('proxy') or os.environ.get('HTTPS_PROXY')

    # Создаем сессию с прокси
session = AiohttpSession(proxy=proxy)

bot = Bot(token=config['token'], session=session)
dp = Dispatcher()

bot_id = bot.id


async def main() -> None:
    await dp.start_polling(bot)
