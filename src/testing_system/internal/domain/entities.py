from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List, Any, Dict

@dataclass
class Question:
    """The question for the assistant"""
    id: str
    text: str
    retrieved_context_id: Optional[List[str]] = None # for RECALL
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Answer:
    """The assistant`s answer (text and details)"""
    id: str
    text: str
    retrieved_context: List[str] # ID of the documents used
    token_count: int
    latency_ms: float 
    metadata: Optional[Dict[str,Any]] = None

class MetricType(Enum):
    PRECISION = "precision"
    RECALL = "recall"
    HALLUCINATION_RATE = "hallucination_rate"
    TOKEN_COUNT = "token_count"
    REUSABILITY = "reusability"
    LATENCY = "latency"

@dataclass
class MetricValue:
    """The result of metric calculation"""
    type: MetricType
    value: float
    metadata: Optional[Dict[str, Any]]

@dataclass
class Experiment:
    """
    The main entity for the system - experiment
    Provides all the methods and attributes for storage and comparison
    """
    id: str
    name: str
    config: Dict[str, Any]
    questions: List[Question]
    answers: List[Answer]
    metrics: List[MetricValue]
    started_at: datetime
    finished_at: Optional[datetime] = None

    def add_answer(self, answer: Answer) -> None:
        self.answers.append(answer)
    
    def add_metric(self, metric: MetricValue) -> None:
        self.answers.append(metric)

    def is_complete(self) -> bool:
        return len(self.answers) == len(self.questions)