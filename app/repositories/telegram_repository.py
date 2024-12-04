from datetime import datetime
from typing import List, Dict, Any

from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import Message

from core.integrations import TelegramClientWrapper
from core.utils import parse_message_content


class TelegramRepository:
    def __init__(self):
        self.client = TelegramClientWrapper()
        self.channel_id = self.client.channel_id
        self.channel = None

    async def start_client(self):
        """
        Start the telegram client and connect to the channel
        """
        if not self.client.is_connected():
            await self.client.connect()
        await self.client.start()
        self.channel = await self.client.get_entity(self.channel_id)

    async def stop_client(self):
        """
        Stop the telegram client and disconnect from the channel
        """
        await self.client.disconnect()

    async def get_history(
            self,
            limit: int = 50,
            offset_id: int = 0,
            offset_date=None,
            add_offset=0,
            max_id=0,
            min_id=0,
    ) -> List[Message]:
        """
        Get the chat history of the channel
        """
        history = await self.client(
            GetHistoryRequest(
                peer=self.channel,
                limit=limit,
                offset_id=offset_id,
                offset_date=offset_date,
                add_offset=add_offset,
                max_id=max_id,
                min_id=min_id,
                hash=self.channel.access_hash,
            )
        )

        return history.messages

    async def grouped_posts(
            self,
            limit: int = 50,
            offset_id: int = 0,
            offset_date=None,
            add_offset=0,
            max_id=0,
            min_id=0,
    ):
        """
        Group the posts by the grouped id
        """
        history = await self.get_history(
            limit, offset_id, offset_date, add_offset, max_id, min_id
        )
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

    async def paginate_posts(
            self,
            limit: int = 50,
            offset_id: int = 0,
            offset_date=None,
            add_offset=0,
            max_id=0,
            min_id=0,
    ) -> Dict[str, Any]:
        """
        Paginate the posts of the channel
        """
        grouped_posts = await self.grouped_posts(
            limit, offset_id, offset_date, add_offset, max_id, min_id
        )

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
                posts.sort(key=lambda x: x["message_id"], reverse=True)

        data = {
            "pagination": {
                "total": len(posts),
                "limit": limit,
                "offset_id": offset_id,
                "offset_date": offset_date,
                "add_offset": add_offset,
                "max_id": max_id,
                "min_id": min_id,
            },
            "data": posts,
        }

        return data
