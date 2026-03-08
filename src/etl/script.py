import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / '.env') 
import json
import asyncio
from datetime import datetime
from telethon import TelegramClient
import socks




project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from config.config import SESSION_NAME, TG_API_ID, TG_API_HASH


proxy = (socks.HTTP, '123.123.123.123', 1080, True, 'my_login', 'my_password')

async def grab_chat_history():
    # Создаем клиента
    client = TelegramClient(
        SESSION_NAME, 
        int(TG_API_ID), 
        TG_API_HASH, 
        proxy=proxy)
    
    await client.start() 
    
    if not await client.is_user_authorized():
        print("Ошибка авторизации")
        return
    
    target_user = input("Введите username (@username) или телефон собеседника: ").strip()
    
    print(f"Получаем историю переписки...")
    
    messages_data = []
    message_count = 0
    
    # Получаем все сообщения с этим пользователем
    async for message in client.iter_messages(target_user, limit=None):
        message_count += 1
        
        # Базовая информация о сообщении
        msg_info = {
            'id': message.id,
            'date': message.date.isoformat() if message.date else None,
            'text': message.text or '',
            'from_me': message.out,  # True - если отправили вы, False - собеседник
        }
        
        # Если есть медиа, добавляем информацию о нем
        if message.media:
            msg_info['has_media'] = True
            msg_info['media_type'] = type(message.media).__name__
        
        messages_data.append(msg_info)
    
    # Сохраняем в JSON
    output_data = {
        'chat_with': target_user,
        'total_messages': message_count,
        'export_date': datetime.now().isoformat(),
        'messages': messages_data
    }
    
    filename = f'chat_history_{target_user.strip("@")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"Готово, файл: {filename}")
        

if __name__ == "__main__":
    asyncio.run(grab_chat_history())