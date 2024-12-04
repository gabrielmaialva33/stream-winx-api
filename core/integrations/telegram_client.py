from telethon import TelegramClient

from core import API_ID, API_HASH, STRING_SESSION, CHANNEL_ID
from core.utils import decode_session

telethon_session = decode_session(STRING_SESSION)


class TelegramClientWrapper(TelegramClient):

    def __init__(self):
        super().__init__(
            telethon_session,
            api_id=API_ID,
            api_hash=API_HASH,
            flood_sleep_threshold=240,
        )
        self.channel_id = CHANNEL_ID
