import os, json, base64, hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from fastapi.testclient import TestClient
from server.main import app

def test_signed_manifest_and_tampering(tmp_path,monkeypatch):
 import server.trust_center as tc
 monkeypatch.setattr(tc,'DB',tmp_path/'trust.sqlite3')
 monkeypatch.setenv('SCRAP_TRUST_ADMIN_KEY','z'*40)
 client=TestClient(app)
 private=Ed25519PrivateKey.generate()
 public=private.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
 r=client.post('/api/trust/keys',headers={'x-trust-admin-key':'z'*40},json={'key_id':'test-key','public_key_base64':base64.b64encode(public).decode(),'provenance':'Verified out of band for unit testing'})
 assert r.status_code==200,r.text
 sha=hashlib.sha256(b'firmware-test').hexdigest()
 manifest={'artifact_sha256':sha,'controller':'px4','hardware':'testboard','firmware_version':'1.0'}
 canonical=json.dumps(manifest,sort_keys=True,separators=(',',':')).encode()
 sig=base64.b64encode(private.sign(canonical)).decode()
 payload={'key_id':'test-key','manifest':manifest,'signature_base64':sig,'artifact_sha256':sha}
 good=client.post('/api/trust/verify-manifest',json=payload)
 assert good.status_code==200 and good.json()['signature_valid'] is True
 assert good.json()['installed_firmware_verified'] is False
 payload['manifest']['firmware_version']='2.0'
 bad=client.post('/api/trust/verify-manifest',json=payload)
 assert bad.status_code==200 and bad.json()['signature_valid'] is False
