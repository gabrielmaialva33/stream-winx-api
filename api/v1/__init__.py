from fastapi import APIRouter

from api.v1 import stream

router = APIRouter(prefix="/v1")
router.include_router(stream.router)
