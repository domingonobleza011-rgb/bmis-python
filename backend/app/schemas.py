from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# ---------------- Auth ----------------

class LoginRequest(BaseModel):
    identity: str   # email or phone
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    name: str
    user_id: int


class ResidentRegister(BaseModel):
    login_identity: str
    password: str
    lname: str
    fname: str
    mi: Optional[str] = None
    pwd: Optional[str] = "No"
    sex: Optional[str] = None
    status: Optional[str] = None
    houseno: Optional[str] = None
    street: Optional[str] = None
    region: Optional[str] = None
    province: Optional[str] = None
    brgy: Optional[str] = None
    municipal: Optional[str] = None
    bdate: Optional[date] = None
    bplace: Optional[str] = None
    nationality: Optional[str] = None
    voter: Optional[str] = None
    family_role: Optional[str] = None


# ---------------- Residents ----------------

class ResidentOut(BaseModel):
    id_resident: int
    email: Optional[str] = None
    phone_number: Optional[str] = None
    lname: str
    fname: str
    mi: Optional[str] = None
    sex: Optional[str] = None
    status: Optional[str] = None
    houseno: Optional[str] = None
    street: Optional[str] = None
    brgy: Optional[str] = None
    municipal: Optional[str] = None
    bdate: Optional[date] = None
    pwd: Optional[str] = None
    voter: Optional[str] = None
    family_role: Optional[str] = None
    role: Optional[str] = None
    is_verified: Optional[int] = None

    class Config:
        from_attributes = True


class ResidentUpdate(BaseModel):
    fname: Optional[str] = None
    lname: Optional[str] = None
    mi: Optional[str] = None
    sex: Optional[str] = None
    status: Optional[str] = None
    houseno: Optional[str] = None
    street: Optional[str] = None
    contact: Optional[str] = None
    voter: Optional[str] = None
    pwd: Optional[str] = None


class FamilyMemberIn(BaseModel):
    lname: str
    fname: str
    mi: Optional[str] = None
    relationship: str
    bdate: Optional[date] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    occupation: Optional[str] = None


class FamilyMemberOut(FamilyMemberIn):
    id_family_member: int
    id_household: int

    class Config:
        from_attributes = True


# ---------------- Staff / Admin ----------------

class StaffCreate(BaseModel):
    login_identity: str
    password: str
    lname: str
    fname: str
    mi: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    address: Optional[str] = None
    contact: Optional[str] = None
    position: Optional[str] = None


class AdminCreate(BaseModel):
    email: EmailStr
    password: str
    lname: str
    fname: str
    mi: Optional[str] = None


# ---------------- Certificates (generic, used for all 9 types) ----------------

class CertificateIn(BaseModel):
    lname: Optional[str] = None
    fname: Optional[str] = None
    mi: Optional[str] = None
    purpose: Optional[str] = None
    houseno: Optional[str] = None
    street: Optional[str] = None
    brgy: Optional[str] = None
    municipal: Optional[str] = None
    # extra fields depending on certificate type are accepted as-is
    extra: Optional[dict] = None

    class Config:
        extra = "allow"


class StatusUpdate(BaseModel):
    status: str  # pending / approved / released / rejected
    remarks: Optional[str] = None


# ---------------- Complaints ----------------

class ComplaintIn(BaseModel):
    full_name: str
    contact_number: Optional[str] = None
    address: Optional[str] = None
    category: str
    description: str
    location: Optional[str] = None


class ComplaintOut(ComplaintIn):
    id_complaint: int
    status: str
    date_submitted: datetime

    class Config:
        from_attributes = True


# ---------------- Messages ----------------

class MessageIn(BaseModel):
    message_text: str


# ---------------- Announcements ----------------

class AnnouncementIn(BaseModel):
    event: str
    start_date: Optional[date] = None
    image: Optional[str] = None


class AnnouncementOut(AnnouncementIn):
    id_announcement: int
    addedby: Optional[str] = None
    status: str
    date_added: datetime

    class Config:
        from_attributes = True


# ---------------- Youth / SK ----------------

class YouthProgramIn(BaseModel):
    program_title: str
    program_type: Optional[str] = None
    description: Optional[str] = None
    venue: Optional[str] = None
    event_date: Optional[date] = None
    slots: Optional[int] = None
    requirements: Optional[str] = None


class YouthEnrollmentIn(BaseModel):
    id_program: int
    youth_name: str
    contact: Optional[str] = None


class YouthBulletinIn(BaseModel):
    post_title: str
    post_content: Optional[str] = None
    post_type: Optional[str] = None
    is_pinned: Optional[bool] = False
