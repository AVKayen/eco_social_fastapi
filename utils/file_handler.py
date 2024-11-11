from fastapi import UploadFile, HTTPException
from uuid import uuid4
import os

from config.settings import settings


CHUNK_SIZE = 1024 * 1024  # 1 MB

MIME_TYPES = {
    'image/jpeg': 'jpg',
    'image/png': 'png'
}


def handle_file_upload(
        uploaded_file: UploadFile, accepted_mime_types: set[str], max_size_in_mb: int = settings.max_image_size_mb
) -> str:
    max_size = max_size_in_mb * 1024 * 1024

    if uploaded_file.size > max_size:
        raise HTTPException(400, 'File too large')

    if uploaded_file.content_type not in accepted_mime_types:
        raise HTTPException(400, {'message': f'Invalid mime type: {uploaded_file.content_type}. '
                                             f'Accepted mime types are: {accepted_mime_types}'})

    uuid = uuid4()
    filename = f'{uuid}.{MIME_TYPES[uploaded_file.content_type]}'
    return filename


async def save_uploaded_file(uploaded_file: UploadFile, filename: str) -> bool:

    with open(os.path.join(settings.upload_dir, filename), 'wb') as output_file:
        while chunk := await uploaded_file.read(CHUNK_SIZE):
            output_file.write(chunk)

    return True


def delete_uploaded_file(filename: str):
    file_path = os.path.join(settings.upload_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False
