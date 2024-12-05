from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import Message

from app.schemas import PaginationData, Post, PaginatedPosts
from core import logger
from core.cache import cache
from core.integrations import TelegramClientWrapper


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

    async def _grouped_posts(
        self, pagination: PaginationData
    ) -> Dict[str, List[Message]]:
        history = await self._get_history(pagination)
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
        posts: List[Post] = []
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
            media = next(
                (
                    msg
                    for msg in group
                    if msg.__class__.__name__ == "Message" and msg.media
                ),
                None,
            )

            if info:
                post = Post.from_messages([info, media])
                posts.append(post)

        posts.sort(key=lambda x: x.message_id, reverse=True)

        if posts:
            last_post = posts[-1]
            total = len(posts)
            pagination.last_offset_id = last_post.message_id
            pagination.total = total

        return PaginatedPosts(data=posts, pagination=pagination)

    async def get_post(self, message_id: int) -> Post:
        messages = await self.client.get_messages(
            self.channel, ids=[message_id, message_id + 1]
        )

        posts = sorted(messages, key=lambda x: x.id)
        post = Post.from_messages(posts)

        return post

    async def get_image(self, message_id: int):
        messages = await self.client.get_messages(self.channel, ids=[message_id])
        info = next(
            (
                msg
                for msg in messages
                if msg.__class__.__name__ == "Message" and msg.message
            ),
            None,
        )

        image = await self.client.download_file(info.media.photo)
        return image

    async def get_video(self, message_id: int, document_id: int, start: int, end: int):
        document = cache.get(document_id)
        if not document:
            messages = await self.client.get_messages(self.channel, ids=[message_id])
            media = next(
                (
                    msg
                    for msg in messages
                    if msg.__class__.__name__ == "Message" and msg.media
                ),
                None,
            )
            document = media.media.document
            cache.set(document_id, document)

        async for chunk in self.client.iter_download(
            document,
            offset=start,
            limit=end - start + 1,
            chunk_size=1024 * 1024,
            stride=1024 * 1024,
            dc_id=document.dc_id,
            file_size=document.size,
        ):
            yield chunk
