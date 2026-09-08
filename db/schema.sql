-- ============================================================================
-- BMIS Barangay San Pedro — PostgreSQL schema
-- Reconstructed from the actual INSERT/SELECT statements in the original
-- PHP (classes/main.class.php, resident.class.php, staff.class.php, and the
-- module pages). Column names are kept identical to the MySQL originals so
-- existing data can be migrated with a straight COPY/INSERT, and so nothing
-- downstream (reports, frontend, printed certs) has to change field names.
--
-- Run:  psql "$DATABASE_URL" -f schema.sql
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ---------------------------------------------------------------------------
-- People / accounts
-- ---------------------------------------------------------------------------

-- Approved residents (the "public" of the barangay)
CREATE TABLE tbl_resident (
    id_resident        SERIAL PRIMARY KEY,
    email              VARCHAR(150) UNIQUE,
    phone_number       VARCHAR(30)  UNIQUE,
    password           VARCHAR(255) NOT NULL,      -- bcrypt hash
    lname              VARCHAR(100) NOT NULL,
    fname              VARCHAR(100) NOT NULL,
    mi                 VARCHAR(10),
    pwd                VARCHAR(5)   DEFAULT 'No',  -- "person with disability" flag, kept as original Yes/No
    sex                VARCHAR(10),
    status             VARCHAR(30),                 -- civil status
    houseno            VARCHAR(50),
    street             VARCHAR(150),
    region             VARCHAR(150),
    province           VARCHAR(150),
    brgy               VARCHAR(150),
    municipal          VARCHAR(150),
    contact            VARCHAR(30),
    bdate              DATE,
    bplace             VARCHAR(150),
    nationality        VARCHAR(80),
    voter              VARCHAR(5),
    family_role        VARCHAR(20),                 -- 'Yes' = household head
    role               VARCHAR(30)  DEFAULT 'resident',
    addedby            VARCHAR(50)  DEFAULT 'Resident',
    is_verified        SMALLINT     DEFAULT 0,
    verified_at        TIMESTAMP,
    verified_by        VARCHAR(150),
    valid_id_file      VARCHAR(255),
    date_added         TIMESTAMP    DEFAULT NOW()
);

-- New resident sign-ups awaiting admin approval of their valid ID
CREATE TABLE tbl_resident_pending (
    id_resident_pending      SERIAL PRIMARY KEY,
    email                    VARCHAR(150),
    phone_number             VARCHAR(30),
    password                 VARCHAR(255) NOT NULL,
    lname                    VARCHAR(100) NOT NULL,
    fname                    VARCHAR(100) NOT NULL,
    mi                       VARCHAR(10),
    pwd                      VARCHAR(5) DEFAULT 'No',
    sex                      VARCHAR(10),
    status                   VARCHAR(30),
    houseno                  VARCHAR(50),
    street                   VARCHAR(150),
    region                   VARCHAR(150),
    province                 VARCHAR(150),
    brgy                     VARCHAR(150),
    municipal                VARCHAR(150),
    contact                  VARCHAR(30),
    bdate                    DATE,
    bplace                   VARCHAR(150),
    nationality              VARCHAR(80),
    voter                    VARCHAR(5),
    family_role              VARCHAR(20),
    role                     VARCHAR(30) DEFAULT 'resident',
    addedby                  VARCHAR(50) DEFAULT 'Resident',
    valid_id_file            VARCHAR(255),
    valid_id_original_name   VARCHAR(255),
    valid_id_file_type       VARCHAR(100),
    application_status       VARCHAR(20) DEFAULT 'pending',  -- pending/approved/rejected
    date_submitted           TIMESTAMP DEFAULT NOW()
);

-- Household roster (family members under a household-head resident)
CREATE TABLE tbl_family_members (
    id_family_member   SERIAL PRIMARY KEY,
    id_household       INTEGER NOT NULL REFERENCES tbl_resident(id_resident) ON DELETE CASCADE,
    lname              VARCHAR(100) NOT NULL,
    fname              VARCHAR(100) NOT NULL,
    mi                 VARCHAR(10),
    relationship       VARCHAR(50) NOT NULL,
    bdate              DATE,
    age                INTEGER,
    sex                VARCHAR(10),
    occupation         VARCHAR(100),
    date_added         TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_family_household ON tbl_family_members(id_household);

-- Staff (barangay employees who process requests)
CREATE TABLE tbl_user (
    id_user            SERIAL PRIMARY KEY,
    login_identity     VARCHAR(150),
    email              VARCHAR(150) UNIQUE,
    phone_number       VARCHAR(30) UNIQUE,
    password           VARCHAR(255) NOT NULL,
    lname              VARCHAR(100) NOT NULL,
    fname              VARCHAR(100) NOT NULL,
    mi                 VARCHAR(10),
    age                INTEGER,
    sex                VARCHAR(10),
    address            VARCHAR(255),
    contact            VARCHAR(30),
    position           VARCHAR(100),
    role               VARCHAR(30) DEFAULT 'user',   -- 'user' = staff
    addedby            VARCHAR(50),
    photo              VARCHAR(255),
    res_is_verified    SMALLINT DEFAULT 0,
    res_verified_at    TIMESTAMP,
    res_verified_by    VARCHAR(150),
    date_added         TIMESTAMP DEFAULT NOW()
);

-- Administrators (super-users)
CREATE TABLE tbl_admin (
    id_admin           SERIAL PRIMARY KEY,
    email              VARCHAR(150) UNIQUE NOT NULL,
    password           VARCHAR(255) NOT NULL,
    lname              VARCHAR(100) NOT NULL,
    fname              VARCHAR(100) NOT NULL,
    mi                 VARCHAR(10),
    role               VARCHAR(30) DEFAULT 'administrator',
    date_added         TIMESTAMP DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Certificates / service requests
-- Each of these mirrors one "services_*" request form + one "admn_*" review
-- queue in the original app. Shared shape: requester snapshot + purpose +
-- status + remarks, so they share one generic API pattern (see crud_factory).
-- ---------------------------------------------------------------------------

CREATE TABLE tbl_rescert (          -- Certificate of Residency
    id_rescert    SERIAL PRIMARY KEY,
    id_resident   INTEGER REFERENCES tbl_resident(id_resident),
    lname VARCHAR(100), fname VARCHAR(100), mi VARCHAR(10),
    age INTEGER, nationality VARCHAR(80),
    houseno VARCHAR(50), street VARCHAR(150), brgy VARCHAR(150), municipal VARCHAR(150),
    date DATE DEFAULT CURRENT_DATE,
    purpose VARCHAR(255), remarks VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    date_submitted TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_soloparent (        -- Solo Parent Certificate
    id_soloparent SERIAL PRIMARY KEY,
    id_resident   INTEGER REFERENCES tbl_resident(id_resident),
    lname VARCHAR(100), fname VARCHAR(100), mi VARCHAR(10),
    civil_status VARCHAR(30),
    houseno VARCHAR(50), street VARCHAR(150), brgy VARCHAR(150), municipal VARCHAR(150),
    children VARCHAR(255), purpose VARCHAR(255),
    date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'pending',
    date_submitted TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_goodmoral (         -- Certificate of Good Moral Character
    id_goodmoral  SERIAL PRIMARY KEY,
    id_resident   INTEGER REFERENCES tbl_resident(id_resident),
    lname VARCHAR(100), fname VARCHAR(100), mi VARCHAR(10),
    civil_status VARCHAR(30),
    houseno VARCHAR(50), street VARCHAR(150), brgy VARCHAR(150), municipal VARCHAR(150),
    date DATE DEFAULT CURRENT_DATE,
    purpose VARCHAR(255), remarks VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    date_submitted TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_livestock (         -- Certificate of Livestock Ownership
    id_livestock  SERIAL PRIMARY KEY,
    id_resident   INTEGER REFERENCES tbl_resident(id_resident),
    lname VARCHAR(100), fname VARCHAR(100), mi VARCHAR(10),
    civil_status VARCHAR(30),
    houseno VARCHAR(50), street VARCHAR(150), brgy VARCHAR(150), municipal VARCHAR(150),
    animal_type VARCHAR(80), animal_sex VARCHAR(20), age_color VARCHAR(80),
    brand_marks VARCHAR(150), quantity INTEGER,
    date DATE DEFAULT CURRENT_DATE,
    purpose VARCHAR(255), remarks VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    date_submitted TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_guardianship (      -- Certificate of Guardianship
    id_guardianship SERIAL PRIMARY KEY,
    id_resident     INTEGER REFERENCES tbl_resident(id_resident),
    lname VARCHAR(100), fname VARCHAR(100), mi VARCHAR(10),
    civil_status VARCHAR(30),
    houseno VARCHAR(50), street VARCHAR(150), brgy VARCHAR(150), municipal VARCHAR(150),
    minor_name VARCHAR(150), minor_bdate DATE, relationship VARCHAR(80), reason VARCHAR(255),
    purpose VARCHAR(255),
    date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'pending',
    date_submitted TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_indigency (         -- Certificate of Indigency
    id_indigency  SERIAL PRIMARY KEY,
    id_resident   INTEGER REFERENCES tbl_resident(id_resident),
    lname VARCHAR(100), fname VARCHAR(100), mi VARCHAR(10),
    nationality VARCHAR(80),
    houseno VARCHAR(50), street VARCHAR(150), brgy VARCHAR(150), municipal VARCHAR(150),
    purpose VARCHAR(255),
    date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'pending',
    date_submitted TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_clearance (         -- Barangay Clearance
    id_clearance  SERIAL PRIMARY KEY,
    id_resident   INTEGER REFERENCES tbl_resident(id_resident),
    lname VARCHAR(100), fname VARCHAR(100), mi VARCHAR(10),
    purpose VARCHAR(255),
    houseno VARCHAR(50), street VARCHAR(150), brgy VARCHAR(150), municipal VARCHAR(150),
    status VARCHAR(20) DEFAULT 'pending',
    age INTEGER,
    date_submitted TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_bspermit (          -- Business Permit
    id_bspermit   SERIAL PRIMARY KEY,
    id_resident   INTEGER REFERENCES tbl_resident(id_resident),
    lname VARCHAR(100), fname VARCHAR(100), mi VARCHAR(10),
    bsname VARCHAR(150),
    houseno VARCHAR(50), street VARCHAR(150), brgy VARCHAR(150), municipal VARCHAR(150),
    bsindustry VARCHAR(150), aoe VARCHAR(150),   -- area of exercise / operation
    status VARCHAR(20) DEFAULT 'pending',
    date_submitted TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_brgyid (            -- Barangay ID
    id_brgyid     SERIAL PRIMARY KEY,
    id_resident   INTEGER REFERENCES tbl_resident(id_resident),
    lname VARCHAR(100), fname VARCHAR(100), mi VARCHAR(10),
    houseno VARCHAR(50), street VARCHAR(150), brgy VARCHAR(150), municipal VARCHAR(150),
    bplace VARCHAR(150), bdate DATE, contact VARCHAR(30), relation VARCHAR(80),
    inc_lname VARCHAR(100), inc_fname VARCHAR(100), inc_mi VARCHAR(10), inc_contact VARCHAR(30),
    inc_houseno VARCHAR(50), inc_street VARCHAR(150), inc_brgy VARCHAR(150), inc_municipal VARCHAR(150),
    status VARCHAR(20) DEFAULT 'pending',
    date_submitted TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_blotter (           -- Blotter report
    id_blotter    SERIAL PRIMARY KEY,
    id_resident   INTEGER REFERENCES tbl_resident(id_resident),
    lname VARCHAR(100), fname VARCHAR(100), mi VARCHAR(10),
    houseno VARCHAR(50), street VARCHAR(150), brgy VARCHAR(150), municipal VARCHAR(150),
    contact VARCHAR(30), narrative TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    date_submitted TIMESTAMP DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Complaints, messaging, notifications
-- ---------------------------------------------------------------------------

CREATE TABLE tbl_complaints (
    id_complaint      SERIAL PRIMARY KEY,
    id_resident       INTEGER REFERENCES tbl_resident(id_resident),
    full_name         VARCHAR(150),
    contact_number    VARCHAR(30),
    address           VARCHAR(255),
    category          VARCHAR(100),
    description       TEXT,
    location           VARCHAR(255),
    photo_path        VARCHAR(255),
    status            VARCHAR(20) DEFAULT 'pending',
    date_submitted    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE resident_messages (      -- resident -> admin/staff
    id_message     SERIAL PRIMARY KEY,
    id_resident    INTEGER REFERENCES tbl_resident(id_resident),
    message_text   TEXT NOT NULL,
    date_sent      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE admin_messages (         -- admin/staff -> resident
    id_message     SERIAL PRIMARY KEY,
    id_resident    INTEGER REFERENCES tbl_resident(id_resident),
    message_text   TEXT NOT NULL,
    date_sent      TIMESTAMP DEFAULT NOW(),
    status         VARCHAR(20) DEFAULT 'unread'
);

CREATE TABLE tbl_fcm_tokens (
    id_token       SERIAL PRIMARY KEY,
    id_user        INTEGER,
    user_role      VARCHAR(30),
    fcm_token      VARCHAR(255) NOT NULL,
    date_added     TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_password_reset_requests (
    id_request     SERIAL PRIMARY KEY,
    identity       VARCHAR(150) NOT NULL,   -- email or phone
    user_type      VARCHAR(30),             -- resident/staff/admin
    token          VARCHAR(255),
    status         VARCHAR(20) DEFAULT 'pending',
    date_requested TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_pw_requests (         -- PWD registry assistance requests
    id_pw_request  SERIAL PRIMARY KEY,
    id_resident    INTEGER REFERENCES tbl_resident(id_resident),
    details        TEXT,
    status         VARCHAR(20) DEFAULT 'pending',
    date_submitted TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_id_uploads (
    id_upload         SERIAL PRIMARY KEY,
    id_resident       INTEGER REFERENCES tbl_resident(id_resident),
    file_name         VARCHAR(255),
    original_name     VARCHAR(255),
    file_type         VARCHAR(100),
    message_note      VARCHAR(255),
    upload_date       TIMESTAMP DEFAULT NOW(),
    status            VARCHAR(20) DEFAULT 'pending'
);

-- ---------------------------------------------------------------------------
-- Announcements / engagement
-- ---------------------------------------------------------------------------

CREATE TABLE tbl_announcement (
    id_announcement SERIAL PRIMARY KEY,
    event           VARCHAR(255) NOT NULL,
    start_date      DATE,
    addedby         VARCHAR(150),
    image           VARCHAR(255),
    status          VARCHAR(20) DEFAULT 'active',
    date_added      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_hidden_announcements (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER NOT NULL,
    announcement_id INTEGER NOT NULL REFERENCES tbl_announcement(id_announcement)
);

CREATE TABLE tbl_announcement_comments (
    id_comment       SERIAL PRIMARY KEY,
    announcement_id  INTEGER NOT NULL REFERENCES tbl_announcement(id_announcement),
    user_id          INTEGER NOT NULL,
    comment_text     TEXT NOT NULL,
    created_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_announcement_reactions (
    id_reaction      SERIAL PRIMARY KEY,
    announcement_id  INTEGER NOT NULL REFERENCES tbl_announcement(id_announcement),
    user_id          INTEGER NOT NULL,
    reaction_type    VARCHAR(20),
    created_at       TIMESTAMP DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Sangguniang Kabataan (Youth) module
-- ---------------------------------------------------------------------------

CREATE TABLE tbl_youth (
    id_youth       SERIAL PRIMARY KEY,
    id_resident    INTEGER REFERENCES tbl_resident(id_resident),
    lname VARCHAR(100), fname VARCHAR(100), mi VARCHAR(10),
    bdate DATE, sex VARCHAR(10), contact VARCHAR(30),
    date_added     TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_youth_programs (
    id_program      SERIAL PRIMARY KEY,
    program_title   VARCHAR(200) NOT NULL,
    program_type    VARCHAR(80),
    description     TEXT,
    venue           VARCHAR(200),
    event_date      DATE,
    event_time      TIME,
    slots           INTEGER,
    requirements    TEXT,
    status          VARCHAR(20) DEFAULT 'open',
    created_by      VARCHAR(150),
    date_added      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_youth_enrollment (
    id_enrollment  SERIAL PRIMARY KEY,
    id_program     INTEGER REFERENCES tbl_youth_programs(id_program),
    id_youth       INTEGER,
    youth_name     VARCHAR(150),
    contact        VARCHAR(30),
    status         VARCHAR(20) DEFAULT 'enrolled',
    enrolled_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_youth_bulletin (
    id_post        SERIAL PRIMARY KEY,
    post_title     VARCHAR(200) NOT NULL,
    post_content   TEXT,
    post_type      VARCHAR(50),
    posted_by      VARCHAR(150),
    is_pinned      BOOLEAN DEFAULT FALSE,
    date_posted    TIMESTAMP DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- System: audit, archive, budget
-- ---------------------------------------------------------------------------

CREATE TABLE tbl_activity_log (
    id_log         SERIAL PRIMARY KEY,
    actor          VARCHAR(150),
    actor_role     VARCHAR(30),
    action         VARCHAR(255) NOT NULL,
    details        TEXT,
    created_at     TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_archive (
    id_archive     SERIAL PRIMARY KEY,
    source_table   VARCHAR(100) NOT NULL,
    record_type    VARCHAR(100),
    display_name   VARCHAR(255),
    original_data  JSONB,
    archived_by    VARCHAR(150),
    archived_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tbl_budget (
    id_budget      SERIAL PRIMARY KEY,
    category       VARCHAR(150) NOT NULL,
    allocated      NUMERIC(14,2) DEFAULT 0,
    spent          NUMERIC(14,2) DEFAULT 0,
    fiscal_year    INTEGER,
    notes          TEXT,
    date_added     TIMESTAMP DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Indexes that matter for the admin search/listing screens
-- ---------------------------------------------------------------------------
CREATE INDEX idx_resident_name    ON tbl_resident(lname, fname);
CREATE INDEX idx_resident_sex     ON tbl_resident(sex);
CREATE INDEX idx_resident_pwd     ON tbl_resident(pwd);
CREATE INDEX idx_resident_voter   ON tbl_resident(voter);
CREATE INDEX idx_user_role        ON tbl_user(role);
CREATE INDEX idx_complaint_status ON tbl_complaints(status);
