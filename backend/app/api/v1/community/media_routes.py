import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app.core.dependencies import require_verified_caregiver
from app.domains.caregivers.models import Caregiver

router = APIRouter(prefix="/community/media", tags=["Community Media"])

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_community_media(
    file: UploadFile = File(...),
    caregiver: Caregiver = Depends(require_verified_caregiver),
):
    """
    Upload an image attachment for community chat.
    ENFORCED: Only verified caregivers can upload media.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image attachments are allowed.",
        )

    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    return {
        "url": f"/static/uploads/{filename}",
        "filename": filename,
        "content_type": file.content_type,
    }
