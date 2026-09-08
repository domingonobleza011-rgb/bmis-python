# BMIS Barangay San Pedro — Python/PostgreSQL rewrite

Rewrite of the original PHP/MySQL Barangay Management Information System into:
- **Backend:** Python (FastAPI) + PostgreSQL
- **Frontend:** vanilla HTML/CSS/JavaScript (static files, no build step), calling the backend as a JSON API

## Project layout

```
bmis-python/
  backend/
    app/
      main.py            entrypoint, mounts all routers, CORS, static /uploads
      config.py           settings from environment variables
      database.py         SQLAlchemy engine/session
      models.py            every table as a SQLAlchemy model
      schemas.py           Pydantic request/response models
      security.py          bcrypt hashing + JWT issue/verify
      deps.py               get_current_user + role guards (require_resident, require_staff_or_admin, require_admin, require_sk)
      crud_factory.py     generic router builder — powers all 9 certificate types from one pattern
      routers/
        auth.py             login (admin/staff/resident), resident registration + ID upload
        residents.py        resident CRUD, pending-registration approval, household/family members
        staff.py            staff & admin account management
        certificates.py     wires the 9 certificate types via crud_factory
        complaints.py
        messages.py         resident <-> admin messaging thread
        announcements.py
        youth.py            SK programs, enrollment, bulletin
        dashboard.py         summary stats
    requirements.txt
    Dockerfile
    railway.json
    .env.example
  db/
    schema.sql            PostgreSQL schema (source of truth for a fresh deploy)
  frontend/
    index.html            login
    register.html          resident registration
    css/style.css
    js/api.js               fetch wrapper + session/auth helpers used by every page
    resident/               home, services (certificate requests), complaints, messages
    admin/                  dashboard, residents, certificates, complaints, announcements, staff
    sk/                     youth program & bulletin dashboard
  render.yaml               Render.com blueprint (web service + managed Postgres)
```

## Local setup

```bash
# 1. Database
createdb bmis
psql bmis -f db/schema.sql

# 2. Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env         # edit DATABASE_URL, JWT_SECRET
uvicorn app.main:app --reload

# 3. Frontend
cd ../frontend
python -m http.server 5500   # or any static file server / VS Code Live Server
# open http://localhost:5500 — it talks to http://localhost:8000 by default
```

If your frontend and backend run on different origins/ports, set `window.API_BASE`
before `js/api.js` loads (add a small `<script>window.API_BASE="https://your-api.onrender.com";</script>`
tag above the `js/api.js` include on each page), and add that frontend origin to
`CORS_ORIGINS` in the backend `.env`.

### First admin account

There's no seed data yet — create your first administrator directly in the database:

```sql
-- password below is the bcrypt hash of "changeme123" — replace via the app once logged in
INSERT INTO tbl_admin (email, password, lname, fname)
VALUES ('admin@sanpedro.gov.ph', '$2b$12$KIX...replace-with-a-real-bcrypt-hash...', 'Cruz', 'Ana');
```
Easiest way to generate a real hash: `python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('changeme123'))"` (run inside `backend/` with the venv active).

## Deploying

**Render:** push this repo, then "New > Blueprint" and point it at `render.yaml`. It provisions
a free Postgres database and the FastAPI web service together, wires `DATABASE_URL`
automatically, and generates `JWT_SECRET`. Run `db/schema.sql` against the new database once
(Render's psql shell or any Postgres client) before first login.

**Railway:** create a Postgres plugin, then a service from `backend/` (it will pick up
`railway.json` and the `Dockerfile`). Set `DATABASE_URL` to the Postgres plugin's connection
string and `JWT_SECRET` to a random string in the service's Variables tab.

**Frontend:** since it's static files, deploy `frontend/` anywhere — Render Static Site,
Netlify, Vercel, GitHub Pages, or the same VPS via nginx. Just set `window.API_BASE` to your
backend's URL as noted above.

## What's covered

- Auth (JWT) for residents, staff, admins, and SK — checked in that precedence order, same as
  the original `index.php` login.
- Resident registration with valid-ID upload → `tbl_resident_pending` → admin approve/reject
  (mirrors the original verification flow).
- All 9 certificate/service types (Residency, Clearance, Indigency, Good Moral, Solo Parent,
  Guardianship, Livestock, Business Permit, Barangay ID) — submit, list/search, view, approve/
  release/reject, delete. Built once via `crud_factory.py` and reused per type rather than
  duplicated, since the original's `services_*.php`/`admn_*.php` pairs shared the same shape.
- Household/family member roster (add/remove members under a household head).
- Complaints (submit, list, status updates).
- Resident ↔ admin messaging thread.
- Announcements (post/list/archive) with reaction/comment endpoints.
- SK module: youth programs, enrollment, bulletin board.
- Dashboard summary stats (counts by sex, voter, PWD, household, pending items).
- Demographic filtering on the residents list (search/sex/voter/PWD/household-head) — replaces
  the ~15 separate `admn_table_*.php` filtered views with query parameters on one endpoint.

## What's not carried over yet — flagged so nothing is assumed done silently

- **Firebase Cloud Messaging push notifications** (`tbl_fcm_tokens` exists in the schema, but
  no Python code registers tokens or sends pushes yet — the original's manual JWT OAuth2 to
  Firebase needs a Python equivalent, e.g. the `firebase-admin` SDK).
- **Email notifications** (PHPMailer/Gmail SMTP in the original) — not yet ported; Python's
  stdlib `smtplib` or an SMTP-sending library would replace it, wired into password-reset and
  certificate-status-change events.
- **Password reset flow** — `tbl_password_reset_requests` table exists, but the token-generation
  + email-send + reset-confirmation endpoints aren't implemented yet.
- **Rule-based AI analytics/insights panel** — the dashboard here is raw counts only; the
  original's rule-based insights logic wasn't ported.
- **Archive/restore workflow** — `tbl_archive` table exists but no endpoints read/write it yet
  (the original's cascading-delete-into-archive logic on `admn_archive.php` needs porting).
- **Blotter, PWD registry requests, ID uploads review queue** — tables exist
  (`tbl_blotter`, `tbl_pw_requests`, `tbl_id_uploads`) but don't have routers yet; they follow
  the same pattern as `complaints.py` and can be added quickly.
- **Activity log writing** — `tbl_activity_log` table exists but nothing writes to it yet; would
  need a small helper called from each mutating endpoint (approve/reject/create/delete).
- **Data migration script** — nothing here copies your existing MySQL data into the new Postgres
  tables. Column names were kept identical to the original MySQL schema specifically to make a
  `mysqldump` → transform → `psql \copy` migration straightforward, but the script itself isn't
  written.
- **File download/printing of certificates as PDFs** — the original likely renders printable
  certificate templates; this rewrite only tracks request status, no PDF generation yet.

## Testing performed

The backend was booted and exercised end-to-end with a real test client during development
(not just written and assumed correct): login for admin/staff/resident, a resident submitting a
certificate request, an admin listing/approving it, dashboard stats, complaint submission, and
role-isolation checks (residents blocked from admin endpoints, cross-resident data access
blocked, unauthenticated requests rejected). A `passlib`/`bcrypt` version mismatch and a missing
`email-validator` dependency were caught this way and fixed in `requirements.txt`.

The frontend pages were **not** run against a live browser/backend pair in this session — worth
a manual click-through pass before you rely on them, particularly the file upload on
`register.html` and the multi-tab certificate review on `admin/certificates.html`.
