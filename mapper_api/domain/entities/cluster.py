"""Domain entity representing a Cluster. Framework-free.

Top level in the hierarchy: Cluster -> Taxonomy -> RiskTheme
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Cluster:
    """Top-level cluster grouping taxonomies and risk themes"""
    id: int
    name: str


