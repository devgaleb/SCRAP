"""Offline firmware artifact verification and aircraft compatibility evidence.
Never asserts installed firmware identity or grants flight authority.
"""
import os, json, hashlib, base64, sqlite3, time
from pathlib import Path
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

router=APIRouter(prefix='/api/trust',tags=['Firmware artifact trust and compatibility'])
DB=Path(os.getenv('SCRAP_TRUST_DB',str(Path(__file__).resolve().parents[1]/'data'/'trust.sqlite3')))
DB.parent.mkdir(parents=True,exist_ok=True)
def db():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row
 c.execute('CREATE TABLE IF NOT EXISTS trusted_keys(key_id TEXT PRIMARY KEY, public_key TEXT NOT NULL, source TEXT NOT NULL, added INTEGER NOT NULL)')
 c.execute('CREATE TABLE IF NOT EXISTS compatibility(id INTEGER PRIMARY KEY AUTOINCREMENT, controller TEXT NOT NULL, hardware TEXT NOT NULL, firmware TEXT NOT NULL, evidence_url TEXT NOT NULL, reviewed_by TEXT NOT NULL, added INTEGER NOT NULL)')
 c.execute('CREATE TABLE IF NOT EXISTS verification_log(id INTEGER PRIMARY KEY AUTOINCREMENT, key_id TEXT, artifact_sha256 TEXT, result TEXT, at INTEGER NOT NULL)')
 return c
class KeyRegistration(BaseModel):
 key_id:str=Field(pattern=r'^[A-Za-z0-9_.:-]{3,80}$')
 public_key_base64:str=Field(max_length=200)
 provenance:str=Field(min_length=8,max_length=500)
class Compatibility(BaseModel):
 controller:str=Field(pattern=r'^(px4|ardupilot|mrs_ros2|custom)$')
 hardware:str=Field(min_length=2,max_length=150)
 firmware:str=Field(min_length=1,max_length=100)
 evidence_url:str=Field(min_length=8,max_length=500)
 reviewed_by:str=Field(min_length=2,max_length=120)
class VerifyRequest(BaseModel):
 key_id:str=Field(min_length=3,max_length=80)
 manifest:dict
 signature_base64:str=Field(min_length=40,max_length=300)
 artifact_sha256:str=Field(pattern=r'^[a-f0-9]{64}$')
def admin(x_trust_admin_key:str=Header(default='')):
 import hmac
 secret=os.getenv('SCRAP_TRUST_ADMIN_KEY','')
 if len(secret)<32:raise HTTPException(503,'Trust administration disabled: set SCRAP_TRUST_ADMIN_KEY')
 if not hmac.compare_digest(secret,x_trust_admin_key):raise HTTPException(403,'Administrator key required')
@router.post('/keys')
def register_key(v:KeyRegistration,x_trust_admin_key:str=Header(default='')):
 admin(x_trust_admin_key)
 try:
  raw=base64.b64decode(v.public_key_base64,validate=True)
  if len(raw)!=32:raise ValueError('Ed25519 public key must be 32 bytes')
  Ed25519PublicKey.from_public_bytes(raw)
 except Exception:raise HTTPException(422,'Invalid Ed25519 public key')
 with db() as c:
  try:c.execute('INSERT INTO trusted_keys VALUES(?,?,?,?)',(v.key_id,v.public_key_base64,v.provenance,int(time.time())))
  except sqlite3.IntegrityError:raise HTTPException(409,'Key ID already registered; rotation requires a new key ID')
 return {'registered':True,'key_id':v.key_id,'trust_source':'operator-registered; not independently certified'}
@router.post('/compatibility')
def add_compat(v:Compatibility,x_trust_admin_key:str=Header(default='')):
 admin(x_trust_admin_key)
 with db() as c:c.execute('INSERT INTO compatibility(controller,hardware,firmware,evidence_url,reviewed_by,added) VALUES(?,?,?,?,?,?)',(*v.model_dump().values(),int(time.time())))
 return {'recorded':True,'status':'operator-reviewed evidence, not physical compatibility confirmation'}
@router.get('/compatibility')
def list_compat():
 with db() as c:rows=c.execute('SELECT controller,hardware,firmware,evidence_url,reviewed_by,added FROM compatibility ORDER BY id DESC LIMIT 200').fetchall()
 return {'records':[dict(x) for x in rows],'physical_compatibility_verified':False}
@router.post('/verify-manifest')
def verify(v:VerifyRequest):
 """Signature covers canonical JSON manifest. Manifest SHA must match independently supplied artifact SHA.
 Caller must hash actual firmware bytes locally; this endpoint does not inspect an installed device.
 """
 with db() as c:row=c.execute('SELECT public_key FROM trusted_keys WHERE key_id=?',(v.key_id,)).fetchone()
 if not row:raise HTTPException(404,'Unknown signing key')
 manifest=v.manifest
 if set(manifest)!={'artifact_sha256','controller','hardware','firmware_version'} or not all(isinstance(x,str) and x for x in manifest.values()):raise HTTPException(422,'Manifest requires exactly artifact_sha256, controller, hardware, firmware_version')
 if manifest['artifact_sha256']!=v.artifact_sha256:raise HTTPException(422,'Manifest digest does not match supplied artifact digest')
 canonical=json.dumps(manifest,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
 try:
  signature=base64.b64decode(v.signature_base64,validate=True)
  Ed25519PublicKey.from_public_bytes(base64.b64decode(row['public_key'])).verify(signature,canonical)
  valid=True
 except (ValueError,InvalidSignature):valid=False
 with db() as c:c.execute('INSERT INTO verification_log(key_id,artifact_sha256,result,at) VALUES(?,?,?,?)',(v.key_id,v.artifact_sha256,'valid' if valid else 'invalid',int(time.time())))
 return {'signature_valid':valid,'artifact_digest_supplied_by_caller':True,'installed_firmware_verified':False,'flight_approval':False,'meaning':'Signature authenticates manifest under operator-registered key only'}
