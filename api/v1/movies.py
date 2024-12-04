from io import BytesIO

from fastapi import APIRouter, HTTPException, Header, Query, Request
from starlette.responses import JSONResponse, StreamingResponse

from app.repositories import telegram_repository

router = APIRouter()


@router.get("/movies")
async def paginate(limit: int = 10, offset_id: int = 0):
    try:
        data = await telegram_repository.paginate_posts(limit, offset_id)
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/movies/images/{message_id}")
async def image(message_id: int):
    try:
        image_bytes = await telegram_repository.get_image(int(message_id))
        return StreamingResponse(BytesIO(image_bytes), media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/movies/stream")
async def video(document_id: int = Query(...), size: int = Query(...),
                range_header: str | None = Header(None, alias="range"), ):
    try:
        if not range_header:
            return StreamingResponse(
                telegram_repository.get_video(document_id, 0, size - 1),
                media_type="video/mp4",
                headers={
                    "Content-Type": "video/mp4",
                    "Content-Length": str(size),
                    "Accept-Ranges": "bytes",
                },
            )

        range_match = range_header.replace("bytes=", "").split("-")
        start = int(range_match[0])
        end = int(range_match[1]) if range_match[1] else size - 1
        chunk_size = end - start + 1

        stream = telegram_repository.get_video(document_id, start, end)
        return StreamingResponse(
            stream,
            media_type="video/mp4",
            status_code=206,
            headers={
                "Content-Range": f"bytes {start}-{end}/{size}",
                "Content-Length": str(chunk_size),
                "Accept-Ranges": "bytes",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/movies/{message_id}")
async def get(message_id: int, request: Request):
    try:
        data = await telegram_repository.get_post(message_id)

        host = request.client.host
        port = request.client.port
        protocol = request.url.scheme

        print(f"host: {host}")
        print(f"port: {port}")
        print(f"protocol: {protocol}")

        image_url = f"{protocol}://{host}:{port}/api/v1/movies/images/{data['message_id']}"
        video_url = f"{protocol}://{host}:{port}/api/v1/movies/stream?document_id={data['document']['id']}&size={data['document']['size']}"

        data["image_url"] = image_url
        data["video_url"] = video_url

        del data["document"]  # Remove the document from the response

        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
