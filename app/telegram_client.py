from telethon import TelegramClient

from app.config import API_ID, API_HASH, BOT_TOKEN

client = TelegramClient('stream_session', API_ID, API_HASH)


async def start_client():
    await client.start(bot_token=BOT_TOKEN)


async def stop_client():
    await client.disconnect()
