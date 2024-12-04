from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import Message

from app.schemas import PaginationData, Post, PaginatedPosts
from core import logger
from core.cache import CacheManager
from core.integrations import TelegramClientWrapper

cache = CacheManager(max_size=100, ttl=3600)


@dataclass
class TelegramRepository:
    client: TelegramClientWrapper = field(default_factory=TelegramClientWrapper)
    channel_id: int = field(init=False)
    channel: Optional[Any] = None

    def __post_init__(self):
        self.channel_id = self.client.channel_id

    async def start_client(self):
        if not self.client.is_connected():
            await self.client.connect()
        await self.client.start()
        logger.info("Connected to Telegram")
        self.channel = await self.client.get_entity(self.channel_id)

    async def stop_client(self):
        await self.client.disconnect()
        logger.info("Disconnected from Telegram")

    async def _get_history(self, pagination: PaginationData) -> List[Message]:
        history = await self.client(
            GetHistoryRequest(
                peer=self.channel,
                limit=pagination.limit,
                offset_id=pagination.offset_id,
                offset_date=pagination.offset_date,
                add_offset=pagination.add_offset,
                max_id=pagination.max_id,
                min_id=pagination.min_id,
                hash=self.channel.access_hash,
            )
        )
        return history.messages

<<<<<<< HEAD
    async def _grouped_posts(self, pagination: PaginationData) -> Dict[str, List[Message]]:
        history = await self._get_history(pagination)
=======
    async def grouped_posts(
        self, pagination: PaginationData
    ) -> Dict[str, List[Message]]:
        history = await self.get_history(pagination)
>>>>>>> 456837447f2fe7e45ca71165907d1d4b6c72eeb5
        messages = [
            message
            for message in history
            if hasattr(message, "grouped_id") and message.grouped_id
        ]

        grouped_messages = {}
        for message in messages:
            group_id = str(message.grouped_id)
            if group_id not in grouped_messages:
                grouped_messages[group_id] = []
            grouped_messages[group_id].append(message)

        return grouped_messages

    async def paginate_posts(self, pagination: PaginationData) -> PaginatedPosts:
        posts = []
        grouped_posts = await self._grouped_posts(pagination)
        for group in grouped_posts.values():
            info = next(
                (
                    msg
                    for msg in group
                    if msg.__class__.__name__ == "Message" and msg.message
                ),
                None,
            )

            if info:
                post = Post.from_message(info)
                posts.append(post)

        posts.sort(key=lambda x: x.message_id, reverse=True)

        return PaginatedPosts(data=posts, pagination=pagination)
