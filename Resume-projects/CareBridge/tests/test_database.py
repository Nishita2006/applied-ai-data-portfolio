from pathlib import Path
import pytest
from src.database import create_visit, delete_item, execute, initialize, one, rows, update_item

@pytest.fixture
def db(tmp_path: Path):
    path=tmp_path/"carebridge.db"; initialize(path); return path
def visit(db): return create_visit({"appointment_date":"2026-09-18","appointment_time":"10:30","provider":"Clinic","specialty":"Primary care","reason":"Prepare","location":"","notes":""},db)
def test_schema_starts_empty(db): assert rows("SELECT * FROM visits",path=db)==[]
def test_create_visit_and_default_tasks(db):
    vid=visit(db); assert one("SELECT * FROM visits WHERE id=?",(vid,),db)["provider"]=="Clinic"; assert len(rows("SELECT * FROM preparation_tasks WHERE visit_id=?",(vid,),db))==9
def test_update_visit(db):
    vid=visit(db); update_item("visits",vid,{"provider":"New Clinic"},db); assert one("SELECT provider FROM visits WHERE id=?",(vid,),db)["provider"]=="New Clinic"
@pytest.mark.parametrize("table,columns,values",[("symptoms","visit_id,name","?,?"),("medications","visit_id,name","?,?"),("allergies","visit_id,allergy","?,?"),("questions","visit_id,question","?,?")])
def test_crud(db,table,columns,values):
    vid=visit(db); item=execute(f"INSERT INTO {table}({columns}) VALUES({values})",(vid,"entered value"),db); assert one(f"SELECT * FROM {table} WHERE id=?",(item,),db); delete_item(table,item,db); assert one(f"SELECT * FROM {table} WHERE id=?",(item,),db) is None
def test_readiness_persists(db):
    vid=visit(db); task=one("SELECT * FROM preparation_tasks WHERE visit_id=?",(vid,),db); update_item("preparation_tasks",task["id"],{"completed":1,"notes":"done"},db); assert one("SELECT * FROM preparation_tasks WHERE id=?",(task["id"],),db)["notes"]=="done"
def test_document_persistence(db):
    vid=visit(db); execute("INSERT INTO documents(visit_id,title,extracted_text) VALUES(?,?,?)",(vid,"Referral","Appointment date is listed."),db); assert one("SELECT * FROM documents WHERE visit_id=?",(vid,),db)["extracted_text"]
def test_visit_delete_cascades(db):
    vid=visit(db); execute("INSERT INTO symptoms(visit_id,name) VALUES(?,?)",(vid,"Pain"),db); delete_item("visits",vid,db); assert rows("SELECT * FROM symptoms",path=db)==[]
