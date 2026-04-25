from typing import List, Optional

from testing_system.internal.domain.entities import Experiment
from testing_system.internal.domain.interfaces import IRegistry


class InMemoryRegistry(IRegistry):
    """Minimal registry implementation for local experiment runs."""

    def __init__(self):
        self._experiments = {}
    
    def push(self, experiment: Experiment) -> None:
        self._experiments[experiment.id] = experiment

    def check(self, experiment: Experiment) -> Optional[Experiment]:
        return self._experiments.get(experiment.id)

    def select(self, latest=None) -> List[Experiment]:
        experiments = list(self._experiments.values())
        if latest is None:
            return experiments
        return experiments[-latest:]
