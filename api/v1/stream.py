from fastapi import APIRouter, HTTPException
from fastapi.params import Header
from fastapi.responses import StreamingResponse

from core.integrations import telegram

router = APIRouter()


@router.get("/stream")
async def stream_file(
    range_header: str | None = Header(None, alias="range"),
):
    try:
        document = await telegram.get_file_info()
        size = document.size

        if not range_header:
            return StreamingResponse(
                telegram.get_file_stream(document, 0, size - 1),
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

        stream = telegram.get_file_stream(document, start, end)
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
        raise HTTPException(status_code=500, detail=f"error while streaming: {e}")
