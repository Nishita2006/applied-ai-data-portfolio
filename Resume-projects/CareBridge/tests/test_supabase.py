from pathlib import Path
from types import SimpleNamespace
import pytest
from src.auth import AuthError, SupabaseAuth, clear_user_session, validate_signup
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
    def rpc(self,name,payload):
        assert name=="create_visit_with_tasks"
        client=self
        class Rpc:
            def execute(self):
                visit_id=f"visits-{len(client.data.setdefault('visits',[]))+1}"
                client.data['visits'].append({"id":visit_id,"user_id":"user-a",**{k[2:]:v for k,v in payload.items() if k.startswith('p_') and k!='p_task_titles'}})
                tasks=client.data.setdefault('readiness_tasks',[])
                tasks.extend({"id":f"task-{len(tasks)+1}","user_id":"user-a","visit_id":visit_id,"title":title,"position":i} for i,title in enumerate(payload['p_task_titles']))
                for profile in client.data.setdefault('profiles',[]):
                    if profile.get('user_id')=='user-a': profile['active_visit_id']=visit_id
                client.calls.append((name,"rpc",[],payload))
                return SimpleNamespace(data=visit_id)
        return Rpc()

def test_signup_validation():
    validate_signup("person@example.com","password1","password1","Person")
    validate_signup("person@example.com","password1","password1","")
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

def test_duplicate_email_has_friendly_error():
    client=SimpleNamespace(auth=SimpleNamespace(sign_up=lambda payload: (_ for _ in ()).throw(RuntimeError("User already registered"))))
    with pytest.raises(AuthError,match="account already exists for this email"):
        SupabaseAuth(client).sign_up("person@example.com","password1","")

def test_successful_login_restores_user():
    raw=SimpleNamespace(id="user-a",email="person@example.com",user_metadata={"first_name":"Person"})
    response=SimpleNamespace(user=raw,session=object())
    client=SimpleNamespace(auth=SimpleNamespace(sign_in_with_password=lambda payload: response))
    result=SupabaseAuth(client).sign_in("person@example.com","password1")
    assert SupabaseAuth.user(result).id=="user-a"

def test_logout_state_cleanup_removes_all_user_specific_values():
    state={"auth_user":object(),"active_visit_id":"visit-a","nav":"Records","record_question":"private","supabase_client":object()}
    clear_user_session(state)
    assert state=={}

def test_password_reset_uses_supabase_supported_methods():
    calls=[]
    auth_api=SimpleNamespace(
        reset_password_for_email=lambda email,options: calls.append(("request",email,options)),
        verify_otp=lambda payload: calls.append(("verify",payload)) or SimpleNamespace(session=object()),
        update_user=lambda payload: calls.append(("update",payload)),
    )
    auth=SupabaseAuth(SimpleNamespace(auth=auth_api))
    auth.request_password_reset("person@example.com","https://carebridge.example/")
    auth.verify_recovery("single-use-token")
    auth.update_password("new-password","new-password")
    assert calls==[
        ("request","person@example.com",{"redirect_to":"https://carebridge.example/"}),
        ("verify",{"token_hash":"single-use-token","type":"recovery"}),
        ("update",{"password":"new-password"}),
    ]

def test_password_reset_validates_matching_passwords():
    auth=SupabaseAuth(SimpleNamespace(auth=SimpleNamespace()))
    with pytest.raises(AuthError,match="do not match"): auth.update_password("new-password","different")

def test_signup_allows_optional_first_name():
    captured={}
    client=SimpleNamespace(auth=SimpleNamespace(sign_up=lambda payload: captured.update(payload) or SimpleNamespace(user=None,session=None)))
    SupabaseAuth(client).sign_up("person@example.com","password1","Person")
    assert captured["options"]["data"]["first_name"]=="Person"

def test_duplicate_first_names_are_allowed():
    calls=[]
    client=SimpleNamespace(auth=SimpleNamespace(sign_up=lambda payload: calls.append(payload) or SimpleNamespace(user=None,session=None)))
    SupabaseAuth(client).sign_up("one@example.com","password1","Same Name")
    SupabaseAuth(client).sign_up("two@example.com","password1","Same Name")
    assert len(calls)==2

def test_store_scopes_visits_to_authenticated_user():
    client=Client({"visits":[{"id":"a","user_id":"user-a","appointment_date":"2026-01-01","appointment_time":"09:00"},{"id":"b","user_id":"user-b","appointment_date":"2026-01-01","appointment_time":"09:00"}]})
    assert [x["id"] for x in SupabaseStore(client,"user-a").list_visits()]==["a"]
    assert [x["id"] for x in SupabaseStore(client,"user-b").list_visits()]==["b"]

def test_active_visit_restores_and_updates_for_owner():
    client=Client({"profiles":[{"user_id":"user-a","active_visit_id":"visit-a"}]}); store=SupabaseStore(client,"user-a")
    assert store.get_active_visit()=="visit-a"
    store.set_active_visit("visit-b")
    assert client.data["profiles"][0]["active_visit_id"]=="visit-b"

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
    client=Client({"profiles":[{"user_id":"user-a","first_name":"Person"}]}); store=SupabaseStore(client,"user-a")
    visit_id=store.create_visit({"appointment_date":"2026-01-01","appointment_time":"09:00","provider":"Clinic","specialty":"Visit","reason":"Prepare"})
    assert client.data["visits"][0]["user_id"]=="user-a"
    assert len(client.data["readiness_tasks"])==9
    assert client.data["profiles"][0]["active_visit_id"]==visit_id
    assert client.calls[-1][0]=="create_visit_with_tasks"

def test_storage_path_is_user_and_visit_scoped():
    client=Client(); store=SupabaseStore(client,"user-a")
    store.upload_document("visit-a","Record","record.txt","text/plain",b"text","text",{"category":"Referral","confidence":.8})
    assert client.uploads[0][0].startswith("user-a/visit-a/")
    assert client.data["document_text"][0]["user_id"]=="user-a"

def test_failed_text_save_cleans_document_row_and_private_object():
    class FailingQuery(Query):
        def execute(self):
            if self.name=="document_text" and self.action=="insert": raise RuntimeError("text save failed")
            return super().execute()
    class FailingClient(Client):
        def table(self,name): return FailingQuery(self,name)
    client=FailingClient(); store=SupabaseStore(client,"user-a")
    with pytest.raises(RuntimeError,match="text save failed"):
        store.upload_document("visit-a","Record","record.txt","text/plain",b"text","text",{"category":"Referral","confidence":.8})
    assert client.data["documents"]==[]
    assert client.removed==[client.uploads[0][0]]

@pytest.mark.parametrize(("table","payload","field","updated"),[
    ("symptoms",{"name":"Initial"},"name","Updated"),
    ("medications",{"name":"Initial"},"name","Updated"),
    ("allergies",{"allergy":"Initial"},"allergy","Updated"),
    ("questions",{"question":"Initial","position":0},"question","Updated"),
])
def test_supabase_crud_is_owner_scoped(table,payload,field,updated):
    client=Client(); store=SupabaseStore(client,"user-a")
    item_id=store.insert(table,{"visit_id":"visit-a",**payload})
    store.update(table,item_id,{field:updated})
    store.delete(table,item_id)
    mapped="provider_questions" if table=="questions" else table
    calls=[call for call in client.calls if call[0]==mapped]
    assert all(("user_id","user-a") in call[2] for call in calls[1:])
    assert not client.data[mapped]

def test_rls_sql_covers_all_private_tables_and_storage():
    sql=Path("sql/supabase_schema.sql").read_text(encoding="utf-8").lower()
    for table in ["profiles","visits","readiness_tasks","symptoms","medications","allergies","documents","document_text","provider_questions","visit_briefs"]:
        assert f"alter table public.{table} enable row level security" in sql
    assert "storage.foldername(name)" in sql
    assert "service_role" not in sql
    assert "drop index if exists public.profiles_first_name_unique" in sql
    assert "drop function if exists public.is_first_name_available" in sql
    assert "create_visit_with_tasks" in sql

def test_config_never_requires_service_role(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL","https://example.supabase.co"); monkeypatch.setenv("SUPABASE_ANON_KEY","anon")
    config=load_config({}); assert config.supabase_ready and config.supabase_anon_key=="anon"
