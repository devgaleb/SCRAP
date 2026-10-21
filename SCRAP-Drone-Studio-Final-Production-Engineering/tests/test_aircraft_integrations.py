import pytest
from pydantic import ValidationError
from server.aircraft_integrations import Capabilities,TelemetryEnvelope,Controller,REGISTRY

def test_all_controllers_listed():
    assert set(REGISTRY)=={x.value for x in Controller}
def test_commands_cannot_be_enabled():
    with pytest.raises(ValidationError):Capabilities(controller='px4',protocol='mavlink',firmware_version='v1',hardware_model='unit',flight_command_access=True)
def test_valid_telemetry():
    v=TelemetryEnvelope(aircraft_id='drone-1',controller='custom',source_timestamp_ms=1700000000000,sequence=3,latitude_deg=51.1)
    assert v.sequence==3
def test_reject_invalid_gps():
    with pytest.raises(ValidationError):TelemetryEnvelope(aircraft_id='drone-1',controller='px4',source_timestamp_ms=1700000000000,sequence=1,latitude_deg=100)
def test_reject_nonfinite():
    with pytest.raises(ValidationError):TelemetryEnvelope(aircraft_id='drone-1',controller='px4',source_timestamp_ms=1700000000000,sequence=1,altitude_m=float('nan'))
