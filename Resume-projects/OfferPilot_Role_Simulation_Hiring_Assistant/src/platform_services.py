import hashlib
import hmac
import json
import secrets
import smtplib
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path


DB_PATH = Path(__file__).resolve().parents[1] / "data" / "applications.db"


def utc_now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def db_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_platform_db():
    with db_connection() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin','recruiter','hiring_manager')),
                password_hash TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                analysis_json TEXT NOT NULL DEFAULT '{}',
                created_by TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                resume_text TEXT NOT NULL DEFAULT '',
                workflow_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(job_id, name),
                FOREIGN KEY(job_id) REFERENCES jobs(id)
            );
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                before_json TEXT,
                after_json TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS portal_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                token_hash TEXT UNIQUE NOT NULL,
                expires_at TEXT,
                revoked INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(candidate_id) REFERENCES candidates(id)
            );
            CREATE TABLE IF NOT EXISTS candidate_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                request_type TEXT NOT NULL,
                details TEXT,
                status TEXT NOT NULL DEFAULT 'Open',
                created_at TEXT NOT NULL,
                FOREIGN KEY(candidate_id) REFERENCES candidates(id)
            );
            CREATE TABLE IF NOT EXISTS interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                starts_at TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                timezone TEXT NOT NULL,
                meeting_url TEXT,
                notes TEXT,
                created_by TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(candidate_id) REFERENCES candidates(id)
            );
            CREATE TABLE IF NOT EXISTS communication_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                channel TEXT NOT NULL,
                recipient TEXT NOT NULL,
                subject TEXT,
                body TEXT NOT NULL,
                status TEXT NOT NULL,
                provider_id TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(candidate_id) REFERENCES candidates(id)
            );
            CREATE TABLE IF NOT EXISTS benchmark_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                metrics_json TEXT NOT NULL,
                rows_json TEXT NOT NULL,
                created_by TEXT,
                created_at TEXT NOT NULL
            );
            """
        )


def hash_password(password, salt=None):
    salt_bytes = bytes.fromhex(salt) if salt else secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt_bytes, 240_000)
    return f"{salt_bytes.hex()}:{digest.hex()}"


def verify_password(password, encoded):
    try:
        salt, expected = encoded.split(":", 1)
        actual = hash_password(password, salt).split(":", 1)[1]
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def user_count():
    with db_connection() as db:
        return db.execute("SELECT COUNT(*) FROM users").fetchone()[0]


def create_user(email, name, role, password):
    if role not in {"admin", "recruiter", "hiring_manager"}:
        raise ValueError("Invalid workspace role.")
    if len(password) < 10:
        raise ValueError("Password must contain at least 10 characters.")
    with db_connection() as db:
        cursor = db.execute(
            "INSERT INTO users(email,name,role,password_hash,created_at) VALUES(?,?,?,?,?)",
            (email.lower().strip(), name.strip(), role, hash_password(password), utc_now()),
        )
        return cursor.lastrowid


def authenticate_user(email, password):
    with db_connection() as db:
        row = db.execute(
            "SELECT * FROM users WHERE email=? AND active=1", (email.lower().strip(),)
        ).fetchone()
    if row and verify_password(password, row["password_hash"]):
        return {"id": row["id"], "email": row["email"], "name": row["name"], "role": row["role"]}
    return None


def list_users():
    with db_connection() as db:
        return [dict(row) for row in db.execute("SELECT id,email,name,role,active,created_at FROM users ORDER BY created_at")]


def audit(actor, action, entity_type, entity_id, before=None, after=None):
    with db_connection() as db:
        db.execute(
            "INSERT INTO audit_events(actor,action,entity_type,entity_id,before_json,after_json,created_at) VALUES(?,?,?,?,?,?,?)",
            (actor, action, entity_type, str(entity_id), json.dumps(before, default=str), json.dumps(after, default=str), utc_now()),
        )


def list_audit_events(limit=250):
    with db_connection() as db:
        return [dict(row) for row in db.execute("SELECT * FROM audit_events ORDER BY id DESC LIMIT ?", (limit,))]


def save_job(title, description, analysis, actor):
    now = utc_now()
    with db_connection() as db:
        cursor = db.execute(
            "INSERT INTO jobs(title,description,analysis_json,created_by,created_at,updated_at) VALUES(?,?,?,?,?,?)",
            (title, description, json.dumps(analysis, default=str), actor, now, now),
        )
        job_id = cursor.lastrowid
    audit(actor, "create", "job", job_id, after={"title": title})
    return job_id


def save_candidate(job_id, name, resume_text, workflow, phone="", email="", actor="system"):
    now = utc_now()
    with db_connection() as db:
        existing = db.execute("SELECT * FROM candidates WHERE job_id IS ? AND name=?", (job_id, name)).fetchone()
        before = dict(existing) if existing else None
        existing_workflow = {}
        if existing:
            try:
                existing_workflow = json.loads(existing["workflow_json"] or "{}")
            except Exception:
                existing_workflow = {}
        merged_workflow = {**existing_workflow, **workflow}
        db.execute(
            """INSERT INTO candidates(job_id,name,email,phone,resume_text,workflow_json,created_at,updated_at)
               VALUES(?,?,?,?,?,?,?,?)
               ON CONFLICT(job_id,name) DO UPDATE SET email=excluded.email,phone=excluded.phone,
               resume_text=excluded.resume_text,workflow_json=excluded.workflow_json,updated_at=excluded.updated_at""",
            (job_id, name, email, phone, resume_text, json.dumps(merged_workflow, default=str), now, now),
        )
        row = db.execute("SELECT * FROM candidates WHERE job_id IS ? AND name=?", (job_id, name)).fetchone()
    audit(actor, "update" if before else "create", "candidate", row["id"], before=before, after={"name": name, "workflow": merged_workflow})
    return row["id"]


def list_jobs():
    with db_connection() as db:
        return [dict(row) for row in db.execute("SELECT * FROM jobs ORDER BY updated_at DESC")]


def list_candidates(job_id=None):
    with db_connection() as db:
        if job_id is None:
            rows = db.execute("SELECT * FROM candidates ORDER BY updated_at DESC")
        else:
            rows = db.execute(
                "SELECT * FROM candidates WHERE job_id=? ORDER BY updated_at DESC",
                (job_id,),
            )
        return [dict(row) for row in rows]


def create_portal_token(candidate_id, expires_at=None):
    raw = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    with db_connection() as db:
        db.execute(
            "INSERT INTO portal_tokens(candidate_id,token_hash,expires_at,created_at) VALUES(?,?,?,?)",
            (candidate_id, token_hash, expires_at, utc_now()),
        )
    return raw


def resolve_portal_token(raw_token):
    token_hash = hashlib.sha256(str(raw_token).encode()).hexdigest()
    with db_connection() as db:
        row = db.execute(
            """SELECT c.* FROM portal_tokens t JOIN candidates c ON c.id=t.candidate_id
               WHERE t.token_hash=? AND t.revoked=0
               AND (t.expires_at IS NULL OR t.expires_at > ?)""",
            (token_hash, utc_now()),
        ).fetchone()
    return dict(row) if row else None


def add_candidate_request(candidate_id, request_type, details):
    with db_connection() as db:
        db.execute(
            "INSERT INTO candidate_requests(candidate_id,request_type,details,created_at) VALUES(?,?,?,?)",
            (candidate_id, request_type, details, utc_now()),
        )


def list_candidate_requests():
    with db_connection() as db:
        return [dict(row) for row in db.execute(
            "SELECT r.*,c.name candidate_name FROM candidate_requests r JOIN candidates c ON c.id=r.candidate_id ORDER BY r.id DESC"
        )]


def save_interview(candidate_id, starts_at, duration_minutes, timezone_name, meeting_url, notes, actor):
    with db_connection() as db:
        cursor = db.execute(
            "INSERT INTO interviews(candidate_id,starts_at,duration_minutes,timezone,meeting_url,notes,created_by,created_at) VALUES(?,?,?,?,?,?,?,?)",
            (candidate_id, starts_at, duration_minutes, timezone_name, meeting_url, notes, actor, utc_now()),
        )
    audit(actor, "schedule", "interview", cursor.lastrowid, after={"candidate_id": candidate_id, "starts_at": starts_at})
    return cursor.lastrowid


def list_interviews():
    with db_connection() as db:
        return [dict(row) for row in db.execute(
            "SELECT i.*,c.name candidate_name,c.email candidate_email FROM interviews i JOIN candidates c ON c.id=i.candidate_id ORDER BY starts_at"
        )]


def send_smtp_email(config, recipient, subject, body):
    message = EmailMessage()
    message["From"] = config["from_email"]
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)
    host, port = config["host"], int(config.get("port", 587))
    if config.get("ssl", False):
        server = smtplib.SMTP_SSL(host, port, timeout=20)
    else:
        server = smtplib.SMTP(host, port, timeout=20)
        server.starttls()
    try:
        server.login(config["username"], config["password"])
        server.send_message(message)
    finally:
        server.quit()
    return {"status": "sent", "sent_at": utc_now()}


def log_communication(candidate_id, channel, recipient, subject, body, status, provider_id=""):
    with db_connection() as db:
        db.execute(
            "INSERT INTO communication_log(candidate_id,channel,recipient,subject,body,status,provider_id,created_at) VALUES(?,?,?,?,?,?,?,?)",
            (candidate_id, channel, recipient, subject, body, status, provider_id, utc_now()),
        )


def save_benchmark(name, metrics, rows, actor):
    with db_connection() as db:
        cursor = db.execute(
            "INSERT INTO benchmark_runs(name,metrics_json,rows_json,created_by,created_at) VALUES(?,?,?,?,?)",
            (name, json.dumps(metrics, default=str), json.dumps(rows, default=str), actor, utc_now()),
        )
    audit(actor, "benchmark", "ats", cursor.lastrowid, after=metrics)
    return cursor.lastrowid


def list_benchmarks():
    with db_connection() as db:
        return [dict(row) for row in db.execute("SELECT * FROM benchmark_runs ORDER BY id DESC")]
