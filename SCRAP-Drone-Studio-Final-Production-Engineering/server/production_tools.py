"""Deterministic show authoring, safety analysis and export; no aircraft actuation."""
import math, csv, io, zipfile, json, hashlib
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
router=APIRouter(prefix='/api/studio',tags=['Advanced studio tools'])
class Point(BaseModel):
    x:float=Field(ge=-10000,le=10000)
    y:float=Field(ge=-10000,le=10000)
    z:float=Field(ge=0,le=10000)
class Frame(BaseModel):
    at:float=Field(ge=0,le=7200)
    positions:list[Point]=Field(min_length=1,max_length=500)
class Show(BaseModel):
    name:str=Field(min_length=1,max_length=120)
    frames:list[Frame]=Field(min_length=1,max_length=500)
    min_separation:float=Field(default=2,gt=0,le=100)
    max_speed:float=Field(default=8,gt=0,le=100)
    max_altitude:float=Field(default=120,gt=0,le=10000)
def inspect(show):
    frames=sorted(show.frames,key=lambda f:f.at)
    n=len(frames[0].positions); issues=[]
    if any(len(f.positions)!=n for f in frames):issues.append({'code':'DRONE_COUNT','detail':'Each keyframe must have the same number of drones'})
    if len({f.at for f in frames})!=len(frames):issues.append({'code':'DUPLICATE_TIME','detail':'Keyframe timestamps must be unique'})
    for fi,f in enumerate(frames):
        for i,p in enumerate(f.positions):
            if p.z>show.max_altitude:issues.append({'code':'ALTITUDE','frame':fi,'drone':i,'value':p.z})
        for i in range(len(f.positions)):
            for j in range(i+1,len(f.positions)):
                a,b=f.positions[i],f.positions[j]
                d=math.dist((a.x,a.y,a.z),(b.x,b.y,b.z))
                if d<show.min_separation:issues.append({'code':'SEPARATION','frame':fi,'drones':[i,j],'distance':round(d,3)})
                if len(issues)>200:return {'valid':False,'issues':issues,'truncated':True}
    if all(len(f.positions)==n for f in frames):
        for fi in range(1,len(frames)):
            a,b=frames[fi-1],frames[fi];dt=b.at-a.at
            if dt<=0:continue
            for i,(p,q) in enumerate(zip(a.positions,b.positions)):
                speed=math.dist((p.x,p.y,p.z),(q.x,q.y,q.z))/dt
                if speed>show.max_speed:issues.append({'code':'SPEED','frame':fi,'drone':i,'speed':round(speed,3)})
    return {'valid':not issues,'issues':issues,'drones':n,'keyframes':len(frames),'duration':frames[-1].at-frames[0].at,'note':'Keyframe checks are not a continuous-path collision guarantee or flight authorization'}
@router.post('/validate')
def validate(show:Show):return inspect(show)
@router.post('/export')
def export(show:Show):
    report=inspect(show)
    if not report['valid']:raise HTTPException(422,{'message':'Resolve validation issues before export','report':report})
    data=show.model_dump(); data['frames'].sort(key=lambda x:x['at'])
    raw=json.dumps(data,indent=2).encode()
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('show.json',raw)
        z.writestr('validation.json',json.dumps(report,indent=2))
        z.writestr('manifest.json',json.dumps({'format':'SCRAP_SHOW_V1','sha256':hashlib.sha256(raw).hexdigest(),'hardware_commands':False},indent=2))
        z.writestr('README.txt','Offline choreography export. NOT a flight-ready mission. Validate with qualified operators and hardware-specific systems before use.\n')
    buf.seek(0)
    return StreamingResponse(buf,media_type='application/zip',headers={'Content-Disposition':'attachment; filename="scrap-show-export.zip"'})
class Generator(BaseModel):
    name:str='Generated formation'
    shape:str=Field(pattern='^(circle|grid|helix|heart)$')
    drones:int=Field(ge=3,le=300)
    radius:float=Field(default=15,gt=0,le=1000)
    altitude:float=Field(default=30,ge=0,le=10000)
    duration:float=Field(default=20,gt=0,le=7200)
@router.post('/generate')
def generate(v:Generator):
    pts=[]
    for i in range(v.drones):
        t=2*math.pi*i/v.drones
        if v.shape=='circle':x,y=v.radius*math.cos(t),v.radius*math.sin(t)
        elif v.shape=='grid':
            side=math.ceil(math.sqrt(v.drones));step=2*v.radius/max(1,side-1);x,y=(i%side)*step-v.radius,(i//side)*step-v.radius
        elif v.shape=='helix':x,y=v.radius*math.cos(t*3),v.radius*math.sin(t*3)
        else:x,y=v.radius*16*math.sin(t)**3/18,v.radius*(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))/18
        pts.append({'x':round(x,3),'y':round(y,3),'z':round(v.altitude+(i/v.drones)*v.radius if v.shape=='helix' else v.altitude,3)})
    return {'name':v.name,'frames':[{'at':0,'positions':pts},{'at':v.duration,'positions':pts}],'min_separation':2,'max_speed':8,'max_altitude':120}
