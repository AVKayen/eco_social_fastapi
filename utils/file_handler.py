from fastapi import UploadFile, HTTPException
from uuid import UUID, uuid4
import os


UPLOAD_DIR = os.getenv('UPLOAD_DIR')
if not UPLOAD_DIR:
    raise Exception('No upload directory specified in the env variables')
os.makedirs(UPLOAD_DIR, exist_ok=True)

CHUNK_SIZE = 1024 * 1024  # 1 MB

MIME_TYPES = {
    'image/jpeg': 'jpg'
}


async def handle_file_upload(uploaded_file: UploadFile, accepted_mime_types: set[str], max_size_in_mb: int) -> UUID:
    max_size = max_size_in_mb * 1024 * 1024
    if uploaded_file.content_type not in accepted_mime_types:
        raise HTTPException(400, {'message': f'Invalid mime type. Accepted mime types are: {accepted_mime_types}'})

    uuid = uuid4()
    filename = f'{uuid}.{MIME_TYPES[uploaded_file.content_type]}'

    file_size = 0
    with open(os.path.join(UPLOAD_DIR, filename), 'wb') as output_file:
        while chunk := await uploaded_file.read(CHUNK_SIZE):
            file_size += len(chunk)

            if file_size > max_size:
                output_file.close()
                os.remove(os.path.join(UPLOAD_DIR, filename))
                raise HTTPException(400, 'File too large')

            output_file.write(chunk)

    return uuid






