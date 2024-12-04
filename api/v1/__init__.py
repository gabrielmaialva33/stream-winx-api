from fastapi import APIRouter

# from api.v1 import stream
from api.v1 import movies

router = APIRouter(prefix="/v1")
# router.include_router(stream.router)
router.include_router(movies.router)
