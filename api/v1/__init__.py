from fastapi import APIRouter

from api.v1 import posts, health, ai

router = APIRouter(prefix="/v1")

router.include_router(health.router)
router.include_router(posts.router)
router.include_router(ai.router)
