import asyncio
import socks
from telethon import TelegramClient
from telethon.errors import ApiIdInvalidError, FloodWaitError

# Твои данные (уже верные)
TG_API_ID = 34395921
TG_API_HASH = 'a86566d239b6d15c97b57d48637b27be'
SESSION_NAME = 'Ediks_session'

# Твой прокси из v2rayTune (IP 127.0.0.1 и порт 12334)
# Для локального v2ray логин/пароль обычно не нужны, поэтому ставим None
proxy_config = (socks.SOCKS5, '127.0.0.1', 12334)

async def main():
    # Создаем клиента с ТВОИМ прокси
    client = TelegramClient(SESSION_NAME, TG_API_ID, TG_API_HASH, proxy=proxy_config)
    
    try:
        print("🔗 Подключение к Telegram через v2rayTune...")
        # start() сам спросит номер, код и пароль 2FA прямо в консоли
        await client.start() 
        
        me = await client.get_me()
        print(f"✅ Успешный вход! Вы вошли как: {me.first_name}")

    except ApiIdInvalidError:
        print("❌ Ошибка: API_ID или API_HASH неверны.")
    except FloodWaitError as e:
        print(f"⏳ Ошибка флуда: Нужно подождать {e.seconds} секунд.")
    except ConnectionError:
        print("❌ Ошибка: Не удалось подключиться к прокси. Проверь, запущен ли v2rayTune!")
    except Exception as e:
        print(f"⚠️ Произошла непредвиденная ошибка: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())