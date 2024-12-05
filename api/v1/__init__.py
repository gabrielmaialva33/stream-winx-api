from fastapi import APIRouter

from api.v1 import posts, health

router = APIRouter(prefix="/v1")

router.include_router(health.router)
router.include_router(posts.router)
