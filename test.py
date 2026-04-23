import json
from telethon import TelegramClient, events
import socks
import asyncio
from dotenv import load_dotenv
import os
from src.etl.internal.adapter.tg_grabber import TelegramParser

# 1. Настройки (подставь свои или возьми из .env)
load_dotenv()
api_id = int(os.getenv('TELEGRAM_API_ID'))  
api_hash = os.getenv('TELEGRAM_API_HASH')  
session_name = os.getenv('SESSION')
chat_username =  "https://t.me/Ereminh"

proxy = (socks.SOCKS5, '127.0.0.1', 10808)        

async def debug_run():
    client = TelegramClient(session_name, api_id, api_hash, proxy=proxy)
    await client.start()
    parser = TelegramParser()
    entity = await client.get_entity(chat_username)
    messages = await client.get_messages(entity, limit=3)
    
    for message in messages:
        # Проверка типа прямо здесь
        print(f"\nDEBUG: Получен тип {type(message)}")
        
        metadata = parser.parse_message(message)
        
        print("="*30)
        print(f"ID сообщения: {getattr(message, 'id', 'N/A')}")
        print(f"Parsed Chat ID: {metadata.chat_id}")
        print(f"Текст: {metadata.text[:50]}...") 
        print(f"Файлы: {metadata.attached_files}")
        print("="*30)

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(debug_run())