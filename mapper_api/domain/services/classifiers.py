"""Domain service protocols for classification orchestration."""
from __future__ import annotations
from typing import Protocol


class Classifier(Protocol):
    def classify(self, text: str) -> str:  # placeholder for domain-level service
        ...
