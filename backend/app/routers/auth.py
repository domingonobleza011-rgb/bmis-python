from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import or_
import os, uuid

from ..database import get_db
from ..config import settings
from .. import models, schemas
from ..security import hash_password, verify_password, create_access_token
from ..deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _find_account(db: Session, identity: str):
    """Checks admin, staff, then resident tables — same precedence as the
    original index.php login (`$bmis->validate_login()`)."""
    admin = db.query(models.Admin).filter(models.Admin.email == identity).first()
    if admin:
        return "administrator", admin, admin.password, admin.id_admin, f"{admin.fname} {admin.lname}"

    staff = db.query(models.Staff).filter(
        or_(models.Staff.email == identity, models.Staff.phone_number == identity)
    ).first()
    if staff:
        role = "sk" if (staff.position or "").lower().startswith("sk") else "staff"
        return role, staff, staff.password, staff.id_user, f"{staff.fname} {staff.lname}"

    resident = db.query(models.Resident).filter(
        or_(models.Resident.email == identity, models.Resident.phone_number == identity)
    ).first()
    if resident:
        return "resident", resident, resident.password, resident.id_resident, f"{resident.fname} {resident.lname}"

    return None, None, None, None, None


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    role, account, hashed, user_id, name = _find_account(db, payload.identity)
    if not account or not verify_password(payload.password, hashed):
        raise HTTPException(401, "Invalid credentials.")
    token = create_access_token({"sub": user_id, "role": role, "name": name})
    return schemas.TokenResponse(access_token=token, role=role, name=name, user_id=user_id)


@router.post("/register")
def register_resident(
    login_identity: str = Form(...),
    password: str = Form(...),
    lname: str = Form(...),
    fname: str = Form(...),
    mi: str = Form(""),
    sex: str = Form(""),
    status: str = Form(""),
    houseno: str = Form(""),
    street: str = Form(""),
    region: str = Form(""),
    province: str = Form(""),
    brgy: str = Form(""),
    municipal: str = Form(""),
    bdate: str = Form(None),
    bplace: str = Form(""),
    nationality: str = Form(""),
    voter: str = Form("No"),
    pwd: str = Form("No"),
    family_role: str = Form("No"),
    valid_id_file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Mirrors ResidentClass::create_resident() — goes into tbl_resident_pending
    until an admin approves the uploaded valid ID."""
    existing = db.query(models.Resident).filter(
        or_(models.Resident.email == login_identity, models.Resident.phone_number == login_identity)
    ).first()
    pending_existing = db.query(models.ResidentPending).filter(
        or_(models.ResidentPending.email == login_identity, models.ResidentPending.phone_number == login_identity)
    ).first()
    if existing or pending_existing:
        raise HTTPException(409, "This email/phone is already registered or pending approval.")

    if valid_id_file.content_type not in ("image/jpeg", "image/png", "application/pdf"):
        raise HTTPException(400, "Please upload a valid government ID (JPEG, PNG, or PDF).")

    safe_name = f"pendingreg_{uuid.uuid4().hex}_{os.path.basename(valid_id_file.filename)}"
    dest_dir = os.path.join(settings.upload_dir, "valid_ids")
    os.makedirs(dest_dir, exist_ok=True)
    with open(os.path.join(dest_dir, safe_name), "wb") as f:
        f.write(valid_id_file.file.read())

    is_email = "@" in login_identity
    record = models.ResidentPending(
        email=login_identity if is_email else None,
        phone_number=None if is_email else login_identity,
        password=hash_password(password),
        lname=lname, fname=fname, mi=mi, pwd=pwd, sex=sex, status=status,
        houseno=houseno, street=street, region=region, province=province,
        brgy=brgy, municipal=municipal, bdate=bdate or None, bplace=bplace,
        nationality=nationality, voter=voter, family_role=family_role,
        valid_id_file=safe_name,
        valid_id_original_name=valid_id_file.filename,
        valid_id_file_type=valid_id_file.content_type,
        application_status="pending",
    )
    db.add(record)
    db.commit()
    return {"message": "Registration submitted. An admin will review your valid ID before you can log in."}


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return user
