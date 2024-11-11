from fastapi import UploadFile, HTTPException
from uuid import uuid4
import os

from config.settings import settings


CHUNK_SIZE = 1024 * 1024  # 1 MB

MIME_TYPES = {
    'image/jpeg': 'jpg',
    'image/png': 'png'
}


async def handle_file_upload(uploaded_file: UploadFile, accepted_mime_types: set[str], max_size_in_mb: int) -> str:
    max_size = max_size_in_mb * 1024 * 1024
    if uploaded_file.content_type not in accepted_mime_types:
        raise HTTPException(400, {'message': f'Invalid mime type: {uploaded_file.content_type}. '
                                             f'Accepted mime types are: {accepted_mime_types}'})

    uuid = uuid4()
    filename = f'{uuid}.{MIME_TYPES[uploaded_file.content_type]}'

    file_size = 0
    with open(os.path.join(settings.upload_dir, filename), 'wb') as output_file:
        while chunk := await uploaded_file.read(CHUNK_SIZE):
            file_size += len(chunk)

            if file_size > max_size:
                output_file.close()
                os.remove(os.path.join(settings.upload_dir, filename))
                raise HTTPException(400, 'File too large')

            output_file.write(chunk)

    return filename


def delete_uploaded_file(filename: str):
    file_path = os.path.join(settings.upload_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False
