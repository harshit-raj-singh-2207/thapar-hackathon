from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_verified_caregiver
from app.domains.users.models import User
from app.domains.caregivers.models import Caregiver
from app.domains.community.models import Resource

router = APIRouter(prefix="/community/resources", tags=["Community Resources"])

class CreateResourceRequest(BaseModel):
    title: str
    description: str
    category: Optional[str] = "General"
    url: Optional[str] = None
    file_type: Optional[str] = "article"

class UpdateResourceRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    url: Optional[str] = None
    file_type: Optional[str] = None

@router.get("")
def get_resources(
    category: Optional[str] = Query(None),
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    query = db.query(Resource)
    if category and category != "All":
        query = query.filter(Resource.category.ilike(category))

    resources = query.order_by(Resource.created_at.desc()).all()
    results = []

    for r in resources:
        author_user = db.query(User).filter(User.id == r.author_id).first()
        author_cg = db.query(Caregiver).filter(Caregiver.user_id == r.author_id).first()
        results.append({
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "category": r.category,
            "url": r.url,
            "file_type": r.file_type,
            "author_id": r.author_id,
            "author_name": author_user.full_name if author_user else "Caregiver",
            "is_verified_caregiver": author_cg.is_verified if author_cg else False,
            "author": {
                "id": r.author_id,
                "name": author_user.full_name if author_user else "Caregiver",
                "is_verified": author_cg.is_verified if author_cg else False,
            },
            "is_own": r.author_id == caregiver.user_id,
            "created_at": r.created_at.isoformat(),
            "updated_at": r.updated_at.isoformat() if r.updated_at else r.created_at.isoformat(),
        })
    return results

@router.get("/{resource_id}")
def get_resource_details(
    resource_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    r = db.query(Resource).filter(Resource.id == resource_id).first()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found.")

    author_user = db.query(User).filter(User.id == r.author_id).first()
    author_cg = db.query(Caregiver).filter(Caregiver.user_id == r.author_id).first()

    return {
        "id": r.id,
        "title": r.title,
        "description": r.description,
        "category": r.category,
        "url": r.url,
        "file_type": r.file_type,
        "author_id": r.author_id,
        "author_name": author_user.full_name if author_user else "Caregiver",
        "is_verified_caregiver": author_cg.is_verified if author_cg else False,
        "author": {
            "id": r.author_id,
            "name": author_user.full_name if author_user else "Caregiver",
            "is_verified": author_cg.is_verified if author_cg else False,
        },
        "is_own": r.author_id == caregiver.user_id,
        "created_at": r.created_at.isoformat(),
        "updated_at": r.updated_at.isoformat() if r.updated_at else r.created_at.isoformat(),
    }

@router.post("", status_code=status.HTTP_201_CREATED)
def create_resource(
    req: CreateResourceRequest,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    user = db.query(User).filter(User.id == user_id).first()

    resource = Resource(
        title=req.title,
        description=req.description,
        category=req.category or "General",
        url=req.url,
        file_type=req.file_type or "article",
        author_id=user_id,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)

    return {
        "id": resource.id,
        "title": resource.title,
        "description": resource.description,
        "category": resource.category,
        "url": resource.url,
        "file_type": resource.file_type,
        "author_id": resource.author_id,
        "author_name": user.full_name if user else "Caregiver",
        "is_verified_caregiver": caregiver.is_verified,
        "author": {
            "id": resource.author_id,
            "name": user.full_name if user else "Caregiver",
            "is_verified": caregiver.is_verified,
        },
        "is_own": True,
        "created_at": resource.created_at.isoformat(),
        "updated_at": resource.created_at.isoformat(),
    }

@router.put("/{resource_id}")
def update_resource(
    resource_id: str,
    req: UpdateResourceRequest,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    r = db.query(Resource).filter(Resource.id == resource_id).first()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found.")

    if r.author_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot edit another caregiver's resource."
        )

    if req.title is not None:
        r.title = req.title
    if req.description is not None:
        r.description = req.description
    if req.category is not None:
        r.category = req.category
    if req.url is not None:
        r.url = req.url
    if req.file_type is not None:
        r.file_type = req.file_type

    db.commit()
    db.refresh(r)

    author_user = db.query(User).filter(User.id == r.author_id).first()
    return {
        "id": r.id,
        "title": r.title,
        "description": r.description,
        "category": r.category,
        "url": r.url,
        "file_type": r.file_type,
        "author_id": r.author_id,
        "author_name": author_user.full_name if author_user else "Caregiver",
        "is_verified_caregiver": caregiver.is_verified,
        "is_own": True,
        "created_at": r.created_at.isoformat(),
        "updated_at": r.updated_at.isoformat() if r.updated_at else r.created_at.isoformat(),
    }

@router.delete("/{resource_id}")
def delete_resource(
    resource_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    r = db.query(Resource).filter(Resource.id == resource_id).first()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found.")

    if r.author_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot delete another caregiver's resource."
        )

    db.delete(r)
    db.commit()
    return {"message": "Resource deleted successfully.", "resource_id": resource_id}
