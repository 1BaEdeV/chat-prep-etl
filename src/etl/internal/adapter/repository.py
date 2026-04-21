import asyncio
import uuid
from typing import List
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from dataclasses import asdict
from fastembed import TextEmbedding

from src.etl.internal.domain.interfaces import IRepository
from src.etl.internal.domain.value_objects import MessageMetadata


class QdrantFastEmbedRepository(IRepository):
    """
    Репозиторий для работы с векторной базой данных Qdrant с использованием FastEmbed.

    Обеспечивает асинхронное сохранение и семантический поиск сообщений
    с поддержкой мультиязычности (RU/EN).
    """

    def __init__(self, url: str, api_key: str, collection_name: str):
        """
        Инициализирует клиент Qdrant и загружает модель эмбеддингов.

        Args:
            url (str): URL адрес сервера Qdrant.
            api_key (str): Ключ доступа к API.
            collection_name (str): Название коллекции для хранения сообщений.
        """
        self._client = AsyncQdrantClient(url=url, api_key=api_key)
        self._collection_name = collection_name
        self._model = TextEmbedding(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

    async def save_batch(self, messages: List[MessageMetadata]) -> None:
        """
        Пакетное сохранение сообщений в базу данных.

        Args:
            messages (List[MessageMetadata]): Список объектов метаданных сообщений.

        Raises:
            Exception: В случае ошибки при векторизации или сетевом запросе к Qdrant.
        """
        try:
            texts = [m.text if m.text else "" for m in messages]
            embeddings = await asyncio.to_thread(lambda: list(self._model.embed(texts)))

            points = [
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector.tolist(),
                    payload=asdict(msg)
                )
                for vector, msg in zip(embeddings, messages)
            ]

            self._client.upload_points(
                collection_name=self._collection_name,
                points=points,
                wait=True
            )
        except Exception as e:
            raise

    async def search_similar(self, query_text: str, chat_id: int, k: int) -> List[
        MessageMetadata]:
        """
        Выполняет семантический поиск похожих сообщений в рамках конкретного чата.

        Args:
            query_text (str): Текстовый запрос для поиска (на любом языке).
            chat_id (int): Идентификатор чата для фильтрации результатов.
            k (int): Максимальное количество возвращаемых результатов.

        Returns:
            List[MessageMetadata]: Список найденных сообщений.

        Raises:
            Exception: При ошибках векторизации запроса или поиска в базе.
        """
        try:
            embeddings = await asyncio.to_thread(
                lambda: list(self._model.embed([query_text])))
            query_vector = embeddings[0].tolist()

            response = await self._client.query_points(
                collection_name=self._collection_name,
                query=query_vector,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="chat_id",
                            match=models.MatchValue(value=chat_id)
                        )
                    ]
                ),
                limit=k,
                with_payload=True
            )

            return [MessageMetadata(**hit.payload) for hit in response.points if
                    hit.payload]
        except Exception as e:
            raise
