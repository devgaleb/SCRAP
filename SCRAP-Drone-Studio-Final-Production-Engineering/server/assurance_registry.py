"""Aircraft configuration and assurance evidence. Administrative, never flight commands."""
import os,sqlite3,json,time,secrets,hashlib
from pathlib import Path
from fastapi import APIRouter,HTTPException,Depends
from pydantic import BaseModel,Field,model_validator
from typing import Literal
ROOT=Path(__file__).resolve().parents[1]
DB=Path(os.getenv("SCRAP_DB",str(ROOT/"data"/"studio.sqlite3")))
def user(authorization: str = __import__("fastapi").Header(default="")):
    from .main import user as authenticate
    return authenticate(authorization)
router=APIRouter(prefix="/api/assurance",tags=["Aircraft assurance"])
class AircraftProfile(BaseModel):
    name:str=Field(min_length=1,max_length=120)
    manufacturer:str=Field(min_length=1,max_length=120)
    aircraft_model:str=Field(min_length=1,max_length=120)
    serial_number:str=Field(min_length=1,max_length=120)
    controller_type:Literal['px4','ardupilot','ros2_mrs','custom']
    controller_manufacturer:str=Field(min_length=1,max_length=120)
    controller_hardware:str=Field(min_length=1,max_length=120)
    firmware_version:str=Field(min_length=1,max_length=120)
    firmware_hash:str=Field(pattern=r'^[0-9a-fA-F]{64}$')
    environment:Literal['indoor','outdoor_vlos','outdoor_bvlos','controlled_test_range']
    jurisdiction:str=Field(min_length=2,max_length=120)
    authority:str=Field(min_length=2,max_length=120)
    operation_category:str=Field(min_length=2,max_length=120)
    approval_reference:str|None=Field(default=None,max_length=200)
    mass_kg:float=Field(gt=0,le=10000)
    max_wind_mps:float=Field(ge=0,le=100)
    failsafe_document:str|None=None
    operator_name:str=Field(min_length=1,max_length=120)
    @model_validator(mode='after')
    def clean(self):
        if self.approval_reference is not None and not self.approval_reference.strip():self.approval_reference=None
        return self
class Evidence(BaseModel):
    aircraft_id:str
    requirement_id:str=Field(pattern=r'^[A-Z0-9_-]{3,64}$')
    title:str=Field(min_length=3,max_length=200)
    method:Literal['review','analysis','simulation','sitl','hil','ground_test','flight_test','independent_assessment']
    outcome:Literal['pass','fail','pending','not_applicable']
    evidence_sha256:str=Field(pattern=r'^[a-fA-F0-9]{64}$')
    artifact_reference:str=Field(min_length=3,max_length=500)
    reviewer:str=Field(min_length=2,max_length=120)
    recorded_at:int=Field(gt=0)
def db():
    c=sqlite3.connect(DB,timeout=15);c.row_factory=sqlite3.Row
    c.execute('CREATE TABLE IF NOT EXISTS aircraft_profiles (id TEXT PRIMARY KEY,owner TEXT NOT NULL,body TEXT NOT NULL,created INTEGER NOT NULL)')
    c.execute('CREATE TABLE IF NOT EXISTS assurance_evidence (id TEXT PRIMARY KEY,owner TEXT NOT NULL,aircraft_id TEXT NOT NULL,body TEXT NOT NULL,created INTEGER NOT NULL)')
    return c
REQUIREMENTS={
'CFG-001':'Controller hardware and firmware traceability',
'CFG-002':'Aircraft model, mass and serial traceability',
'OPS-001':'Operational environment and limitations',
'REG-001':'Jurisdiction, operation category and authorisations',
'SAF-001':'Failsafe behaviour and recovery validation',
'SAF-002':'Trajectory separation and uncertainty validation',
'SAF-003':'Geofence and containment validation',
'SAF-004':'Lost-link and degraded navigation validation',
'SEC-001':'Authentication, access control and audit validation',
'SEC-002':'Firmware provenance and update security',
'TST-001':'Software-in-the-loop regression',
'TST-002':'Hardware-in-the-loop regression',
'TST-003':'Controlled ground and flight testing',
'IND-001':'Independent assessment and release authorisation'}
@router.get('/requirements')
def requirements(u=Depends(user)):return REQUIREMENTS
@router.post('/aircraft',status_code=201)
def add_aircraft(v:AircraftProfile,u=Depends(user)):
    aid=secrets.token_hex(12)
    with db() as c:c.execute('INSERT INTO aircraft_profiles VALUES(?,?,?,?)',(aid,u['id'],v.model_dump_json(),int(time.time())))
    return {'id':aid,'configuration_recorded':True,'certified':False}
@router.get('/aircraft')
def aircraft(u=Depends(user)):
    with db() as c:rows=c.execute('SELECT id,body FROM aircraft_profiles WHERE owner=? ORDER BY created DESC',(u['id'],)).fetchall()
    return [{'id':r['id'],**json.loads(r['body'])} for r in rows]
@router.post('/evidence',status_code=201)
def evidence(v:Evidence,u=Depends(user)):
    if v.requirement_id not in REQUIREMENTS:raise HTTPException(422,'Unknown requirement')
    with db() as c:
        if not c.execute('SELECT 1 FROM aircraft_profiles WHERE id=? AND owner=?',(v.aircraft_id,u['id'])).fetchone():raise HTTPException(404,'Aircraft not found')
        eid=secrets.token_hex(12)
        c.execute('INSERT INTO assurance_evidence VALUES(?,?,?,?,?)',(eid,u['id'],v.aircraft_id,v.model_dump_json(),int(time.time())))
    return {'id':eid,'recorded':True,'verified_independently':False}
@router.get('/readiness/{aircraft_id}')
def readiness(aircraft_id:str,u=Depends(user)):
    with db() as c:
        row=c.execute('SELECT body FROM aircraft_profiles WHERE id=? AND owner=?',(aircraft_id,u['id'])).fetchone()
        if not row:raise HTTPException(404,'Aircraft not found')
        rows=c.execute('SELECT body FROM assurance_evidence WHERE aircraft_id=? AND owner=? ORDER BY created',(aircraft_id,u['id'])).fetchall()
    profile=json.loads(row['body']); records=[json.loads(r['body']) for r in rows]
    latest={r['requirement_id']:r for r in records}
    passed=[k for k,r in latest.items() if r['outcome']=='pass']
    missing=[k for k in REQUIREMENTS if k not in passed]
    return {'aircraft_id':aircraft_id,'profile':profile,'requirements_total':len(REQUIREMENTS),'recorded_passes':passed,'missing_or_unpassed':missing,'evidence_count':len(records),'documentation_complete':not missing,'independently_certified':False,'flight_release_authorized':False,'warning':'Recorded evidence is self-reported; independent verification and regulator/operator approval are required.'}
