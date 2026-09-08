from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..deps import get_current_user, require_sk

router = APIRouter(prefix="/api/youth", tags=["youth"])


@router.get("/programs")
def list_programs(db: Session = Depends(get_db)):
    return db.query(models.YouthProgram).order_by(models.YouthProgram.event_date).all()


@router.post("/programs")
def create_program(payload: schemas.YouthProgramIn, db: Session = Depends(get_db), user=Depends(require_sk)):
    p = models.YouthProgram(**payload.model_dump(), created_by=user["name"])
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.post("/enroll")
def enroll(payload: schemas.YouthEnrollmentIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    e = models.YouthEnrollment(**payload.model_dump())
    db.add(e)
    db.commit()
    return {"message": "Enrolled."}


@router.get("/enrollments/{program_id}")
def list_enrollments(program_id: int, db: Session = Depends(get_db), user=Depends(require_sk)):
    return db.query(models.YouthEnrollment).filter(models.YouthEnrollment.id_program == program_id).all()


@router.get("/bulletin")
def list_bulletin(db: Session = Depends(get_db)):
    return db.query(models.YouthBulletin).order_by(
        models.YouthBulletin.is_pinned.desc(), models.YouthBulletin.date_posted.desc()
    ).all()


@router.post("/bulletin")
def post_bulletin(payload: schemas.YouthBulletinIn, db: Session = Depends(get_db), user=Depends(require_sk)):
    post = models.YouthBulletin(**payload.model_dump(), posted_by=user["name"])
    db.add(post)
    db.commit()
    return {"message": "Posted."}
