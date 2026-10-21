"""Authenticated read-only telemetry ingress. Does not issue aircraft commands."""
import os,time,hmac,hashlib,secrets,sqlite3,json
from pathlib import Path
from fastapi import APIRouter,HTTPException,Header
from pydantic import BaseModel,Field
router=APIRouter(prefix='/api/bridge',tags=['Read-only telemetry'])
DB=Path(os.getenv('SCRAP_TELEMETRY_DB',str(Path(__file__).resolve().parents[1]/'data'/'telemetry.sqlite3')))
DB.parent.mkdir(parents=True,exist_ok=True)
def connect():
    c=sqlite3.connect(DB,timeout=10);c.execute('PRAGMA journal_mode=WAL');c.execute('CREATE TABLE IF NOT EXISTS samples(id INTEGER PRIMARY KEY AUTOINCREMENT, drone TEXT, source TEXT, received REAL, body TEXT)');return c
class Sample(BaseModel):
    drone_id:str=Field(min_length=1,max_length=80,pattern=r'^[a-zA-Z0-9_.:-]+$')
    source:str=Field(min_length=1,max_length=80)
    timestamp:float=Field(gt=0)
    battery_percent:float|None=Field(default=None,ge=0,le=100)
    altitude_m:float|None=Field(default=None,ge=-10000,le=100000)
    latitude:float|None=Field(default=None,ge=-90,le=90)
    longitude:float|None=Field(default=None,ge=-180,le=180)
    armed:bool|None=None

def require_key(x_bridge_key:str=Header(default='')):
    key=os.getenv('SCRAP_BRIDGE_KEY','')
    if len(key)<24:raise HTTPException(503,'Bridge disabled: configure SCRAP_BRIDGE_KEY (24+ chars)')
    if not hmac.compare_digest(x_bridge_key,key):raise HTTPException(401,'Invalid bridge key')
@router.post('/telemetry',dependencies=[])
def ingest(sample:Sample,x_bridge_key:str=Header(default='')):
    require_key(x_bridge_key)
    if abs(time.time()-sample.timestamp)>300:raise HTTPException(422,'Timestamp outside five-minute window')
    with connect() as c:c.execute('INSERT INTO samples(drone,source,received,body) VALUES(?,?,?,?)',(sample.drone_id,sample.source,time.time(),sample.model_dump_json()))
    return {'accepted':True,'command_capability':False}
@router.get('/telemetry/{drone_id}')
def latest(drone_id:str,x_bridge_key:str=Header(default='')):
    require_key(x_bridge_key)
    with connect() as c:row=c.execute('SELECT body,received FROM samples WHERE drone=? ORDER BY id DESC LIMIT 1',(drone_id,)).fetchone()
    if not row:raise HTTPException(404,'No telemetry for drone')
    return {'sample':json.loads(row[0]),'received':row[1],'stale':time.time()-row[1]>10}
