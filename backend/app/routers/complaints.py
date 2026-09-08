from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..deps import get_current_user, require_staff_or_admin

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.post("", response_model=schemas.ComplaintOut)
def submit_complaint(payload: schemas.ComplaintIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    complaint = models.Complaint(
        id_resident=user["sub"] if user.get("role") == "resident" else None,
        **payload.model_dump(),
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@router.get("", response_model=list[schemas.ComplaintOut])
def list_complaints(status: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(models.Complaint)
    if user.get("role") == "resident":
        q = q.filter(models.Complaint.id_resident == user["sub"])
    if status:
        q = q.filter(models.Complaint.status == status)
    return q.order_by(models.Complaint.id_complaint.desc()).all()


@router.patch("/{complaint_id}/status")
def update_complaint_status(complaint_id: int, payload: schemas.StatusUpdate, db: Session = Depends(get_db), user=Depends(require_staff_or_admin)):
    c = db.query(models.Complaint).get(complaint_id)
    if not c:
        raise HTTPException(404, "Not found")
    c.status = payload.status
    db.commit()
    return {"message": "Status updated."}
