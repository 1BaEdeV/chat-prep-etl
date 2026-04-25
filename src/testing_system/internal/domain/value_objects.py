from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class AdapterConfig:
    """Declarative adapter selection and constructor parameters."""
    name: str
    params: Dict[str, Any]


@dataclass(frozen=True)
class PromptConfig:
    """Prompt source resolved from experiment configuration."""
    text: Optional[str] = None
    path: Optional[str] = None


@dataclass
class RetrievedDocument:
    """
    The document is an abstraction for the dialogue entity.
    TODO: should be multi-modal, but no idea
    """
    id: str
    content: str
    metadata: Optional[Dict[str, Any]]

@dataclass
class AssistantRequest:
    """The request for Assistant interface"""
    question: str
    retrieved_context: List[RetrievedDocument]
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
    error: Optional[str]
    metadata: Optional[Dict[str, Any]]

@dataclass
class RetrievalRequest:
    """The request for k nearest documents"""
    query: str
    k: int

@dataclass
class RetrievalResponse:
    """The response from db with abstract Reteieved Documents"""
    documents: List[RetrievedDocument]
    k: int
