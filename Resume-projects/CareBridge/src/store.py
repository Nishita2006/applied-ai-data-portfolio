from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
from src.database import DEFAULT_TASKS, create_visit as sqlite_create, delete_item as sqlite_delete, execute, one, rows, update_item as sqlite_update

TABLE_MAP={"preparation_tasks":"readiness_tasks","questions":"provider_questions"}

def friendly_data_error(exc: Exception) -> str:
    text=str(exc).lower()
    if "pgrst205" in text or "schema cache" in text or "could not find the table" in text:
        return "CareBridge's database tables have not been installed in this Supabase project. Run sql/supabase_schema.sql in the Supabase SQL Editor, then reload the app."
    if "permission denied" in text or "row-level security" in text:
        return "CareBridge cannot access your workspace because the Supabase security policies are missing or incomplete. Reapply sql/supabase_schema.sql, then reload the app."
    return "CareBridge could not load your workspace from Supabase. Check the app logs and verify that the database schema was applied successfully."

class LocalStore:
    def __init__(self,path: Path,user_id: str="local"): self.path=path; self.user_id=user_id
    def list_visits(self): return rows("SELECT * FROM visits ORDER BY appointment_date,appointment_time",path=self.path)
    def get_visit(self,visit_id): return one("SELECT * FROM visits WHERE id=?",(visit_id,),self.path)
    def list_items(self,table,visit_id): return rows(f"SELECT * FROM {table} WHERE visit_id=? ORDER BY {'position,id' if table=='questions' else 'id'}",(visit_id,),self.path)
    def create_visit(self,data): return sqlite_create(data,self.path)
    def insert(self,table,data):
        fields=list(data); marks=",".join("?" for _ in fields)
        return execute(f"INSERT INTO {table}({','.join(fields)}) VALUES({marks})",tuple(data[k] for k in fields),self.path)
    def update(self,table,item_id,data): sqlite_update(table,item_id,data,self.path)
    def delete(self,table,item_id): sqlite_delete(table,item_id,self.path)
    def confirm_brief(self,visit_id,confirmed): self.update("visits",visit_id,{"brief_confirmed":int(confirmed)})
    def set_active_visit(self,visit_id): return None
    def get_active_visit(self): return None
    def upload_document(self,visit_id,title,filename,mime,data,text,pred):
        return self.insert("documents",{"visit_id":visit_id,"title":title,"filename":filename,"mime_type":mime,"extracted_text":text,"suggested_category":pred["category"],"confidence":pred["confidence"],"category":pred["category"] if pred["category"]!="Uncertain" else "Other"})

class SupabaseStore:
    def __init__(self,client: Any,user_id: str): self.client=client; self.user_id=user_id
    def _table(self,name): return self.client.table(TABLE_MAP.get(name,name))
    def list_visits(self): return self._table("visits").select("*").eq("user_id",self.user_id).order("appointment_date").order("appointment_time").execute().data or []
    def get_visit(self,visit_id):
        data=self._table("visits").select("*").eq("user_id",self.user_id).eq("id",visit_id).limit(1).execute().data or []
        return data[0] if data else None
    def list_items(self,table,visit_id):
        name=TABLE_MAP.get(table,table); selection="*,document_text(extracted_text)" if table=="documents" else "*"
        query=self.client.table(name).select(selection).eq("user_id",self.user_id).eq("visit_id",visit_id)
        query=query.order("position").order("created_at") if table=="questions" else query.order("created_at")
        data=query.execute().data or []
        if table=="documents":
            for item in data:
                nested=item.pop("document_text",None)
                item["extracted_text"]=(nested or {}).get("extracted_text","") if isinstance(nested,dict) else ((nested or [{}])[0].get("extracted_text","") if nested else "")
        return data
    def create_visit(self,data):
        payload={**data,"user_id":self.user_id}; visit=self._table("visits").insert(payload).execute().data[0]; visit_id=visit["id"]
        try:
            self._table("preparation_tasks").insert([{"user_id":self.user_id,"visit_id":visit_id,"title":title,"position":i} for i,title in enumerate(DEFAULT_TASKS)]).execute()
            self.set_active_visit(visit_id)
        except Exception:
            self._table("visits").delete().eq("user_id",self.user_id).eq("id",visit_id).execute(); raise
        return visit_id
    def insert(self,table,data):
        payload={**data,"user_id":self.user_id}; return self._table(table).insert(payload).execute().data[0]["id"]
    def update(self,table,item_id,data): self._table(table).update(data).eq("user_id",self.user_id).eq("id",item_id).execute()
    def delete(self,table,item_id):
        if table=="documents":
            found=self.client.table("documents").select("storage_path").eq("user_id",self.user_id).eq("id",item_id).limit(1).execute().data or []
            if found and found[0].get("storage_path"): self.client.storage.from_("carebridge-records").remove([found[0]["storage_path"]])
        self._table(table).delete().eq("user_id",self.user_id).eq("id",item_id).execute()
    def set_active_visit(self,visit_id):
        self.client.table("profiles").update({"active_visit_id":visit_id}).eq("user_id",self.user_id).execute()
    def get_active_visit(self):
        data=self.client.table("profiles").select("active_visit_id").eq("user_id",self.user_id).limit(1).execute().data or []
        return data[0].get("active_visit_id") if data else None
    def confirm_brief(self,visit_id,confirmed):
        self.client.table("visits").update({"brief_confirmed":bool(confirmed)}).eq("user_id",self.user_id).eq("id",visit_id).execute()
        self.client.table("visit_briefs").upsert({"user_id":self.user_id,"visit_id":visit_id,"confirmed":bool(confirmed),"confirmed_at":datetime.now(timezone.utc).isoformat() if confirmed else None},on_conflict="visit_id").execute()
    def upload_document(self,visit_id,title,filename,mime,data,text,pred):
        document_id=str(uuid4()); safe_name=Path(filename).name.replace("/","_").replace("\\","_"); storage_path=f"{self.user_id}/{visit_id}/{document_id}/{safe_name}"
        self.client.storage.from_("carebridge-records").upload(storage_path,data,{"content-type":mime,"upsert":"false"})
        try:
            category=pred["category"] if pred["category"]!="Uncertain" else "Other"
            self.client.table("documents").insert({"id":document_id,"user_id":self.user_id,"visit_id":visit_id,"title":title,"filename":filename,"mime_type":mime,"storage_path":storage_path,"suggested_category":pred["category"],"confidence":pred["confidence"],"category":category}).execute()
            self.client.table("document_text").insert({"document_id":document_id,"user_id":self.user_id,"visit_id":visit_id,"extracted_text":text}).execute()
            return document_id
        except Exception:
            try: self.client.storage.from_("carebridge-records").remove([storage_path])
            except Exception: pass
            raise
