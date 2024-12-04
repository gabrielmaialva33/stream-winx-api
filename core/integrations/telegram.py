from typing import List, Dict

from telethon import TelegramClient
from telethon.tl.types import Message

from core import API_ID, API_HASH, STRING_SESSION, CHANNEL_ID, logger
from core.exceptions import BadRequestException
from core.utils import decode_session

telethon_session = decode_session(STRING_SESSION)


class Telegram:
    def __init__(self):
        self.client = TelegramClient(telethon_session, API_ID, API_HASH)
        self.channel_id = CHANNEL_ID

    async def start(self):
        logger.info("Starting Telegram client")
        await self.client.start()

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
            document, offset=start, limit=end - start + 1, chunk_size=1024 * 1024
        ):
            yield chunk

    async def get_channel(self, channel_id: int):
        return await self.client.get_entity(channel_id)

    async def get_history(self, limit: int = 30, offset_id: int = 0) -> List[Message]:
        history = await self.client.get_messages(
            entity=self.channel_id, limit=limit, offset_id=offset_id
        )
        return history

    async def grouped_posts(
        self, limit: int = 30, offset_id: int = 0
    ) -> Dict[str, List[Message]]:
        history = await self.get_history(limit, offset_id)
        messages = [msg for msg in history if isinstance(msg, Message)]
        grouped_messages = [msg for msg in messages if msg.grouped_id]

        grouped_dict: Dict[str, List[Message]] = {}
        for message in grouped_messages:
            group_id = str(message.grouped_id)
            if group_id not in grouped_dict:
                grouped_dict[group_id] = []
            grouped_dict[group_id].append(message)

        return grouped_dict

    async def list_messages(self, limit: int = 100, offset_id: int = 0) -> List[Dict]:
        grouped_posts = await self.grouped_posts(limit, offset_id)
        print("grouped_posts", grouped_posts)
        posts = []

        for group in grouped_posts.values():
            reactions = []
            info = next((msg for msg in group if msg.message), None)

            if info:
                # Extrair reações
                if info.reactions:
                    for reaction in info.reactions.results:
                        emoticon = getattr(reaction.reaction, "emoticon", None)
                        if emoticon:
                            reactions.append(
                                {"reaction": emoticon, "count": reaction.count}
                            )

                parsed_data = parse_message_content(info.message)

                post = {
                    "image_url": "",  # Você pode implementar a lógica para URLs de imagens
                    "grouped_id": str(info.grouped_id),
                    "message_id": info.id,
                    "date": info.date.isoformat(),
                    "author": info.post_author,  # Certifique-se de que este atributo existe
                    "reactions": reactions,
                    "original_content": info.message,
                    "parsed_content": parsed_data,
                }

                posts.append(post)

        return posts

    async def get_image(self, message_id: int) -> bytes:
        message = await self.client.get_messages(entity=self.channel_id, ids=message_id)
        if not message or not message.photo:
            raise BadRequestException("No image found in the provided message.")

        image_bytes = await self.client.download_media(message.photo)
        return image_bytes
