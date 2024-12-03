from fastapi import APIRouter

from app.api.v1 import videos, stream

router = APIRouter(prefix="/v1")
router.include_router(videos.router)
router.include_router(stream.router)
