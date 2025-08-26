"""Pydantic request DTOs matching API contracts."""
from __future__ import annotations
from pydantic import BaseModel, Field


class CommonHeader(BaseModel):
    recordId: str = Field(...)


class CommonData(BaseModel):
    controlDescription: str = Field(...)


class CommonRequest(BaseModel):
    header: CommonHeader
    data: CommonData
