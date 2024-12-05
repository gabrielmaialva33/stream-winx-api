import os
import platform
from datetime import datetime

import psutil
from fastapi import APIRouter

from app.schemas import DebugInfo, HealthResponse

router = APIRouter()


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
