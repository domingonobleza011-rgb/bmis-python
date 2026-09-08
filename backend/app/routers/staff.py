from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..security import hash_password
from ..deps import require_admin, require_staff_or_admin

router = APIRouter(prefix="/api/staff", tags=["staff"])


@router.get("")
def list_staff(db: Session = Depends(get_db), user=Depends(require_staff_or_admin)):
    rows = db.query(models.Staff).order_by(models.Staff.lname).all()
    return [{c.name: getattr(r, c.name) for c in r.__table__.columns if c.name != "password"} for r in rows]


@router.post("")
def create_staff(payload: schemas.StaffCreate, db: Session = Depends(get_db), user=Depends(require_admin)):
    existing = db.query(models.Staff).filter(models.Staff.email == payload.login_identity).first()
    if existing:
        raise HTTPException(409, "Staff with this identity already exists.")
    is_email = "@" in payload.login_identity
    staff = models.Staff(
        login_identity=payload.login_identity,
        email=payload.login_identity if is_email else None,
        phone_number=None if is_email else payload.login_identity,
        password=hash_password(payload.password),
        lname=payload.lname, fname=payload.fname, mi=payload.mi,
        age=payload.age, sex=payload.sex, address=payload.address,
        contact=payload.contact, position=payload.position, role="user",
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return {"id_user": staff.id_user, "message": "Staff account created."}


@router.delete("/{staff_id}")
def delete_staff(staff_id: int, db: Session = Depends(get_db), user=Depends(require_admin)):
    s = db.query(models.Staff).get(staff_id)
    if not s:
        raise HTTPException(404, "Not found")
    db.delete(s)
    db.commit()
    return {"deleted": True}


@router.post("/admins")
def create_admin(payload: schemas.AdminCreate, db: Session = Depends(get_db), user=Depends(require_admin)):
    admin = models.Admin(
        email=payload.email, password=hash_password(payload.password),
        lname=payload.lname, fname=payload.fname, mi=payload.mi,
    )
    db.add(admin)
    db.commit()
    return {"id_admin": admin.id_admin, "message": "Admin account created."}
