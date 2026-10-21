"""Aircraft-neutral, read-only telemetry integration contract. No command transmission."""
from __future__ import annotations
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from fastapi import APIRouter, Depends, HTTPException
import math

class Controller(str,Enum):
    PX4='px4'
    ARDUPILOT='ardupilot'
    MRS_ROS2='mrs_ros2'
    CUSTOM='custom'

class Capabilities(BaseModel):
    controller:Controller
    protocol:str=Field(min_length=1,max_length=60)
    firmware_version:str=Field(min_length=1,max_length=80)
    hardware_model:str=Field(min_length=1,max_length=120)
    telemetry_fields:list[str]=Field(default_factory=list,max_length=40)
    flight_command_access:Literal[False]=False
    evidence_reference:str|None=Field(default=None,max_length=180)

class TelemetryEnvelope(BaseModel):
    schema_version:Literal['1.0']='1.0'
    aircraft_id:str=Field(pattern=r'^[a-zA-Z0-9_.:-]{1,80}$')
    controller:Controller
    source_timestamp_ms:int=Field(gt=0)
    sequence:int=Field(ge=0)
    latitude_deg:float|None=Field(default=None,ge=-90,le=90)
    longitude_deg:float|None=Field(default=None,ge=-180,le=180)
    altitude_m:float|None=Field(default=None,ge=-10000,le=100000)
    battery_percent:float|None=Field(default=None,ge=0,le=100)
    link_quality_percent:float|None=Field(default=None,ge=0,le=100)
    armed:bool|None=None
    mode:str|None=Field(default=None,max_length=80)
    @model_validator(mode='after')
    def check_finite(self):
        for field in ('latitude_deg','longitude_deg','altitude_m','battery_percent','link_quality_percent'):
            value=getattr(self,field)
            if value is not None and not math.isfinite(value):raise ValueError('Non-finite telemetry value')
        return self

REGISTRY={
 'px4':{'protocols':['MAVLink via independently deployed telemetry gateway'],'notes':'Firmware and vehicle-specific validation required'},
 'ardupilot':{'protocols':['MAVLink via independently deployed telemetry gateway'],'notes':'Firmware and vehicle-specific validation required'},
 'mrs_ros2':{'protocols':['ROS2 topic subscriber via independently deployed telemetry gateway'],'notes':'ROS distribution, message types and DDS domain must be validated'},
 'custom':{'protocols':['Versioned telemetry envelope via authenticated bridge'],'notes':'Provide custom hardware interface specification and safety evidence'},
}
router=APIRouter(prefix='/api/aircraft',tags=['Aircraft integration contracts'])
@router.get('/controller-types')
def controller_types():return {'controllers':REGISTRY,'command_execution':False}
@router.post('/validate-capabilities')
def validate_capabilities(v:Capabilities):return {'valid':True,'controller':v.controller,'command_execution':False,'missing_evidence':not bool(v.evidence_reference)}
@router.post('/validate-telemetry')
def validate_telemetry(v:TelemetryEnvelope):return {'valid':True,'aircraft_id':v.aircraft_id,'sequence':v.sequence,'command_execution':False}
