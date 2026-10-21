"""Conservative offline linear-segment trajectory analysis, NOT flight certification."""
import math
from fastapi import APIRouter
from pydantic import BaseModel, Field
router=APIRouter(prefix='/api/verification',tags=['Offline verification'])
class P(BaseModel):
    x:float=Field(ge=-100000,le=100000)
    y:float=Field(ge=-100000,le=100000)
    z:float=Field(ge=-100000,le=100000)
class F(BaseModel):
    at:float=Field(ge=0,le=86400)
    positions:list[P]=Field(min_length=1,max_length=200)
class Trajectory(BaseModel):
    frames:list[F]=Field(min_length=2,max_length=200)
    min_separation:float=Field(default=3,gt=0,le=1000)
    max_speed:float=Field(default=8,gt=0,le=200)
    min_altitude:float=Field(default=0,ge=-100000,le=100000)
    max_altitude:float=Field(default=120,ge=-100000,le=100000)

def vec(p):return (p.x,p.y,p.z)
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def dist(a,b):return math.sqrt(dot(sub(a,b),sub(a,b)))
def verify(t:Trajectory):
    frames=t.frames; n=len(frames[0].positions);issues=[]
    def issue(code,**kw):
        if len(issues)<300:issues.append({'code':code,**kw})
    if t.max_altitude<t.min_altitude:issue('ALTITUDE_BOUNDS')
    if any(len(f.positions)!=n for f in frames):issue('INCONSISTENT_FLEET');return {'valid':False,'issues':issues,'model':'piecewise-linear'}
    for k,f in enumerate(frames):
        if any(not t.min_altitude<=p.z<=t.max_altitude for p in f.positions):issue('ALTITUDE',frame=k)
        if k==0:continue
        prev=frames[k-1];dt=f.at-prev.at
        if dt<=0:issue('NON_INCREASING_TIME',frame=k);continue
        starts=[vec(p) for p in prev.positions];ends=[vec(p) for p in f.positions]
        velocities=[tuple(v/dt for v in sub(b,a)) for a,b in zip(starts,ends)]
        for i,(a,b) in enumerate(zip(starts,ends)):
            speed=dist(a,b)/dt
            if speed>t.max_speed:issue('SPEED',segment=k-1,drone=i,speed=round(speed,4))
        for i in range(n):
            for j in range(i+1,n):
                relative_start=sub(starts[i],starts[j]);relative_velocity=sub(velocities[i],velocities[j]);den=dot(relative_velocity,relative_velocity)
                tau=max(0,min(dt,-dot(relative_start,relative_velocity)/den)) if den>1e-16 else 0
                delta=tuple(relative_start[d]+tau*relative_velocity[d] for d in range(3))
                distance=math.sqrt(dot(delta,delta))
                if distance<t.min_separation:issue('CONTINUOUS_SEPARATION',segment=k-1,drones=[i,j],time=round(prev.at+tau,5),distance=round(distance,5))
    return {'valid':not issues,'issues':issues,'truncated':len(issues)>=300,'model':'piecewise-linear, exact closest approach per overlapping segment','certified':False,'limitations':['Assumes straight-line constant-speed motion between keyframes','No wind, GPS uncertainty, latency, dynamic obstacles, aircraft envelopes or controller dynamics','Not suitable as sole basis for real flight authorization']}
@router.post('/trajectory')
def trajectory(t:Trajectory):return verify(t)
