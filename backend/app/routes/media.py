from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.dependencies import get_media_storage
from providers.media_storage import LocalMediaStorage, MediaStorageError


router = APIRouter()


@router.get("/media/{storage_key:path}")
def get_media(
    storage_key: str,
    media_storage: LocalMediaStorage = Depends(get_media_storage),
) -> FileResponse:
    try:
        media_path = media_storage.path_for_key(storage_key)
    except MediaStorageError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    if not media_path.exists():
        raise HTTPException(status_code=404, detail="Media file was not found.")

    return FileResponse(media_path, media_type="video/mp4")
