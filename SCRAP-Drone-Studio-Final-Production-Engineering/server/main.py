"""SCRAP operations API. No flight-command endpoints are exposed."""
import os, json, sqlite3, secrets, hashlib, hmac, time, re
from contextlib import contextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, Header, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

ROOT=Path(__file__).resolve().parents[1]
DB=Path(os.getenv('SCRAP_DB',str(ROOT/'data'/'studio.sqlite3')))
DB.parent.mkdir(parents=True,exist_ok=True)
from .lights import router as lights_router
app=FastAPI(title='SCRAP Drone Studio API',version='2.0.0',description='Design, simulation, and read-only integration API; not flight control')

app.include_router(lights_router)
from .production_tools import router as production_router
app.include_router(production_router)
from .aircraft_integrations import router as aircraft_router
app.include_router(aircraft_router)

def conn():
    c=sqlite3.connect(DB,timeout=15);c.row_factory=sqlite3.Row;c.execute('PRAGMA journal_mode=WAL');return c

def init():
    with conn() as c:
        c.executescript('''CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,username TEXT UNIQUE NOT NULL,salt TEXT NOT NULL,hash TEXT NOT NULL,role TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS tokens(token_hash TEXT PRIMARY KEY,user_id TEXT NOT NULL,expires INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS resources(id TEXT PRIMARY KEY,kind TEXT NOT NULL,owner TEXT NOT NULL,name TEXT NOT NULL,body TEXT NOT NULL,updated INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT,actor TEXT,action TEXT,resource TEXT,at INTEGER NOT NULL);
        CREATE INDEX IF NOT EXISTS resources_owner_kind ON resources(owner,kind);''')
init()

def digest(p,s):return hashlib.pbkdf2_hmac('sha256',p.encode(),bytes.fromhex(s),260000).hex()
def audit(c,u,a,r=''):c.execute('INSERT INTO audit(actor,action,resource,at) VALUES(?,?,?,?)',(u,a,r,int(time.time())))
class Credentials(BaseModel):
    username:str=Field(min_length=3,max_length=50,pattern=r'^[a-zA-Z0-9_.-]+$')
    password:str=Field(min_length=12,max_length=256)
class Resource(BaseModel):
    name:str=Field(min_length=1,max_length=120)
    body:dict
class ImportRecord(BaseModel):
    source:str=Field(min_length=1,max_length=120)
    timestamp:int
    values:dict

@app.post('/api/auth/register')
def register(v:Credentials):
    s=secrets.token_hex(16);uid=secrets.token_hex(12)
    try:
        with conn() as c:
            c.execute('INSERT INTO users VALUES(?,?,?,?,?)',(uid,v.username,s,digest(v.password,s),'operator'))
            audit(c,uid,'register')
    except sqlite3.IntegrityError:raise HTTPException(409,'Username already exists')
    return {'created':True}
@app.post('/api/auth/login')
def login(v:Credentials):
    with conn() as c:
        row=c.execute('SELECT * FROM users WHERE username=?',(v.username,)).fetchone()
        valid=row and hmac.compare_digest(digest(v.password,row['salt']),row['hash'])
        if not valid:raise HTTPException(401,'Invalid credentials')
        token=secrets.token_urlsafe(32)
        c.execute('INSERT INTO tokens VALUES(?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),row['id'],int(time.time())+86400))
        audit(c,row['id'],'login')
    return {'access_token':token,'token_type':'bearer','expires_in':86400}

def user(authorization:str=Header(default='')):
    if not authorization.startswith('Bearer '):raise HTTPException(401,'Bearer token required')
    key=hashlib.sha256(authorization[7:].encode()).hexdigest()
    with conn() as c:
        row=c.execute('SELECT users.id,users.username,users.role FROM tokens JOIN users ON tokens.user_id=users.id WHERE token_hash=? AND expires>?',(key,int(time.time()))).fetchone()
    if not row:raise HTTPException(401,'Token invalid or expired')
    return dict(row)
@app.post('/api/auth/logout')
def logout(authorization:str=Header(default=''),u=Depends(user)):
    with conn() as c:c.execute('DELETE FROM tokens WHERE token_hash=?',(hashlib.sha256(authorization[7:].encode()).hexdigest(),))
    return {'logged_out':True}
@app.get('/api/me')
def me(u=Depends(user)):return u
@app.get('/api/health')
def health():return {'status':'ok','mode':'planning-and-simulation','flight_control_enabled':False}
KINDS={'fleet','missions','shows','telemetry','maps','settings'}
def kind_ok(kind):
    if kind not in KINDS:raise HTTPException(404,'Unknown resource type')
@app.get('/api/{kind}')
def list_resources(kind:str,u=Depends(user)):
    kind_ok(kind)
    with conn() as c:rows=c.execute('SELECT id,name,body,updated FROM resources WHERE kind=? AND owner=? ORDER BY updated DESC LIMIT 500',(kind,u['id'])).fetchall()
    return [{'id':r['id'],'name':r['name'],'body':json.loads(r['body']),'updated':r['updated']} for r in rows]
@app.post('/api/{kind}',status_code=201)
def create_resource(kind:str,v:Resource,u=Depends(user)):
    kind_ok(kind)
    raw=json.dumps(v.body,allow_nan=False)
    if len(raw)>250000:raise HTTPException(413,'Resource too large')
    rid=secrets.token_hex(12)
    with conn() as c:
        c.execute('INSERT INTO resources VALUES(?,?,?,?,?,?)',(rid,kind,u['id'],v.name,raw,int(time.time())))
        audit(c,u['id'],'create:'+kind,rid)
    return {'id':rid,'name':v.name}
@app.put('/api/{kind}/{rid}')
def update_resource(kind:str,rid:str,v:Resource,u=Depends(user)):
    kind_ok(kind)
    raw=json.dumps(v.body,allow_nan=False)
    if len(raw)>250000:raise HTTPException(413,'Resource too large')
    with conn() as c:
        cur=c.execute('UPDATE resources SET name=?,body=?,updated=? WHERE id=? AND kind=? AND owner=?',(v.name,raw,int(time.time()),rid,kind,u['id']))
        if not cur.rowcount:raise HTTPException(404,'Not found')
        audit(c,u['id'],'update:'+kind,rid)
    return {'updated':True}
@app.delete('/api/{kind}/{rid}')
def delete_resource(kind:str,rid:str,u=Depends(user)):
    kind_ok(kind)
    with conn() as c:
        cur=c.execute('DELETE FROM resources WHERE id=? AND kind=? AND owner=?',(rid,kind,u['id']))
        if not cur.rowcount:raise HTTPException(404,'Not found')
        audit(c,u['id'],'delete:'+kind,rid)
    return {'deleted':True}
@app.get('/api/audit/events')
def audit_events(u=Depends(user)):
    with conn() as c:rows=c.execute('SELECT action,resource,at FROM audit WHERE actor=? ORDER BY id DESC LIMIT 100',(u['id'],)).fetchall()
    return [dict(r) for r in rows]
@app.get('/api/integrations/capabilities')
def capabilities(u=Depends(user)):
    return {'ros2':'adapter required','mavlink':'adapter required','px4':'adapter required','ardupilot':'adapter required','mrs':'adapter required','telemetry_import':'available via resources','command_execution':False}
@app.websocket('/api/ws/simulation')
async def simulation(ws:WebSocket):
    await ws.accept()
    try:
        while True:
            message=await ws.receive_json()
            if message.get('type')!='preview':
                await ws.send_json({'error':'Only preview messages accepted; flight commands unavailable'});continue
            points=message.get('points',[])
            if not isinstance(points,list) or len(points)>500 or any(not isinstance(p,dict) or not all(isinstance(p.get(k), (float,int)) and 0<=p[k]<=1 for k in ('x','y')) for p in points):
                await ws.send_json({'error':'Invalid normalized preview points'});continue
            await ws.send_json({'type':'preview','count':len(points),'mode':'simulation-only','timestamp':int(time.time())})
    except WebSocketDisconnect:pass

app.mount('/static',StaticFiles(directory=ROOT/'app'),name='static')
@app.get('/operations')
def operations():return FileResponse(ROOT/'app'/'operations.html')
@app.get('/')
def index():return FileResponse(ROOT/'app'/'index.html')

@app.get('/lights')
def lights_studio():return FileResponse(ROOT/'app'/'lights.html')

@app.get("/advanced")
def advanced():return FileResponse(ROOT/"app"/"advanced.html")

from .verification import router as verification_router
from .telemetry_bridge import router as bridge_router
app.include_router(verification_router)
app.include_router(bridge_router)

from .assurance_registry import router as assurance_router
app.include_router(assurance_router)

from .trust_center import router as trust_router
app.include_router(trust_router)
