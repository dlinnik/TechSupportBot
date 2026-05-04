import logging
from aiogram.filters import Command
from aiogram import types, F, Bot
from bot import dp, config, templates, bot_id

# Добавьте в начало файла
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

messages = {}

@dp.message(Command('ping'))
async def ping(message: types.Message) -> None:
    await message.reply('pong')

@dp.message(Command('id'))
async def get_id(message: types.Message) -> None:
    await message.reply(f'Chat ID: {message.chat.id}')

@dp.message(F.chat.type == 'private' and Command('start', 'help'))
async def help_msg(message: types.Message) -> None:
    await message.reply(templates['helpMessage'])

@dp.message(
    F.chat.id == config['chatId'] and
    F.reply_to_message.from_user.id == bot_id
)
async def answer(message: types.Message, bot: Bot) -> None:
    cashed_user_id = messages.get(message.reply_to_message.message_id, None)
    try:
        user_id = message.reply_to_message.forward_from.id
    except Exception as e:
        logger.error(f"Ошибка получения forward_from: {e}")
        user_id = cashed_user_id

    if not user_id:
        user_id = cashed_user_id
    if not user_id:
        await message.reply(templates['userNotFound'])
        return

    if config['systemMessages']:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=templates['answerReceived']
            )
        except Exception as e:
            logger.error(f"Ошибка отправки системного сообщения: {e}")

    try:
        await message.copy_to(chat_id=user_id)
    except Exception as e:
        logger.error(f"Ошибка копирования сообщения: {e}")
        await message.reply(templates['cantSend'])
        return

    if config['systemMessages']:
        await message.reply(templates['answerSent'])

@dp.message(F.chat.type == 'private')
async def question(message: types.Message) -> None:
    try:
        result = await message.forward(chat_id=config['chatId'])
        logger.info(f"Сообщение переслано: {result.message_id}")
    except Exception as e:
        logger.error(f"Ошибка пересылки сообщения: {e}")
        await message.reply(templates['cantSend'])
        return

    messages[result.message_id] = message.from_user.id
    if config['systemMessages']:
        await message.reply(templates['questionSent'])