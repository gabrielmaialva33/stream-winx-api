from telethon import TelegramClient

from core import API_ID, API_HASH, BOT_TOKEN
from core.logging import logger


# client = TelegramClient('stream_session', API_ID, API_HASH)


# async def start_client():
#     logger(__name__).info("Starting Telegram client")
#     await client.start(bot_token=BOT_TOKEN)
#
#
# async def stop_client():
#     logger(__name__).info("Stopping Telegram client")
#     await client.disconnect()
class Telegram:
    def __init__(self):
        self.client = TelegramClient("stream_session", API_ID, API_HASH)

    async def start(self):
        logger(__name__).info("Starting Telegram client")
        await self.client.start(bot_token=BOT_TOKEN)

    async def stop(self):
        logger(__name__).info("Stopping Telegram client")
        await self.client.disconnect()

    async def get_client(self):
        return self.client

    async def get_file_info(self):
        channel_id = -1001774402469
        message_id = 7206

        chat = await self.client.get_entity(channel_id)
        message = await self.client.get_messages(chat, ids=message_id)

        document = message.media.document

        return document

    async def get_file_stream(self, document, start: int, end: int):
        async for chunk in self.client.iter_download(
            document,
            offset=start,
            limit=end - start + 1,
            chunk_size=1024 * 1024,  # Tamanho do chunk: 1MB
        ):
            yield chunk
