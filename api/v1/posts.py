from io import BytesIO

from fastapi import APIRouter, HTTPException, Header, Query, Request
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse, StreamingResponse

from app.repositories import telegram_repository
from app.schemas import PaginationData, PaginatedPosts, Post

router = APIRouter()


@router.get(
    "/posts",
    tags=["Post"],
    operation_id="paginate.posts",
    response_model=PaginatedPosts,
)
async def paginate(
        request: Request, per_page: int = Query(10), offset_id: int = Query(0),
        search: str = Query(None)
):
    try:
        pagination_data = PaginationData.from_parameters(
            per_page=per_page, offset_id=offset_id, search=search
        )

        data = await telegram_repository.paginate_posts(pagination_data)

        host = request.headers["host"]
        protocol = request.url.scheme

        for post in data.data:
            image_url = f"{protocol}://{host}/api/v1/posts/images/{post.message_id}"
            video_url = f"{protocol}://{host}/api/v1/posts/stream?document_id={post.document_id}&size={post.document_size}&message_id={post.message_document_id}"

            post.image_url = image_url
            post.video_url = video_url

        json_data = jsonable_encoder(data)
        return JSONResponse(json_data)
    except Exception as e:
        print(e)
        print(e.__class__)
        print(e.with_traceback())
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/posts/images/{message_id}",
    tags=["Post"],
    operation_id="get.post.image",
    response_class=StreamingResponse,
)
async def stream_image(message_id: int):
    try:
        image_bytes = await telegram_repository.get_image(message_id)
        return StreamingResponse(BytesIO(image_bytes), media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/posts/stream",
    tags=["Post"],
    operation_id="get.post.video",
    response_class=StreamingResponse,
)
async def stream_video(
        message_id: int = Query(...),
        document_id: int = Query(...),
        size: int = Query(...),
        range_header: str | None = Header(None, alias="range"),
):
    try:
        if not range_header:
            return StreamingResponse(
                telegram_repository.get_video(message_id, document_id, 0, size - 1),
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

        stream = telegram_repository.get_video(message_id, document_id, start, end)
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


@router.get(
    "/posts/search",
    tags=["Post"],
    operation_id="search.posts",
    response_model=PaginatedPosts,
)
async def search_posts(
        request: Request, search: str = Query(None), per_page: int = Query(10), offset_id: int = Query(0)
):
    try:
        pagination_data = PaginationData.from_parameters(
            per_page=per_page, offset_id=offset_id, search=search
        )
        data = await telegram_repository.paginate_with_search(pagination_data)

        host = request.headers["host"]
        protocol = request.url.scheme

        for post in data.data:
            image_url = f"{protocol}://{host}/api/v1/posts/images/{post.message_id}"
            video_url = f"{protocol}://{host}/api/v1/posts/stream?document_id={post.document_id}&size={post.document_size}&message_id={post.message_document_id}"

            post.image_url = image_url
            post.video_url = video_url

        json_data = jsonable_encoder(data)
        return JSONResponse(json_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/posts/{message_id}", tags=["Post"], operation_id="get.post", response_model=Post
)
async def get(request: Request, message_id: int):
    try:
        data = await telegram_repository.get_post(message_id)

        host = request.headers["host"]
        protocol = request.url.scheme

        image_url = f"{protocol}://{host}/api/v1/posts/images/{data.message_id}"
        video_url = f"{protocol}://{host}/api/v1/posts/stream?document_id={data.document_id}&size={data.document_size}&message_id={data.message_document_id}"

        data.image_url = image_url
        data.video_url = video_url

        json_data = jsonable_encoder(data)
        return JSONResponse(json_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
