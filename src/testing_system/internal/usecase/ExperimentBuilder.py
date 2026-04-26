from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from testing_system.internal.adapter.registries.memory import InMemoryRegistry
from testing_system.internal.domain.entities import Experiment, ExperimentConfig, Question
from testing_system.internal.domain.interfaces import IAssistant, IRegistry, IRetriever
from testing_system.internal.domain.value_objects import (
    AdapterConfig,
    RetrievedDocument,
)
from testing_system.internal.usecase.Runner import Runner


@dataclass
class ExperimentBuild:
    """Ready-to-run experiment pipeline assembled from config."""
    experiment: Experiment
    runner: Runner


class ExperimentBuilder:
    """Builds runtime objects from declarative ExperimentConfig."""

    def build(self, config: ExperimentConfig) -> ExperimentBuild:
        assistant = self._build_assistant(config.assistant)
        retriever = self._build_retriever(config.retriever)
        registry = self._build_registry()
        top_k = int(config.retriever.params.get("top_k", 3))

        experiment = Experiment(
            id=config.id,
            name=config.name,
            config=config,
            questions=self._questions_with_metadata(config),
            answers=[],
            metrics=[],
        )
        runner = Runner(
            registry=registry,
            assistant=assistant,
            retriever=retriever,
            top_k=top_k,
        )
        return ExperimentBuild(experiment=experiment, runner=runner)

    def _build_assistant(self, config: AdapterConfig) -> IAssistant:
        params = self._runtime_params(config.params)

        if config.name == "mock":
            from testing_system.internal.adapter.assistants.mock import MockAssistant

            return MockAssistant(**params)
        if config.name == "ollama":
            from testing_system.internal.adapter.assistants.ollama import OllamaAssistant

            return OllamaAssistant(**params)

        raise ValueError(f"Unsupported assistant adapter: '{config.name}'")

    def _build_retriever(self, config: AdapterConfig) -> IRetriever:
        if config.name == "mock":
            from testing_system.internal.adapter.retrievers.mock import MockRetriever

            documents = self._documents(config.params.get("documents", []))
            return MockRetriever(documents=documents)

        raise ValueError(f"Unsupported retriever adapter: '{config.name}'")

    def _build_registry(self) -> IRegistry:
        return InMemoryRegistry()

    def _questions_with_metadata(
        self,
        config: ExperimentConfig,
    ) -> List[Question]:
        questions = []
        temperature = self._temperature(config.assistant.params)

        for question in config.questions:
            metadata = deepcopy(question.metadata or {})
            metadata["system_prompt"] = config.prompt.text
            metadata["temperature"] = temperature

            questions.append(
                Question(
                    id=question.id,
                    text=question.text,
                    retrieved_context_id=question.retrieved_context_id,
                    metadata=metadata,
                )
            )

        return questions

    def _documents(self, raw_documents: List[Dict[str, Any]]) -> List[RetrievedDocument]:
        return [
            RetrievedDocument(
                id=str(doc["id"]),
                content=doc["content"],
                metadata=doc.get("metadata"),
            )
            for doc in raw_documents
        ]

    def _runtime_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            key: value
            for key, value in params.items()
            if key not in {"temperature", "generation"}
        }

    def _temperature(self, params: Dict[str, Any]) -> Optional[float]:
        if "temperature" in params:
            return params["temperature"]

        generation = params.get("generation") or {}
        return generation.get("temperature")
