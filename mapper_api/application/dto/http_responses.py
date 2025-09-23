"""Pydantic response DTOs matching API contracts."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field, conlist, confloat
from pydantic import ConfigDict


class ResponseHeader(BaseModel):
    recordId: str


class TaxonomyItem(BaseModel):
    name: str
    id: int
    score: confloat(ge=0.0, le=1.0)  # type: ignore[valid-type]
    reasoning: str


class TaxonomyData(BaseModel):
    taxonomy: conlist(TaxonomyItem, min_length=3, max_length=3)  # type: ignore[valid-type]


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
    fivews: conlist(FiveWItem, min_length=5, max_length=5) = Field(  # type: ignore[valid-type]
        serialization_alias="5ws",
        validation_alias="5ws",
    )


class FiveWResponse(BaseModel):
    header: ResponseHeader
    data: FiveWData
