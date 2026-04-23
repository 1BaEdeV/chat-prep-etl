from typing import Any, List
from telethon.tl.patched import Message
from src.etl.internal.domain.interfaces import IParser
from src.etl.internal.domain.value_objects import MessageMetadata

class TelegramParser(IParser):
    def parse_message(self, event: Any) -> MessageMetadata:
        msg = event
        text = msg if isinstance(msg, str) else getattr(msg, 'message', "")
        chat_id = getattr(msg, 'chat_id', 0)
        sender_id = getattr(msg, 'sender_id', 0)
        attached_files = []
        if hasattr(msg, 'media') and msg.media:
            attached_files.append("media_detected")
        return MessageMetadata(
            chat_id=chat_id,
            sender_id=sender_id,
            text=text,
            attached_files=attached_files
        )

    def parse_batch(self, raw_events: List[Any]) -> List[MessageMetadata]:
        return [self.parse_message(e) for e in raw_events]