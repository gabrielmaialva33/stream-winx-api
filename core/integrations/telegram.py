from telethon import TelegramClient

from core import API_ID, API_HASH, BOT_TOKEN, logger


# from core.logging import logger


class Telegram:
    def __init__(self):
        self.client = TelegramClient("stream_session", API_ID, API_HASH)

    async def start(self):
        logger.info("Starting Telegram client")
        await self.client.start(bot_token=BOT_TOKEN)

    async def stop(self):
        logger.info("Stopping Telegram client")
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
                chunk_size=1024 * 1024
        ):
            yield chunk
