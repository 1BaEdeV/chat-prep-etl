from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class AssistantRequest:
    """The request for Assistant interface"""
    question: str
    #context: List[RetrievedDocuments] TODO
    system_prompt: Optional[str]
    temperature: Optional[float]
    metadata: Optional[Dict[str, Any]]

@dataclass
class AssistantResponse:
    """The response from Assistant interface"""
    answer: str
    token_count: int
    latency_ms: float
    used_prompt: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]]
