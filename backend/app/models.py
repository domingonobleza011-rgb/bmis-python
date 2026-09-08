from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, Time, Numeric, Boolean,
    ForeignKey, SmallInteger, func, JSON
)
from sqlalchemy.orm import relationship

from .database import Base


class Resident(Base):
    __tablename__ = "tbl_resident"
    id_resident = Column(Integer, primary_key=True)
    email = Column(String(150), unique=True)
    phone_number = Column(String(30), unique=True)
    password = Column(String(255), nullable=False)
    lname = Column(String(100), nullable=False)
    fname = Column(String(100), nullable=False)
    mi = Column(String(10))
    pwd = Column(String(5), default="No")
    sex = Column(String(10))
    status = Column(String(30))
    houseno = Column(String(50))
    street = Column(String(150))
    region = Column(String(150))
    province = Column(String(150))
    brgy = Column(String(150))
    municipal = Column(String(150))
    contact = Column(String(30))
    bdate = Column(Date)
    bplace = Column(String(150))
    nationality = Column(String(80))
    voter = Column(String(5))
    family_role = Column(String(20))
    role = Column(String(30), default="resident")
    addedby = Column(String(50), default="Resident")
    is_verified = Column(SmallInteger, default=0)
    verified_at = Column(DateTime)
    verified_by = Column(String(150))
    valid_id_file = Column(String(255))
    date_added = Column(DateTime, server_default=func.now())


class ResidentPending(Base):
    __tablename__ = "tbl_resident_pending"
    id_resident_pending = Column(Integer, primary_key=True)
    email = Column(String(150))
    phone_number = Column(String(30))
    password = Column(String(255), nullable=False)
    lname = Column(String(100), nullable=False)
    fname = Column(String(100), nullable=False)
    mi = Column(String(10))
    pwd = Column(String(5), default="No")
    sex = Column(String(10))
    status = Column(String(30))
    houseno = Column(String(50))
    street = Column(String(150))
    region = Column(String(150))
    province = Column(String(150))
    brgy = Column(String(150))
    municipal = Column(String(150))
    contact = Column(String(30))
    bdate = Column(Date)
    bplace = Column(String(150))
    nationality = Column(String(80))
    voter = Column(String(5))
    family_role = Column(String(20))
    role = Column(String(30), default="resident")
    addedby = Column(String(50), default="Resident")
    valid_id_file = Column(String(255))
    valid_id_original_name = Column(String(255))
    valid_id_file_type = Column(String(100))
    application_status = Column(String(20), default="pending")
    date_submitted = Column(DateTime, server_default=func.now())


class FamilyMember(Base):
    __tablename__ = "tbl_family_members"
    id_family_member = Column(Integer, primary_key=True)
    id_household = Column(Integer, ForeignKey("tbl_resident.id_resident", ondelete="CASCADE"), nullable=False)
    lname = Column(String(100), nullable=False)
    fname = Column(String(100), nullable=False)
    mi = Column(String(10))
    relationship_ = Column("relationship", String(50), nullable=False)
    bdate = Column(Date)
    age = Column(Integer)
    sex = Column(String(10))
    occupation = Column(String(100))
    date_added = Column(DateTime, server_default=func.now())


class Staff(Base):
    __tablename__ = "tbl_user"
    id_user = Column(Integer, primary_key=True)
    login_identity = Column(String(150))
    email = Column(String(150), unique=True)
    phone_number = Column(String(30), unique=True)
    password = Column(String(255), nullable=False)
    lname = Column(String(100), nullable=False)
    fname = Column(String(100), nullable=False)
    mi = Column(String(10))
    age = Column(Integer)
    sex = Column(String(10))
    address = Column(String(255))
    contact = Column(String(30))
    position = Column(String(100))
    role = Column(String(30), default="user")
    addedby = Column(String(50))
    photo = Column(String(255))
    res_is_verified = Column(SmallInteger, default=0)
    res_verified_at = Column(DateTime)
    res_verified_by = Column(String(150))
    date_added = Column(DateTime, server_default=func.now())


class Admin(Base):
    __tablename__ = "tbl_admin"
    id_admin = Column(Integer, primary_key=True)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    lname = Column(String(100), nullable=False)
    fname = Column(String(100), nullable=False)
    mi = Column(String(10))
    role = Column(String(30), default="administrator")
    date_added = Column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# Certificates — all share the same request/review shape.
# ---------------------------------------------------------------------------

class Rescert(Base):
    __tablename__ = "tbl_rescert"
    id_rescert = Column(Integer, primary_key=True)
    id_resident = Column(Integer, ForeignKey("tbl_resident.id_resident"))
    lname = Column(String(100)); fname = Column(String(100)); mi = Column(String(10))
    age = Column(Integer); nationality = Column(String(80))
    houseno = Column(String(50)); street = Column(String(150)); brgy = Column(String(150)); municipal = Column(String(150))
    date = Column(Date)
    purpose = Column(String(255)); remarks = Column(String(255))
    status = Column(String(20), default="pending")
    date_submitted = Column(DateTime, server_default=func.now())


class SoloParent(Base):
    __tablename__ = "tbl_soloparent"
    id_soloparent = Column(Integer, primary_key=True)
    id_resident = Column(Integer, ForeignKey("tbl_resident.id_resident"))
    lname = Column(String(100)); fname = Column(String(100)); mi = Column(String(10))
    civil_status = Column(String(30))
    houseno = Column(String(50)); street = Column(String(150)); brgy = Column(String(150)); municipal = Column(String(150))
    children = Column(String(255)); purpose = Column(String(255))
    date = Column(Date)
    status = Column(String(20), default="pending")
    date_submitted = Column(DateTime, server_default=func.now())


class GoodMoral(Base):
    __tablename__ = "tbl_goodmoral"
    id_goodmoral = Column(Integer, primary_key=True)
    id_resident = Column(Integer, ForeignKey("tbl_resident.id_resident"))
    lname = Column(String(100)); fname = Column(String(100)); mi = Column(String(10))
    civil_status = Column(String(30))
    houseno = Column(String(50)); street = Column(String(150)); brgy = Column(String(150)); municipal = Column(String(150))
    date = Column(Date)
    purpose = Column(String(255)); remarks = Column(String(255))
    status = Column(String(20), default="pending")
    date_submitted = Column(DateTime, server_default=func.now())


class Livestock(Base):
    __tablename__ = "tbl_livestock"
    id_livestock = Column(Integer, primary_key=True)
    id_resident = Column(Integer, ForeignKey("tbl_resident.id_resident"))
    lname = Column(String(100)); fname = Column(String(100)); mi = Column(String(10))
    civil_status = Column(String(30))
    houseno = Column(String(50)); street = Column(String(150)); brgy = Column(String(150)); municipal = Column(String(150))
    animal_type = Column(String(80)); animal_sex = Column(String(20)); age_color = Column(String(80))
    brand_marks = Column(String(150)); quantity = Column(Integer)
    date = Column(Date)
    purpose = Column(String(255)); remarks = Column(String(255))
    status = Column(String(20), default="pending")
    date_submitted = Column(DateTime, server_default=func.now())


class Guardianship(Base):
    __tablename__ = "tbl_guardianship"
    id_guardianship = Column(Integer, primary_key=True)
    id_resident = Column(Integer, ForeignKey("tbl_resident.id_resident"))
    lname = Column(String(100)); fname = Column(String(100)); mi = Column(String(10))
    civil_status = Column(String(30))
    houseno = Column(String(50)); street = Column(String(150)); brgy = Column(String(150)); municipal = Column(String(150))
    minor_name = Column(String(150)); minor_bdate = Column(Date); relationship_ = Column("relationship", String(80)); reason = Column(String(255))
    purpose = Column(String(255))
    date = Column(Date)
    status = Column(String(20), default="pending")
    date_submitted = Column(DateTime, server_default=func.now())


class Indigency(Base):
    __tablename__ = "tbl_indigency"
    id_indigency = Column(Integer, primary_key=True)
    id_resident = Column(Integer, ForeignKey("tbl_resident.id_resident"))
    lname = Column(String(100)); fname = Column(String(100)); mi = Column(String(10))
    nationality = Column(String(80))
    houseno = Column(String(50)); street = Column(String(150)); brgy = Column(String(150)); municipal = Column(String(150))
    purpose = Column(String(255))
    date = Column(Date)
    status = Column(String(20), default="pending")
    date_submitted = Column(DateTime, server_default=func.now())


class Clearance(Base):
    __tablename__ = "tbl_clearance"
    id_clearance = Column(Integer, primary_key=True)
    id_resident = Column(Integer, ForeignKey("tbl_resident.id_resident"))
    lname = Column(String(100)); fname = Column(String(100)); mi = Column(String(10))
    purpose = Column(String(255))
    houseno = Column(String(50)); street = Column(String(150)); brgy = Column(String(150)); municipal = Column(String(150))
    status = Column(String(20), default="pending")
    age = Column(Integer)
    date_submitted = Column(DateTime, server_default=func.now())


class BusinessPermit(Base):
    __tablename__ = "tbl_bspermit"
    id_bspermit = Column(Integer, primary_key=True)
    id_resident = Column(Integer, ForeignKey("tbl_resident.id_resident"))
    lname = Column(String(100)); fname = Column(String(100)); mi = Column(String(10))
    bsname = Column(String(150))
    houseno = Column(String(50)); street = Column(String(150)); brgy = Column(String(150)); municipal = Column(String(150))
    bsindustry = Column(String(150)); aoe = Column(String(150))
    status = Column(String(20), default="pending")
    date_submitted = Column(DateTime, server_default=func.now())


class BarangayId(Base):
    __tablename__ = "tbl_brgyid"
    id_brgyid = Column(Integer, primary_key=True)
    id_resident = Column(Integer, ForeignKey("tbl_resident.id_resident"))
    lname = Column(String(100)); fname = Column(String(100)); mi = Column(String(10))
    houseno = Column(String(50)); street = Column(String(150)); brgy = Column(String(150)); municipal = Column(String(150))
    bplace = Column(String(150)); bdate = Column(Date); contact = Column(String(30)); relation = Column(String(80))
    inc_lname = Column(String(100)); inc_fname = Column(String(100)); inc_mi = Column(String(10)); inc_contact = Column(String(30))
    inc_houseno = Column(String(50)); inc_street = Column(String(150)); inc_brgy = Column(String(150)); inc_municipal = Column(String(150))
    status = Column(String(20), default="pending")
    date_submitted = Column(DateTime, server_default=func.now())


class Blotter(Base):
    __tablename__ = "tbl_blotter"
    id_blotter = Column(Integer, primary_key=True)
    id_resident = Column(Integer, ForeignKey("tbl_resident.id_resident"))
    lname = Column(String(100)); fname = Column(String(100)); mi = Column(String(10))
    houseno = Column(String(50)); street = Column(String(150)); brgy = Column(String(150)); municipal = Column(String(150))
    contact = Column(String(30)); narrative = Column(Text)
    status = Column(String(20), default="pending")
    date_submitted = Column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# Complaints / messaging / notifications
# ---------------------------------------------------------------------------

class Complaint(Base):
    __tablename__ = "tbl_complaints"
    id_complaint = Column(Integer, primary_key=True)
    id_resident = Column(Integer, ForeignKey("tbl_resident.id_resident"))
    full_name = Column(String(150))
    contact_number = Column(String(30))
    address = Column(String(255))
    category = Column(String(100))
    description = Column(Text)
    location = Column(String(255))
    photo_path = Column(String(255))
    status = Column(String(20), default="pending")
    date_submitted = Column(DateTime, server_default=func.now())


class ResidentMessage(Base):
    __tablename__ = "resident_messages"
    id_message = Column(Integer, primary_key=True)
    id_resident = Column(Integer, ForeignKey("tbl_resident.id_resident"))
    message_text = Column(Text, nullable=False)
    date_sent = Column(DateTime, server_default=func.now())


class AdminMessage(Base):
    __tablename__ = "admin_messages"
    id_message = Column(Integer, primary_key=True)
    id_resident = Column(Integer, ForeignKey("tbl_resident.id_resident"))
    message_text = Column(Text, nullable=False)
    date_sent = Column(DateTime, server_default=func.now())
    status = Column(String(20), default="unread")


class FcmToken(Base):
    __tablename__ = "tbl_fcm_tokens"
    id_token = Column(Integer, primary_key=True)
    id_user = Column(Integer)
    user_role = Column(String(30))
    fcm_token = Column(String(255), nullable=False)
    date_added = Column(DateTime, server_default=func.now())


class PasswordResetRequest(Base):
    __tablename__ = "tbl_password_reset_requests"
    id_request = Column(Integer, primary_key=True)
    identity = Column(String(150), nullable=False)
    user_type = Column(String(30))
    token = Column(String(255))
    status = Column(String(20), default="pending")
    date_requested = Column(DateTime, server_default=func.now())


class IdUpload(Base):
    __tablename__ = "tbl_id_uploads"
    id_upload = Column(Integer, primary_key=True)
    id_resident = Column(Integer, ForeignKey("tbl_resident.id_resident"))
    file_name = Column(String(255))
    original_name = Column(String(255))
    file_type = Column(String(100))
    message_note = Column(String(255))
    upload_date = Column(DateTime, server_default=func.now())
    status = Column(String(20), default="pending")


# ---------------------------------------------------------------------------
# Announcements / engagement
# ---------------------------------------------------------------------------

class Announcement(Base):
    __tablename__ = "tbl_announcement"
    id_announcement = Column(Integer, primary_key=True)
    event = Column(String(255), nullable=False)
    start_date = Column(Date)
    addedby = Column(String(150))
    image = Column(String(255))
    status = Column(String(20), default="active")
    date_added = Column(DateTime, server_default=func.now())


class AnnouncementComment(Base):
    __tablename__ = "tbl_announcement_comments"
    id_comment = Column(Integer, primary_key=True)
    announcement_id = Column(Integer, ForeignKey("tbl_announcement.id_announcement"), nullable=False)
    user_id = Column(Integer, nullable=False)
    comment_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class AnnouncementReaction(Base):
    __tablename__ = "tbl_announcement_reactions"
    id_reaction = Column(Integer, primary_key=True)
    announcement_id = Column(Integer, ForeignKey("tbl_announcement.id_announcement"), nullable=False)
    user_id = Column(Integer, nullable=False)
    reaction_type = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# Youth (SK) module
# ---------------------------------------------------------------------------

class Youth(Base):
    __tablename__ = "tbl_youth"
    id_youth = Column(Integer, primary_key=True)
    id_resident = Column(Integer, ForeignKey("tbl_resident.id_resident"))
    lname = Column(String(100)); fname = Column(String(100)); mi = Column(String(10))
    bdate = Column(Date); sex = Column(String(10)); contact = Column(String(30))
    date_added = Column(DateTime, server_default=func.now())


class YouthProgram(Base):
    __tablename__ = "tbl_youth_programs"
    id_program = Column(Integer, primary_key=True)
    program_title = Column(String(200), nullable=False)
    program_type = Column(String(80))
    description = Column(Text)
    venue = Column(String(200))
    event_date = Column(Date)
    event_time = Column(Time)
    slots = Column(Integer)
    requirements = Column(Text)
    status = Column(String(20), default="open")
    created_by = Column(String(150))
    date_added = Column(DateTime, server_default=func.now())


class YouthEnrollment(Base):
    __tablename__ = "tbl_youth_enrollment"
    id_enrollment = Column(Integer, primary_key=True)
    id_program = Column(Integer, ForeignKey("tbl_youth_programs.id_program"))
    id_youth = Column(Integer)
    youth_name = Column(String(150))
    contact = Column(String(30))
    status = Column(String(20), default="enrolled")
    enrolled_at = Column(DateTime, server_default=func.now())


class YouthBulletin(Base):
    __tablename__ = "tbl_youth_bulletin"
    id_post = Column(Integer, primary_key=True)
    post_title = Column(String(200), nullable=False)
    post_content = Column(Text)
    post_type = Column(String(50))
    posted_by = Column(String(150))
    is_pinned = Column(Boolean, default=False)
    date_posted = Column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# System: audit, archive, budget
# ---------------------------------------------------------------------------

class ActivityLog(Base):
    __tablename__ = "tbl_activity_log"
    id_log = Column(Integer, primary_key=True)
    actor = Column(String(150))
    actor_role = Column(String(30))
    action = Column(String(255), nullable=False)
    details = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class Archive(Base):
    __tablename__ = "tbl_archive"
    id_archive = Column(Integer, primary_key=True)
    source_table = Column(String(100), nullable=False)
    record_type = Column(String(100))
    display_name = Column(String(255))
    original_data = Column(JSON)
    archived_by = Column(String(150))
    archived_at = Column(DateTime, server_default=func.now())


class Budget(Base):
    __tablename__ = "tbl_budget"
    id_budget = Column(Integer, primary_key=True)
    category = Column(String(150), nullable=False)
    allocated = Column(Numeric(14, 2), default=0)
    spent = Column(Numeric(14, 2), default=0)
    fiscal_year = Column(Integer)
    notes = Column(Text)
    date_added = Column(DateTime, server_default=func.now())


# Certificate tables registry used by the generic CRUD factory (routers/certificates.py)
CERTIFICATE_MODELS = {
    "residency": Rescert,
    "solo-parent": SoloParent,
    "good-moral": GoodMoral,
    "livestock": Livestock,
    "guardianship": Guardianship,
    "indigency": Indigency,
    "clearance": Clearance,
    "business-permit": BusinessPermit,
    "barangay-id": BarangayId,
}
