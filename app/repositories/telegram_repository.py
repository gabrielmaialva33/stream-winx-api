from datetime import datetime
from typing import List, Dict, Any

from telethon.tl.functions.messages import GetHistoryRequest

from core import STRING_SESSION
from core.integrations import TelegramClientWrapper
from core.utils import decode_session, parse_message_content

telethon_session = decode_session(STRING_SESSION)


class TelegramRepository:
    def __init__(self):
        self.client = TelegramClientWrapper()
        self.channel_id = self.client.channel_id
        self.channel = None

    async def start_client(self):
        if not self.client.is_connected():
            await self.client.connect()
        await self.client.start()
        self.channel = await self.client.get_entity(self.channel_id)

    async def stop_client(self):
        await self.client.disconnect()

    async def get_history(self, limit: int = 100, offset_id: int = 0):
        history = await self.client(
            GetHistoryRequest(
                peer=self.channel,
                limit=limit,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                max_id=0,
                min_id=0,
                hash=self.channel.access_hash,
            )
        )

        return history.messages

    async def grouped_posts(self, limit: int = 100, offset_id: int = 0):
        history = await self.get_history(limit, offset_id)
        messages = [
            message
            for message in history
            if hasattr(message, "grouped_id") and message.grouped_id
        ]

        grouped_messages = {}
        for message in messages:
            group_id = str(message.grouped_id)
            if group_id not in grouped_messages:
                grouped_messages[group_id] = {"grouped_id": group_id, "messages": []}
            grouped_messages[group_id]["messages"].append(message)

        return grouped_messages

    async def list_messages(
        self, limit: int = 6, offset_id: int = 0
    ) -> List[Dict[str, Any]]:
        grouped_posts = await self.grouped_posts(limit, offset_id)

        posts = []
        for group in grouped_posts.values():
            reactions = []

            info = next(
                (
                    msg
                    for msg in group["messages"]
                    if msg.__class__.__name__ == "Message" and msg.message
                ),
                None,
            )

            if info:
                if hasattr(info, "reactions") and info.reactions:
                    reactions = [
                        {
                            "reaction": (
                                result.reaction.emoticon
                                if hasattr(result.reaction, "emoticon")
                                else None
                            ),
                            "count": result.count,
                        }
                        for result in info.reactions.results
                        if hasattr(result.reaction, "emoticon")
                    ]

                parsed_content = parse_message_content(info.message)

                post = {
                    "image_url": "",
                    "grouped_id": group["grouped_id"],
                    "message_id": info.id,
                    "date": (
                        info.date.isoformat()
                        if isinstance(info.date, datetime)
                        else info.date
                    ),
                    "author": info.post_author,
                    "reactions": reactions,
                    "original_content": info.message,
                    "parsed_content": parsed_content.to_dict(),
                }
                posts.append(post)

        return posts
