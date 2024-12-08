from datetime import datetime
from typing import List, Dict, Any, Optional

from pydantic.dataclasses import dataclass, Field
from telethon.tl.types import Message

from app.schemas import PaginationData
from core.cache import cache
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
    document_id: Optional[int] = Field(None, description="Document ID")
    document_size: Optional[int] = Field(None, description="Document size")
    message_document_id: Optional[int] = Field(
        None, description="Message ID of the document"
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
            document_id=None,
            document_size=None,
            message_document_id=None,
        )

    @classmethod
    def from_messages(cls, messages: List[Message]) -> "Post":
        info_message = next((msg for msg in messages if msg.message), None)
        media_message = next(
            (
                msg
                for msg in messages
                if msg.media is not None and hasattr(msg.media, "document")
            ),
            None,
        )

        parsed_content = parse_message_content(info_message.message)

        reactions = []
        if info_message.reactions:
            reactions = [
                {
                    "reaction": (
                        result.reaction.emoticon
                        if hasattr(result.reaction, "emoticon")
                        else None
                    ),
                    "count": result.count,
                }
                for result in info_message.reactions.results
                if hasattr(result.reaction, "emoticon")
            ]

        # document = media_message.media.document
        #
        # document_cache = cache.get(document.id)
        # if not document_cache:
        #     cache.set(document.id, document)

        if media_message and media_message.media and hasattr(media_message.media, "document"):
            document = media_message.media.document

            document_cache = cache.get(document.id)
            if not document_cache:
                cache.set(document.id, document)
        else:
            document = None

        return cls(
            image_url="",  # Atualize se necessário
            video_url="",  # Atualize se necessário
            grouped_id=info_message.grouped_id,
            message_id=info_message.id,
            date=(
                info_message.date.isoformat()
                if isinstance(info_message.date, datetime)
                else info_message.date
            ),
            author=info_message.post_author,
            reactions=reactions,
            original_content=info_message.message,
            parsed_content=parsed_content.to_dict(),
            document_id=media_message.media.document.id if media_message else None,
            document_size=media_message.media.document.size if media_message else None,
            message_document_id=media_message.id if media_message else None,
        )


@dataclass
class PaginatedPosts:
    data: List[Post] = Field(..., description="List of posts")
    pagination: PaginationData = Field(..., description="Pagination data")
