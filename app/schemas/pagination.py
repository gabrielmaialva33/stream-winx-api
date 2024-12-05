from datetime import datetime
from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class PaginationData:
    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Number of items per page")
    offset_id: int = Field(..., description="Offset ID")
    last_offset_id: Optional[int] = Field(None, description="Last offset ID")
    offset_date: Optional[datetime] = Field(None, description="Offset date")
    add_offset: int = Field(0, description="Add offset")
    max_id: int = Field(0, description="Max ID")
    min_id: int = Field(0, description="Min ID")

    @classmethod
    def from_parameters(cls, **kwargs) -> "PaginationData":
        return cls(
            total=kwargs.get("total", 0),
            limit=kwargs.get("limit", 50),
            offset_id=kwargs.get("offset_id", 0),
            last_offset_id=kwargs.get("last_offset_id"),
            offset_date=kwargs.get("offset_date"),
            add_offset=kwargs.get("add_offset", 0),
            max_id=kwargs.get("max_id", 0),
            min_id=kwargs.get("min_id", 0),
        )
