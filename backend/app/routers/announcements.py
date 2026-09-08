from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..deps import get_current_user, require_staff_or_admin

router = APIRouter(prefix="/api/announcements", tags=["announcements"])


@router.get("", response_model=list[schemas.AnnouncementOut])
def list_announcements(db: Session = Depends(get_db)):
    return db.query(models.Announcement).filter(models.Announcement.status == "active") \
        .order_by(models.Announcement.date_added.desc()).all()


@router.post("", response_model=schemas.AnnouncementOut)
def create_announcement(payload: schemas.AnnouncementIn, db: Session = Depends(get_db), user=Depends(require_staff_or_admin)):
    a = models.Announcement(**payload.model_dump(), addedby=user["name"], status="active")
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: int, db: Session = Depends(get_db), user=Depends(require_staff_or_admin)):
    a = db.query(models.Announcement).get(announcement_id)
    if not a:
        raise HTTPException(404, "Not found")
    a.status = "archived"
    db.commit()
    return {"deleted": True}


@router.post("/{announcement_id}/react")
def react(announcement_id: int, reaction_type: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    r = models.AnnouncementReaction(announcement_id=announcement_id, user_id=user["sub"], reaction_type=reaction_type)
    db.add(r)
    db.commit()
    return {"message": "Reaction recorded."}


@router.post("/{announcement_id}/comment")
def comment(announcement_id: int, payload: schemas.MessageIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    c = models.AnnouncementComment(announcement_id=announcement_id, user_id=user["sub"], comment_text=payload.message_text)
    db.add(c)
    db.commit()
    return {"message": "Comment posted."}
