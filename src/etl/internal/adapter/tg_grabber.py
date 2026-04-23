from typing import Any, List
from src.etl.internal.domain.interfaces import IParser
from src.etl.internal.domain.value_objects import MessageMetadata
from telethon import TelegramClient

class TelegramGrabber:
    def __init__(self, client: TelegramClient, parser: IParser):
        self.client = client
        self.parser = parser

    async def grab_chat(self, chat_entity: str, limit: int = 10):
        # Убеждаемся, что клиент запущен
        if not self.client.is_connected():
            await self.client.start()

        results = []
        # Получаем сообщения
        async for message in self.client.iter_messages(chat_entity, limit=limit):
            # Передаем client в парсер, если нужно качать медиа
            metadata = await self.parser.parse_message(message)
            results.append(metadata)
        
        return results


class TelegramParser(IParser):
    def __init__(self, client: TelegramClient):
        self.client = client

    async def parse_message(self, event: Any) -> MessageMetadata:
        msg = event
        text = msg if isinstance(msg, str) else getattr(msg, 'message', "")
        chat_id = getattr(msg, 'chat_id', 0)
        sender_id = getattr(msg, 'sender_id', 0)
        attached_files = []
        if hasattr(msg, 'media') and msg.media:
            file_path = f"media/{chat_id}/{msg.id}"
            path = await self.client.download_media(msg, file=file_path)
            attached_files.append(path)
        return MessageMetadata(
            chat_id=chat_id,
            sender_id=sender_id,
            text=text,
            attached_files=attached_files
        )

    async def parse_batch(self, raw_events: List[Any]) -> List[MessageMetadata]:
        return [await self.parse_message(e) for e in raw_events]