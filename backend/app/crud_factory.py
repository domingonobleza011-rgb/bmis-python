"""
The original app has 9 certificate types, each with its own resident-facing
request page (services_*.php) and its own admin review page (admn_*.php) —
~18 files that do the same four things: create, list/search, view one,
update status. Rather than hand-copy that duplication into 9 nearly
identical Python files, this factory builds one working router per
certificate type from its SQLAlchemy model. Behavior is identical across
all of them; only the table/columns differ.
"""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from .database import get_db
from .deps import require_resident, require_staff_or_admin, get_current_user


def build_certificate_router(prefix: str, model, tag: str) -> APIRouter:
    router = APIRouter(prefix=f"/api/certificates/{prefix}", tags=[tag])
    pk_col = list(model.__table__.primary_key.columns)[0]
    pk_name = pk_col.name

    @router.post("")
    def submit_request(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
        """Resident submits a new certificate/service request."""
        if user.get("role") != "resident":
            raise HTTPException(403, "Only residents can submit this request.")
        allowed_cols = {c.name for c in model.__table__.columns}
        data = {k: v for k, v in payload.items() if k in allowed_cols}
        data["id_resident"] = user["sub"]
        data.setdefault("status", "pending")
        if "date" in allowed_cols and not data.get("date"):
            data["date"] = date.today()
        record = model(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return _row_to_dict(record)

    @router.get("")
    def list_requests(
        status: str | None = None,
        search: str | None = Query(None, description="matches lname/fname"),
        db: Session = Depends(get_db),
        user=Depends(get_current_user),
    ):
        """Staff/admin: list & search all requests. Resident: only their own."""
        q = db.query(model)
        if user.get("role") == "resident":
            q = q.filter(model.id_resident == user["sub"])
        if status:
            q = q.filter(model.status == status)
        if search and hasattr(model, "lname"):
            like = f"%{search}%"
            q = q.filter(or_(model.lname.ilike(like), model.fname.ilike(like)))
        rows = q.order_by(pk_col.desc()).limit(500).all()
        return [_row_to_dict(r) for r in rows]

    @router.get("/{record_id}")
    def get_one(record_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
        record = db.query(model).get(record_id)
        if not record:
            raise HTTPException(404, "Not found")
        if user.get("role") == "resident" and record.id_resident != user["sub"]:
            raise HTTPException(403, "Access denied.")
        return _row_to_dict(record)

    @router.patch("/{record_id}/status")
    def update_status(
        record_id: int,
        payload: dict,
        db: Session = Depends(get_db),
        user=Depends(require_staff_or_admin),
    ):
        """Staff/admin approves, rejects, or marks a request released."""
        record = db.query(model).get(record_id)
        if not record:
            raise HTTPException(404, "Not found")
        record.status = payload.get("status", record.status)
        if "remarks" in payload and hasattr(record, "remarks"):
            record.remarks = payload["remarks"]
        db.commit()
        db.refresh(record)
        return _row_to_dict(record)

    @router.delete("/{record_id}")
    def delete_record(record_id: int, db: Session = Depends(get_db), user=Depends(require_staff_or_admin)):
        record = db.query(model).get(record_id)
        if not record:
            raise HTTPException(404, "Not found")
        db.delete(record)
        db.commit()
        return {"deleted": True}

    return router


def _row_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}
