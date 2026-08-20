from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Any
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "carebridge.db"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"
DEFAULT_TASKS = ["Appointment details confirmed","Insurance information prepared","Referral information prepared if needed","Medication list reviewed","Allergy information reviewed","Symptoms documented","Requested records uploaded","Transportation arranged if relevant","Provider questions prepared"]

def connect(path: Path = DB_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db=sqlite3.connect(path,check_same_thread=False); db.row_factory=sqlite3.Row; db.execute("PRAGMA foreign_keys=ON"); return db
def initialize(path: Path = DB_PATH) -> None:
    with connect(path) as db:
        existing={row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "preparation_tasks" in existing:
            columns={row[1] for row in db.execute("PRAGMA table_info(preparation_tasks)")}
            if "visit_id" not in columns:
                # Remove the original bundled fictional workspace before creating the
                # user-driven schema. That legacy release did not store end-user visits.
                db.executescript("""
                DROP TABLE IF EXISTS symptom_responses;
                DROP TABLE IF EXISTS questions;
                DROP TABLE IF EXISTS documents;
                DROP TABLE IF EXISTS medications;
                DROP TABLE IF EXISTS symptoms;
                DROP TABLE IF EXISTS preparation_tasks;
                DROP TABLE IF EXISTS appointments;
                DROP TABLE IF EXISTS patients;
                """)
        db.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
def rows(sql: str, params: tuple[Any,...]=(), path: Path=DB_PATH) -> list[dict[str,Any]]:
        with connect(path) as db: return [dict(r) for r in db.execute(sql,params).fetchall()]
def query(sql: str, params: tuple[Any,...]=(), path: Path=DB_PATH) -> pd.DataFrame:
    with connect(path) as db: return pd.read_sql_query(sql,db,params=params)
def one(sql: str, params: tuple[Any,...]=(), path: Path=DB_PATH) -> dict[str,Any] | None:
    result=rows(sql,params,path); return result[0] if result else None
def execute(sql: str, params: tuple[Any,...]=(), path: Path=DB_PATH) -> int:
    with connect(path) as db: return int(db.execute(sql,params).lastrowid or 0)
def create_visit(data: dict[str,Any], path: Path=DB_PATH) -> int:
    with connect(path) as db:
        cur=db.execute("INSERT INTO visits(appointment_date,appointment_time,provider,specialty,reason,location,notes) VALUES(?,?,?,?,?,?,?)",tuple(data.get(k,"") for k in ("appointment_date","appointment_time","provider","specialty","reason","location","notes")))
        visit_id=int(cur.lastrowid); db.executemany("INSERT INTO preparation_tasks(visit_id,title,position) VALUES(?,?,?)",[(visit_id,t,i) for i,t in enumerate(DEFAULT_TASKS)]); return visit_id
def update_item(table: str,item_id: int,values: dict[str,Any],path: Path=DB_PATH)->None:
    if table not in {"visits","preparation_tasks","symptoms","medications","allergies","documents","questions"} or not values: raise ValueError("Invalid update")
    execute(f"UPDATE {table} SET "+",".join(f"{k}=?" for k in values)+" WHERE id=?",(*values.values(),item_id),path)
def delete_item(table: str,item_id: int,path: Path=DB_PATH)->None:
    if table not in {"visits","symptoms","medications","allergies","documents","questions"}: raise ValueError("Invalid delete")
    execute(f"DELETE FROM {table} WHERE id=?",(item_id,),path)
