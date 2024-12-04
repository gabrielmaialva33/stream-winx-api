from fastapi import APIRouter, HTTPException
from starlette.responses import JSONResponse

from app.repositories import telegram_repository

router = APIRouter()


@router.get("/videos")
async def paginate(limit: int = 10, offset_id: int = 0):
    try:
        data = await telegram_repository.paginate_posts(limit, offset_id)
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
