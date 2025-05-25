import os
import pathlib
import uuid

import aiofiles
from fastapi import HTTPException

from .configs import MEDIA_DIR

async def save_image(folder_name, file) ->str:
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image type")
    folder_path = os.path.join(MEDIA_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    image_path = os.path.join("media", folder_name, filename)
    async with aiofiles.open(os.path.join(folder_path, filename) , "wb") as f:
        await f.write(await file.read())
    return image_path

async def delete_image(image_path):
    if not str(image_path).startswith("media"):
        return

    full_path = os.path.join(pathlib.Path(MEDIA_DIR).parent, image_path)


    try:
        os.remove(full_path)
    except Exception as e:
        print(f"Image {image_path} could not be deleted: {e}")
