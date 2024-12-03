from telethon.tl.types import Document

from app.telegram_client import client


async def get_file_info():
    channel_id = -1001774402469
    message_id = 7206

    chat = await client.get_entity(channel_id)
    message = await client.get_messages(chat, ids=message_id)

    document = message.media.document

    return document


async def get_file_stream(document: Document, start: int, end: int):
    async for chunk in client.iter_download(
            document,
            offset=start,
            limit=end - start + 1,
            chunk_size=1024 * 1024,  # Tamanho do chunk: 1MB
    ):
        yield chunk
