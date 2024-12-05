from datetime import datetime

from pydantic.dataclasses import dataclass
from pydantic.fields import Field


@dataclass
class DebugInfo:
    pid: int = Field(..., description="Process ID")
    ppid: int = Field(..., description="Parent Process ID")
    sys_platform: str = Field(..., description="System platform")
    uptime: float = Field(..., description="Uptime")
    now: datetime = Field(..., description="Current datetime")


@dataclass
class HealthResponse:
    is_healthy: bool = Field(True, description="Health status")
    debug_info: DebugInfo = Field(..., description="Debug information")
