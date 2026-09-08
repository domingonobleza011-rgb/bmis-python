from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..deps import get_current_user, require_staff_or_admin

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.post("/resident")
def send_as_resident(payload: schemas.MessageIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.get("role") != "resident":
        raise HTTPException(403, "Only residents can send this way.")
    msg = models.ResidentMessage(id_resident=user["sub"], message_text=payload.message_text)
    db.add(msg)
    db.commit()
    return {"message": "Sent."}


@router.post("/admin/{resident_id}")
def send_as_admin(resident_id: int, payload: schemas.MessageIn, db: Session = Depends(get_db), user=Depends(require_staff_or_admin)):
    msg = models.AdminMessage(id_resident=resident_id, message_text=payload.message_text, status="unread")
    db.add(msg)
    db.commit()
    return {"message": "Sent."}


@router.get("/thread/{resident_id}")
def get_thread(resident_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.get("role") == "resident" and user["sub"] != resident_id:
        raise HTTPException(403, "Access denied.")
    from_resident = db.query(models.ResidentMessage).filter(models.ResidentMessage.id_resident == resident_id).all()
    from_admin = db.query(models.AdminMessage).filter(models.AdminMessage.id_resident == resident_id).all()
    combined = (
        [{"from": "resident", "text": m.message_text, "at": m.date_sent} for m in from_resident]
        + [{"from": "admin", "text": m.message_text, "at": m.date_sent} for m in from_admin]
    )
    combined.sort(key=lambda x: x["at"])
    return combined


@router.patch("/admin/{message_id}/read")
def mark_read(message_id: int, db: Session = Depends(get_db), user=Depends(require_staff_or_admin)):
    m = db.query(models.AdminMessage).get(message_id)
    if not m:
        raise HTTPException(404, "Not found")
    m.status = "read"
    db.commit()
    return {"message": "Marked read."}
