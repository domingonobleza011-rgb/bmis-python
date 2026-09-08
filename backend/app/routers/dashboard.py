from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from .. import models
from ..deps import require_staff_or_admin

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(db: Session = Depends(get_db), user=Depends(require_staff_or_admin)):
    total_residents = db.query(func.count(models.Resident.id_resident)).scalar()
    male = db.query(func.count(models.Resident.id_resident)).filter(models.Resident.sex == "Male").scalar()
    female = db.query(func.count(models.Resident.id_resident)).filter(models.Resident.sex == "Female").scalar()
    voters = db.query(func.count(models.Resident.id_resident)).filter(models.Resident.voter == "Yes").scalar()
    pwd = db.query(func.count(models.Resident.id_resident)).filter(models.Resident.pwd == "Yes").scalar()
    households = db.query(func.count(models.Resident.id_resident)).filter(models.Resident.family_role == "Yes").scalar()
    pending_certs = 0
    for model in [models.Rescert, models.SoloParent, models.GoodMoral, models.Livestock,
                  models.Guardianship, models.Indigency, models.Clearance,
                  models.BusinessPermit, models.BarangayId]:
        pending_certs += db.query(func.count()).select_from(model).filter(model.status == "pending").scalar()
    pending_complaints = db.query(func.count(models.Complaint.id_complaint)).filter(
        models.Complaint.status == "pending"
    ).scalar()
    pending_registrations = db.query(func.count(models.ResidentPending.id_resident_pending)).filter(
        models.ResidentPending.application_status == "pending"
    ).scalar()

    return {
        "total_residents": total_residents,
        "male": male,
        "female": female,
        "voters": voters,
        "pwd": pwd,
        "households": households,
        "pending_certificates": pending_certs,
        "pending_complaints": pending_complaints,
        "pending_registrations": pending_registrations,
    }
