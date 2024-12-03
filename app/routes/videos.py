from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from telethon import types

from app.config import CHANNEL_ID  # Certifique-se de definir CHANNEL_ID no seu config.py
from app.telegram_client import client

router = APIRouter()


@router.get("/videos")
async def video(request: Request, document_id: int, size: int):
    range_header = request.headers.get('range', None)
    if not range_header:
        headers = {
            'Content-Type': 'video/mp4',
            'Content-Length': str(size)
        }
        stream = get_video_stream(document_id, 0, size - 1)
        return StreamingResponse(stream, headers=headers)
    else:
        positions = range_header.replace('bytes=', '').split('-')
        start = int(positions[0])
        end = int(positions[1]) if positions[1] else size - 1
        chunk_size = end - start + 1

        headers = {
            'Content-Range': f'bytes {start}-{end}/{size}',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(chunk_size),
            'Content-Type': 'video/mp4'
        }

        stream = get_video_stream(document_id, start, end)
        return StreamingResponse(stream, headers=headers, status_code=206)


async def get_video_stream(document_id: int, start: int, end: int):
    document = await get_document(document_id)
    file_size = document.size

    iterable = client.iter_download(
        file=document,
        offset=start,
        limit=end - start + 1,
        request_size=1024 * 1024,  # Tamanho do chunk de 1MB
    )

    async for chunk in iterable:
        yield chunk


async def get_document(document_id):
    messages = await client.get_messages(CHANNEL_ID, ids=document_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    message = messages[0]
    if not message.media or not isinstance(message.media, types.MessageMediaDocument):
        raise HTTPException(status_code=400, detail="A mensagem não contém um documento")
    document = message.media.document
    return document
