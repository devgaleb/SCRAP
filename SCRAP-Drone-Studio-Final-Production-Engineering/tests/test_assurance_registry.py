from server.assurance_registry import AircraftProfile,REQUIREMENTS
from pydantic import ValidationError
import pytest
def sample():
 return dict(name='A',manufacturer='Vendor',aircraft_model='X',serial_number='S1',controller_type='custom',controller_manufacturer='Vendor',controller_hardware='Board Rev B',firmware_version='1.2.3',firmware_hash='a'*64,environment='controlled_test_range',jurisdiction='UK',authority='CAA',operation_category='Specific',mass_kg=1.5,max_wind_mps=5,operator_name='Operator')
def test_valid_profile():assert AircraftProfile(**sample()).controller_type=='custom'
def test_unknown_controller_rejected():
 d=sample();d['controller_type']='unknown'
 with pytest.raises(ValidationError):AircraftProfile(**d)
def test_invalid_firmware_hash_rejected():
 d=sample();d['firmware_hash']='unverified'
 with pytest.raises(ValidationError):AircraftProfile(**d)
def test_requirements_defined():assert len(REQUIREMENTS)>=10
