from pathlib import Path
from typing import Any, Dict, List

import yaml

from testing_system.internal.domain.entities import ExperimentConfig, Question
from testing_system.internal.domain.value_objects import (
    AdapterConfig,
    PromptConfig,
)


class YamlConfigLoader:
    """Loads an ExperimentConfig from a YAML file."""

    def load(self, path: str) -> ExperimentConfig:
        config_path = Path(path)
        data = self._read_yaml(config_path)

        assistant = self._adapter_config(data, "assistant")
        retriever = self._adapter_config(data, "retriever")
        prompt = self._prompt_config(data.get("prompt", {}), config_path)

        return ExperimentConfig(
            id=data["id"],
            name=data["name"],
            assistant=assistant,
            retriever=retriever,
            prompt=prompt,
            questions=self._questions(data.get("queries", [])),
            metrics=list(data.get("metrics", [])),
            metadata=data.get("metadata"),
        )

    def _read_yaml(self, path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as file:
            loaded = yaml.safe_load(file) or {}
        if not isinstance(loaded, dict):
            raise ValueError()
        return loaded

    def _adapter_config(self, data: Dict[str, Any], key: str) -> AdapterConfig:
        raw = data.get(key)
        if not isinstance(raw, dict):
            raise ValueError()

        name = raw.get("adapter") or raw.get("name")
        if not name:
            raise ValueError()

        params = raw.get("params", {})
        if not isinstance(params, dict):
            raise ValueError()

        return AdapterConfig(name=name, params=params)

    def _prompt_config(self, data: Dict[str, Any], config_path: Path) -> PromptConfig:
        if not data:
            return PromptConfig()

        text = data.get("text")
        path = data.get("path")
        if text:
            return PromptConfig(text=text, path=path)
        if not path:
            return PromptConfig()

        prompt_path = Path(path)
        if not prompt_path.exists():
            prompt_path = config_path.parent / prompt_path
        prompt_data = self._read_yaml(prompt_path)
        return PromptConfig(text=self._render_prompt(prompt_data), path=str(path))

    def _render_prompt(self, data: Dict[str, Any]) -> str:
        parts = []
        for key in ("role", "instruction", "constraints", "output_format"):
            value = data.get(key)
            if value:
                parts.append(f"{key}: {value}")

        examples = data.get("examples") or []
        if examples:
            parts.append(f"examples: {examples}")

        return "\n\n".join(parts)

    def _questions(self, raw_queries: List[Dict[str, Any]]) -> List[Question]:
        questions = []
        for raw in raw_queries:
            questions.append(
                Question(
                    id=str(raw["id"]),
                    text=raw["text"],
                    retrieved_context_id=[
                        str(item) for item in raw.get("expected_context_ids", [])
                    ],
                    metadata=raw.get("metadata") or {},
                )
            )
        return questions
