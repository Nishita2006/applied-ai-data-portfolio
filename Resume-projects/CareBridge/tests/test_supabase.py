from pathlib import Path
from types import SimpleNamespace
import pytest
from src.auth import AuthError, SupabaseAuth, validate_signup
from src.config import load_config
from src.store import SupabaseStore, friendly_data_error
from src.rag import Chunk, answer

class Query:
    def __init__(self,client,table,action="select",payload=None): self.client=client; self.name=table; self.action=action; self.payload=payload; self.filters=[]
    def select(self,*args): self.action="select"; return self
    def insert(self,payload): self.action="insert"; self.payload=payload; return self
    def upsert(self,payload,**kwargs): self.action="upsert"; self.payload=payload; return self
    def update(self,payload): self.action="update"; self.payload=payload; return self
    def delete(self): self.action="delete"; return self
    def eq(self,key,value): self.filters.append((key,value)); return self
    def order(self,*args,**kwargs): return self
    def limit(self,*args): return self
    def execute(self):
        self.client.calls.append((self.name,self.action,list(self.filters),self.payload))
        records=self.client.data.setdefault(self.name,[])
        matches=lambda row: all(str(row.get(k))==str(v) for k,v in self.filters)
        if self.action=="select": return SimpleNamespace(data=[dict(x) for x in records if matches(x)])
        payloads=self.payload if isinstance(self.payload,list) else [self.payload]
        if self.action in {"insert","upsert"}:
            added=[]
            for value in payloads:
                row={**value}; row.setdefault("id",f"{self.name}-{len(records)+1}"); row.setdefault("created_at","2026-01-01")
                existing=next((x for x in records if x.get("user_id")==row.get("user_id") and self.action=="upsert"),None)
                if existing: existing.update(row); added.append(existing)
                else: records.append(row); added.append(row)
            return SimpleNamespace(data=added)
        if self.action=="update":
            for row in records:
                if matches(row): row.update(self.payload)
            return SimpleNamespace(data=[])
        if self.action=="delete": self.client.data[self.name]=[row for row in records if not matches(row)]
        return SimpleNamespace(data=[])

class Bucket:
    def __init__(self,client): self.client=client
    def upload(self,path,data,options): self.client.uploads.append((path,data,options))
    def remove(self,paths): self.client.removed.extend(paths)
class Storage:
    def __init__(self,client): self.client=client
    def from_(self,name): assert name=="carebridge-records"; return Bucket(self.client)
class Client:
    def __init__(self,data=None): self.data=data or {}; self.calls=[]; self.uploads=[]; self.removed=[]; self.storage=Storage(self)
    def table(self,name): return Query(self,name)

def test_signup_validation():
    validate_signup("person@example.com","password1","password1","Person")
    with pytest.raises(AuthError,match="first name"): validate_signup("person@example.com","password1","password1","")
    with pytest.raises(AuthError): validate_signup("bad","password1","password1","Person")
    with pytest.raises(AuthError): validate_signup("person@example.com","password1","different","Person")

def test_placeholder_supabase_url_is_not_ready(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL","https://your-project-id.supabase.co"); monkeypatch.setenv("SUPABASE_ANON_KEY","anon")
    assert not load_config({}).supabase_ready

def test_missing_supabase_schema_has_actionable_error():
    error=RuntimeError("PGRST205 Could not find the table public.visits in the schema cache")
    message=friendly_data_error(error)
    assert "sql/supabase_schema.sql" in message
    assert "not been installed" in message

def test_auth_errors_are_sanitized():
    client=SimpleNamespace(auth=SimpleNamespace(sign_in_with_password=lambda payload: (_ for _ in ()).throw(RuntimeError("invalid login credentials internal trace"))))
    with pytest.raises(AuthError,match="Check your email and password"): SupabaseAuth(client).sign_in("person@example.com","bad-password")

def test_signup_uses_carebridge_redirect_url():
    captured={}
    client=SimpleNamespace(auth=SimpleNamespace(sign_up=lambda payload: captured.update(payload) or SimpleNamespace(user=None,session=None)))
    SupabaseAuth(client,"https://carebridge.example").sign_up("person@example.com","password1","Person")
    assert captured["options"]["email_redirect_to"]=="https://carebridge.example/?auth=signin&confirmed=1"

def test_store_scopes_visits_to_authenticated_user():
    client=Client({"visits":[{"id":"a","user_id":"user-a","appointment_date":"2026-01-01","appointment_time":"09:00"},{"id":"b","user_id":"user-b","appointment_date":"2026-01-01","appointment_time":"09:00"}]})
    assert [x["id"] for x in SupabaseStore(client,"user-a").list_visits()]==["a"]
    assert [x["id"] for x in SupabaseStore(client,"user-b").list_visits()]==["b"]

def test_retrieval_source_query_is_user_and_visit_scoped():
    client=Client({"documents":[]}); SupabaseStore(client,"user-a").list_items("documents","visit-a")
    _,_,filters,_=client.calls[-1]
    assert ("user_id","user-a") in filters and ("visit_id","visit-a") in filters

def test_user_b_cannot_retrieve_user_a_unique_phrase(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY",raising=False)
    client=Client({"documents":[
        {"id":"doc-a","user_id":"user-a","visit_id":"visit-a","title":"A record","created_at":"2026","document_text":{"extracted_text":"UniqueUserARecord4827"}},
        {"id":"doc-b","user_id":"user-b","visit_id":"visit-b","title":"B record","created_at":"2026","document_text":{"extracted_text":"Routine appointment information"}},
    ]})
    documents=SupabaseStore(client,"user-b").list_items("documents","visit-b")
    chunks=[Chunk(item["extracted_text"],item["title"],"record") for item in documents]
    result=answer("Where is UniqueUserARecord4827 mentioned?",chunks)
    assert result["evidence"]==[]

def test_create_visit_sets_owner_tasks_and_active_visit():
    client=Client(); store=SupabaseStore(client,"user-a")
    visit_id=store.create_visit({"appointment_date":"2026-01-01","appointment_time":"09:00","provider":"Clinic","specialty":"Visit","reason":"Prepare"})
    assert client.data["visits"][0]["user_id"]=="user-a"
    assert len(client.data["readiness_tasks"])==9
    assert client.data["profiles"][0]["active_visit_id"]==visit_id

def test_storage_path_is_user_and_visit_scoped():
    client=Client(); store=SupabaseStore(client,"user-a")
    store.upload_document("visit-a","Record","record.txt","text/plain",b"text","text",{"category":"Referral","confidence":.8})
    assert client.uploads[0][0].startswith("user-a/visit-a/")
    assert client.data["document_text"][0]["user_id"]=="user-a"

def test_rls_sql_covers_all_private_tables_and_storage():
    sql=Path("sql/supabase_schema.sql").read_text(encoding="utf-8").lower()
    for table in ["profiles","visits","readiness_tasks","symptoms","medications","allergies","documents","document_text","provider_questions","visit_briefs"]:
        assert f"alter table public.{table} enable row level security" in sql
    assert "storage.foldername(name)" in sql
    assert "service_role" not in sql

def test_config_never_requires_service_role(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL","https://example.supabase.co"); monkeypatch.setenv("SUPABASE_ANON_KEY","anon")
    config=load_config({}); assert config.supabase_ready and config.supabase_anon_key=="anon"
