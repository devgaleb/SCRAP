import os,tempfile
f=tempfile.NamedTemporaryFile(delete=False);os.environ['SCRAP_DB']=f.name
from fastapi.testclient import TestClient
from server.main import app
c=TestClient(app)
def test_auth_and_isolation():
    assert c.get('/api/health').json()['flight_control_enabled'] is False
    assert c.get('/api/fleet').status_code==401
    assert c.post('/api/auth/register',json={'username':'pilot1','password':'correct-horse-battery-staple'}).status_code==200
    token=c.post('/api/auth/login',json={'username':'pilot1','password':'correct-horse-battery-staple'}).json()['access_token']
    h={'Authorization':'Bearer '+token}
    r=c.post('/api/fleet',headers=h,json={'name':'Test drone','body':{'platform':'PX4','status':'offline'}})
    assert r.status_code==201
    assert len(c.get('/api/fleet',headers=h).json())==1
    assert c.get('/api/integrations/capabilities',headers=h).json()['command_execution'] is False
    assert c.delete('/api/fleet/'+r.json()['id'],headers=h).status_code==200
    assert c.get('/api/fleet',headers=h).json()==[]
