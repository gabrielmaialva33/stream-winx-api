from fastapi import APIRouter

from api.v1 import posts

router = APIRouter(prefix="/v1")

router.include_router(posts.router)
