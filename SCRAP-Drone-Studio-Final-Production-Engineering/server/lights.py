"""Offline LED choreography compiler. No hardware or flight commands."""
import math
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

router=APIRouter(prefix='/api/lights',tags=['Light choreography'])
class Cue(BaseModel):
    at:float=Field(ge=0,le=3600)
    color:str=Field(pattern=r'^#[0-9a-fA-F]{6}$')
    brightness:float=Field(ge=0,le=1,default=1)
    effect:str=Field(default='solid',pattern=r'^(solid|pulse|strobe|rainbow|fade)$')
    speed:float=Field(default=1,ge=0.1,le=5)
class RenderRequest(BaseModel):
    cues:list[Cue]=Field(min_length=1,max_length=300)
    duration:float=Field(gt=0,le=3600)
    fps:int=Field(default=10,ge=1,le=30)
    drones:int=Field(default=24,ge=1,le=500)

def blend(a,b,t):return round(a+(b-a)*t)
def rgb(c):return [int(c[i:i+2],16) for i in (1,3,5)]
def hexcolor(v):return '#'+''.join(f'{max(0,min(255,round(x))):02x}' for x in v)
def render(v):
    if v.duration*v.fps*v.drones>250000:raise HTTPException(413,'Preview too large; reduce duration, fps, or drones')
    cues=sorted(v.cues,key=lambda c:c.at)
    if cues[0].at>0:raise HTTPException(422,'First cue must start at 0')
    if cues[-1].at>v.duration:raise HTTPException(422,'Cue exceeds duration')
    frames=[]; j=0
    for k in range(math.ceil(v.duration*v.fps)):
        t=k/v.fps
        while j+1<len(cues) and cues[j+1].at<=t:j+=1
        cue=cues[j]; nxt=cues[j+1] if j+1<len(cues) else None
        elapsed=t-cue.at
        brightness=cue.brightness
        if cue.effect=='pulse':brightness*=0.5+0.5*math.sin(elapsed*cue.speed*math.tau)
        elif cue.effect=='strobe':brightness*=1 if int(elapsed*cue.speed*8)%2==0 else 0
        base=rgb(cue.color)
        if cue.effect=='fade' and nxt:
            p=max(0,min(1,(t-cue.at)/(nxt.at-cue.at))) if nxt.at>cue.at else 1
            base=[blend(a,b,p) for a,b in zip(base,rgb(nxt.color))]
        colors=[]
        for d in range(v.drones):
            if cue.effect=='rainbow':
                h=(d/v.drones+elapsed*cue.speed*.15)%1
                import colorsys
                r,g,b=colorsys.hsv_to_rgb(h,1,brightness)
                colors.append(hexcolor([255*r,255*g,255*b]))
            else:colors.append(hexcolor([x*brightness for x in base]))
        frames.append({'t':round(t,3),'colors':colors})
    return {'mode':'simulation-only','flight_control_enabled':False,'fps':v.fps,'drones':v.drones,'frames':frames}
@router.post('/preview')
def preview(v:RenderRequest):return render(v)
@router.get('/presets')
def presets():return {'presets':{'Aurora':[{'at':0,'color':'#00c9ff','effect':'pulse','speed':0.6},{'at':5,'color':'#b56cff','effect':'rainbow','speed':0.4},{'at':10,'color':'#19f5b3','effect':'fade'}],'Festival':[{'at':0,'color':'#ff6b37','effect':'strobe','speed':0.8},{'at':4,'color':'#ffd347','effect':'pulse'},{'at':8,'color':'#56dfff','effect':'rainbow'}]}}
