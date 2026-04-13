from abc import ABC, abstractmethod
from testing_system.internal.domain.value_objects import \
    AssistantRequest, AssistantResponse, \
    RetrievalResponse, RetrievalRequest


class IAssistant(ABC):
    """Interface for AI Assistant implementations"""

    @abstractmethod
    def ask(self, request: AssistantRequest) -> AssistantResponse:
        """Sends request to assistant and returns responce"""
        pass

class IRetriever(ABC):
    """Interface for any database implementation"""

    @abstractmethod
    def retrieve(self, request: RetrievalRequest) -> RetrievalResponse:
        """Sends request to db and returns response with docs"""
        pass