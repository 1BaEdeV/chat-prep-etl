from dataclasses import dataclass, field
from typing import List, Optional

@dataclass(frozen=True)
class MessageMetadata:
    """
    Метаданные сообщения для хранения в векторной базе данных.

    Attributes:
        chat_id (int): Уникальный идентификатор чата.
        sender_id (Optional[int]): Идентификатор пользователя, отправившего сообщение.
            Может быть None.
        text (Optional[str]): Текстовое содержимое сообщения.
        attached_files (List[str]): Список путей или имен файлов,
            прикрепленных к сообщению. По умолчанию пустой список.
    """

    chat_id: int
    sender_id: Optional[int]
    text: Optional[str]
    attached_files: List[str] = field(default_factory=list)
