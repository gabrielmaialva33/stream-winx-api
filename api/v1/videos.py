from fastapi import APIRouter, HTTPException
from starlette.responses import JSONResponse

from app.repositories import telegram_repository

router = APIRouter()


@router.get("/videos")
async def paginate():
    try:
        posts = await telegram_repository.list_messages()
        return JSONResponse(content=posts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
