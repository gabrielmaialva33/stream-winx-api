import os
import platform
from datetime import datetime

import psutil
from fastapi import APIRouter
from pydantic.dataclasses import dataclass, Field

router = APIRouter()


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


@router.get("/health")
async def health_check():
    now = datetime.now()
    pid = os.getpid()
    ppid = os.getppid()
    sys_platform = platform.system().lower()
    uptime = psutil.boot_time()

    debug_info = DebugInfo(
        pid=pid, ppid=ppid, sys_platform=sys_platform, uptime=uptime, now=now
    )

    return HealthResponse(debug_info=debug_info, is_healthy=True)
