from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..database import get_db
from .. import models, schemas
from ..deps import get_current_user, require_staff_or_admin, require_resident

router = APIRouter(prefix="/api/residents", tags=["residents"])


@router.get("", response_model=list[schemas.ResidentOut])
def list_residents(
    search: str | None = None,
    sex: str | None = None,
    voter: str | None = None,
    pwd: str | None = None,
    family_role: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(require_staff_or_admin),
):
    """Powers all the admn_table_* demographic filter views (male/female,
    voters, PWD, households, etc.) from one endpoint via query params."""
    q = db.query(models.Resident)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(models.Resident.lname.ilike(like), models.Resident.fname.ilike(like)))
    if sex:
        q = q.filter(models.Resident.sex == sex)
    if voter:
        q = q.filter(models.Resident.voter == voter)
    if pwd:
        q = q.filter(models.Resident.pwd == pwd)
    if family_role:
        q = q.filter(models.Resident.family_role == family_role)
    return q.order_by(models.Resident.lname).limit(1000).all()


@router.get("/pending")
def list_pending(db: Session = Depends(get_db), user=Depends(require_staff_or_admin)):
    rows = db.query(models.ResidentPending).filter(
        models.ResidentPending.application_status == "pending"
    ).order_by(models.ResidentPending.date_submitted.desc()).all()
    return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows]


@router.post("/pending/{pending_id}/approve")
def approve_pending(pending_id: int, db: Session = Depends(get_db), user=Depends(require_staff_or_admin)):
    p = db.query(models.ResidentPending).get(pending_id)
    if not p:
        raise HTTPException(404, "Not found")
    resident = models.Resident(
        email=p.email, phone_number=p.phone_number, password=p.password,
        lname=p.lname, fname=p.fname, mi=p.mi, pwd=p.pwd, sex=p.sex, status=p.status,
        houseno=p.houseno, street=p.street, region=p.region, province=p.province,
        brgy=p.brgy, municipal=p.municipal, bdate=p.bdate, bplace=p.bplace,
        nationality=p.nationality, voter=p.voter, family_role=p.family_role,
        role=p.role, addedby=p.addedby, is_verified=1, verified_by=user["name"],
        valid_id_file=p.valid_id_file,
    )
    db.add(resident)
    p.application_status = "approved"
    db.commit()
    return {"message": "Resident approved."}


@router.post("/pending/{pending_id}/reject")
def reject_pending(pending_id: int, db: Session = Depends(get_db), user=Depends(require_staff_or_admin)):
    p = db.query(models.ResidentPending).get(pending_id)
    if not p:
        raise HTTPException(404, "Not found")
    p.application_status = "rejected"
    db.commit()
    return {"message": "Application rejected."}


@router.get("/{resident_id}", response_model=schemas.ResidentOut)
def get_resident(resident_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.get("role") == "resident" and user["sub"] != resident_id:
        raise HTTPException(403, "Access denied.")
    r = db.query(models.Resident).get(resident_id)
    if not r:
        raise HTTPException(404, "Not found")
    return r


@router.patch("/{resident_id}", response_model=schemas.ResidentOut)
def update_resident(
    resident_id: int, payload: schemas.ResidentUpdate,
    db: Session = Depends(get_db), user=Depends(get_current_user),
):
    if user.get("role") == "resident" and user["sub"] != resident_id:
        raise HTTPException(403, "Access denied.")
    r = db.query(models.Resident).get(resident_id)
    if not r:
        raise HTTPException(404, "Not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(r, field, value)
    db.commit()
    db.refresh(r)
    return r


# ---------------- Household / family members ----------------

@router.get("/{household_id}/family", response_model=list[schemas.FamilyMemberOut])
def list_family(household_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.get("role") == "resident" and user["sub"] != household_id:
        raise HTTPException(403, "Access denied.")
    return db.query(models.FamilyMember).filter(models.FamilyMember.id_household == household_id).all()


@router.post("/{household_id}/family", response_model=schemas.FamilyMemberOut)
def add_family_member(
    household_id: int, payload: schemas.FamilyMemberIn,
    db: Session = Depends(get_db), user=Depends(get_current_user),
):
    if user.get("role") == "resident" and user["sub"] != household_id:
        raise HTTPException(403, "Access denied.")
    member = models.FamilyMember(id_household=household_id, **payload.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.delete("/family/{member_id}")
def delete_family_member(member_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    m = db.query(models.FamilyMember).get(member_id)
    if not m:
        raise HTTPException(404, "Not found")
    if user.get("role") == "resident" and user["sub"] != m.id_household:
        raise HTTPException(403, "Access denied.")
    db.delete(m)
    db.commit()
    return {"deleted": True}
