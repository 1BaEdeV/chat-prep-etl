import asyncio
import time
from qdrant_client import QdrantClient
from qdrant_client.http import models

from src.etl.dbconfig import url, api_key, collection_name, test_collection_name
from src.etl.internal.adapter.repository import QdrantFastEmbedRepository
from src.etl.internal.domain.value_objects import MessageMetadata


async def test():
    URL = url
    API_KEY = api_key
    COLLECTION_NAME = test_collection_name

    client = QdrantClient(url=URL, api_key=API_KEY)

    if client.collection_exists(collection_name=COLLECTION_NAME):
        client.delete_collection(collection_name=COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=384,
            distance=models.Distance.COSINE
        ),
        on_disk_payload=True
    )
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="chat_id",
        field_schema=models.PayloadSchemaType.INTEGER,
    )

    repo = QdrantFastEmbedRepository(URL, API_KEY, COLLECTION_NAME)

    extra_messages = [
        # Чат 101 - Техническая поддержка (RU/EN)
        MessageMetadata(sender_id=1, chat_id=101,
                        text="Как сбросить пароль от учетной записи?", attached_files=[]),
        MessageMetadata(sender_id=2, chat_id=101, text="The server is down since 2 AM",
                        attached_files=["logs.txt"]),
        MessageMetadata(sender_id=1, chat_id=101, text="Где найти документацию по API?",
                        attached_files=[]),
        MessageMetadata(sender_id=3, chat_id=101, text="I need help with my subscription",
                        attached_files=[]),
        MessageMetadata(sender_id=2, chat_id=101,
                        text="Ошибка 404 при входе в личный кабинет", attached_files=[]),
        MessageMetadata(sender_id=1, chat_id=101, text="Is there a Python SDK available?",
                        attached_files=[]),
        MessageMetadata(sender_id=4, chat_id=101,
                        text="Плановое обслуживание начнется в полночь",
                        attached_files=[]),
        MessageMetadata(sender_id=2, chat_id=101, text="Can you increase my storage limit?",
                        attached_files=[]),
        MessageMetadata(sender_id=1, chat_id=101, text="Спасибо, проблема решена!",
                        attached_files=[]),
        MessageMetadata(sender_id=3, chat_id=101,
                        text="How to enable two-factor authentication?",
                        attached_files=[]),

        # Чат 505 - Обсуждение проекта (RU/EN)
        MessageMetadata(sender_id=10, chat_id=505,
                        text="Нужно обновить дизайн главной страницы",
                        attached_files=["design.fig"]),
        MessageMetadata(sender_id=11, chat_id=505,
                        text="Meeting scheduled for tomorrow at 10 AM",
                        attached_files=[]),
        MessageMetadata(sender_id=10, chat_id=505, text="Согласовали бюджет на маркетинг",
                        attached_files=[]),
        MessageMetadata(sender_id=12, chat_id=505,
                        text="Who is responsible for the database?", attached_files=[]),
        MessageMetadata(sender_id=11, chat_id=505, text="Подготовил отчет за прошлый месяц",
                        attached_files=["report.pdf"]),
        MessageMetadata(sender_id=10, chat_id=505, text="Let's use React for the frontend",
                        attached_files=[]),
        MessageMetadata(sender_id=12, chat_id=505,
                        text="Нам нужен новый тестировщик в команду", attached_files=[]),
        MessageMetadata(sender_id=11, chat_id=505, text="I will finish the task by Friday",
                        attached_files=[]),
        MessageMetadata(sender_id=10, chat_id=505,
                        text="Добавил новые иконки в репозиторий", attached_files=[]),
        MessageMetadata(sender_id=12, chat_id=505,
                        text="Does anyone have the link to the dev server?",
                        attached_files=[])
    ]
    start = time.perf_counter()
    await repo.save_batch(extra_messages)
    end = time.perf_counter()
    print(f"✅ Пакет успешно загружен. Время выполнения - {end-start}")

    query = "проблемы с доступом и логином"
    print(f"🔎 Ищем: '{query}' в чате 101...")
    start = time.perf_counter()
    results = await repo.search_similar(query, chat_id=101, k=3)
    end = time.perf_counter()
    print(f"✅ Ответ получен. Время выполнения - {end - start}")

    for m in results:
        print(f" - [{m.chat_id}] {m.text}")

if __name__ == "__main__":
    asyncio.run(test())