from fastapi import APIRouter, Request, HTTPException

from core.ai.openai import get_chat_response

router = APIRouter()


@router.get(
    "/ai",
    tags=["Post"],
    operation_id="ai",

)
async def paginate(
        request: Request,
):
    try:
        chat = get_chat_response("qual o melhor filme? ")

        return {"message": chat}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
