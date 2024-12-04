from datetime import datetime
from typing import List, Dict, Any, Optional

from pydantic.dataclasses import dataclass, Field
from telethon.tl.types import Message

from core.utils import parse_message_content


@dataclass
class Post:
    image_url: str = Field(..., description="URL of the image")
    video_url: str = Field(..., description="URL of the video")
    grouped_id: Optional[int] = Field(..., description="Grouped ID")
    message_id: int = Field(..., description="Message ID")
    date: str = Field(..., description="Date of the message")
    author: Optional[str] = Field(..., description="Author of the message")
    reactions: List[Dict[str, Any]] = Field(..., description="Reactions of the message")
    original_content: str = Field(..., description="Original content of the message")
    parsed_content: Dict[str, Any] = Field(
        ..., description="Parsed content of the message"
    )

    @classmethod
    def from_message(cls, message: Message) -> "Post":
        parsed_content = parse_message_content(message.message)

        reactions = []
        if message.reactions:
            reactions = [
                {
                    "reaction": (
                        result.reaction.emoticon
                        if hasattr(result.reaction, "emoticon")
                        else None
                    ),
                    "count": result.count,
                }
                for result in message.reactions.results
                if hasattr(result.reaction, "emoticon")
            ]

        return cls(
            image_url="",
            video_url="",
            grouped_id=message.grouped_id,
            message_id=message.id,
            date=(
                message.date.isoformat()
                if isinstance(message.date, datetime)
                else message.date
            ),
            author=message.post_author,
            reactions=reactions,
            original_content=message.message,
            parsed_content=parsed_content.to_dict(),
        )
