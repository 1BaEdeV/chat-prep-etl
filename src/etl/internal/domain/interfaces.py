from abc import ABC, abstractmethod
from typing import List, Any

from src.etl.internal.domain.value_objects import MessageMetadata


class IRepository(ABC):
    """
    Интерфейс репозитория для хранения и поиска метаданных сообщений.

    Определяет методы для сохранения данных в векторном пространстве
    и выполнения семантического поиска с учетом контекста чата.
    """

    @abstractmethod
    async def save_batch(self, messages: List[MessageMetadata]) -> None:
        """
        Пакетное сохранение сообщений в хранилище.

        Args:
            messages (List[MessageMetadata]): Список объектов метаданных сообщений
                для векторизации и сохранения.
        """
        pass

    @abstractmethod
    async def search_similar(self, query_text: str, chat_id: int, k: int) -> List[
        MessageMetadata]:
        """
        Поиск наиболее релевантных сообщений по текстовому запросу.

        Args:
            query_text (str): Текст поискового запроса.
            chat_id (int): Идентификатор чата, внутри которого производится поиск.
            k (int): Количество возвращаемых наиболее похожих результатов.

        Returns:
            List[MessageMetadata]: Список найденных сообщений, отсортированных по релевантности.
        """
        pass



class IParser(ABC):
    """
    Интерфейс для преобразования сырых данных из внешних источников 
    в доменную сущность MessageMetadata.
    """

    @abstractmethod
    def parse_message(self, raw_event: Any) -> MessageMetadata:
        """
        Парсит одно входящее событие (например, NewMessage от Telethon).
        
        Args:
            raw_event: Объект сообщения из библиотеки-адаптера.
            
        Returns:
            MessageMetadata: Очищенные и структурированные данные.
        """
        pass

    @abstractmethod
    def parse_batch(self, raw_events: List[Any]) -> List[MessageMetadata]:
        """
        Пакетный парсинг списка событий (например, при докачке истории).
        """
        pass