"""Pydantic response DTOs matching API contracts."""
from __future__ import annotations
from typing import Literal, Annotated, List
from pydantic import BaseModel, Field
from pydantic import ConfigDict


class ResponseHeader(BaseModel):
    recordId: str


class TaxonomyItem(BaseModel):
    name: str
    id: int
    score: Annotated[float, Field(ge=0.0, le=1.0)]
    reasoning: str


class TaxonomyData(BaseModel):
    taxonomy: Annotated[List[TaxonomyItem], Field(min_length=3, max_length=3)]


class TaxonomyResponse(BaseModel):
    header: ResponseHeader
    data: TaxonomyData


FiveWName = Literal["who", "what", "when", "where", "why"]
FiveWStatus = Literal["present", "missing"]


class FiveWItem(BaseModel):
    name: FiveWName
    status: FiveWStatus
    reasoning: str


class FiveWData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    _order = ["who", "what", "when", "where", "why"]
    fivews: Annotated[List[FiveWItem], Field(min_length=5, max_length=5)] = Field(
        serialization_alias="5ws",
        validation_alias="5ws",
    )


class FiveWResponse(BaseModel):
    header: ResponseHeader
    data: FiveWData
