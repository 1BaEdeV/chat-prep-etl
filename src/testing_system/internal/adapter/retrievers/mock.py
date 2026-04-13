from typing import List

from testing_system.internal.domain.interfaces import IRetriever
from testing_system.internal.domain.value_objects import RetrievedDocument, \
RetrievalRequest, RetrievalResponse

class MockRetriever(IRetriever):
    def __init__(self, documents : List[RetrievedDocument]):
        self._docs = documents
    
    def retrieve(self, request: RetrievalRequest) -> RetrievalResponse:
        return RetrievalResponse(
            documents=self._docs[:request.k],
            k=request.k
        )