"""Domain entity representing a Risk Theme with taxonomy metadata. Framework-free.

Implements: RiskTheme(id: int, name: str, nfr_taxonomy_id: int, nfr_taxonomy: str, cluster: str)
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RiskTheme:
    """Risk Theme with taxonomy metadata"""
    id: int
    name: str
    taxonomy_id: int
    taxonomy: str
    cluster: str
    cluster_id: int
