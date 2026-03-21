from abc import ABC, abstractmethod
from domain.value_objects import AssistantRequest, AssistantResponse


class IAssistant(ABC):
    """Interface for AI Assistant implementations"""

    @abstractmethod
    def ask(self, request: AssistantRequest) -> AssistantResponse:
        """Sends request to assistant and returns responce"""
        pass