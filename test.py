import json
from telethon import TelegramClient
import socks
import asyncio
from dotenv import load_dotenv
import os
from src.etl.internal.adapter.tg_grabber import TelegramParser, TelegramGrabber

# 1. Настройки (подставь свои или возьми из .env)
load_dotenv()
api_id = int(os.getenv('TELEGRAM_API_ID'))  
api_hash = os.getenv('TELEGRAM_API_HASH')  
session_name = os.getenv('SESSION')
chat_username =  "https://t.me/..."

proxy = (socks.SOCKS5, '127.0.0.1', 10808)        

async def debug_run():
    client = TelegramClient(session_name, api_id, api_hash, proxy=proxy)
    parser = TelegramParser(client)
    grabber = TelegramGrabber(client, parser)

    messages = await grabber.grab_chat(chat_username, limit=10)
    
    print(f"--- Результаты парсинга ({len(messages)} шт.) ---")
    
    for metadata in messages:
        print("\n" + "="*30)
        print(f"Parsed Chat ID: {metadata.chat_id}")
        print(f"Текст: {metadata.text[:50]}...") 
        print(f"Пути к файлам: {metadata.attached_files}")
        print("="*30)

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(debug_run())