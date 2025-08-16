import json
from pathlib import Path

def test_config_flow_enabled():
    manifest_path = Path(__file__).resolve().parents[1] / 'custom_components' / 'ha_mqtt_sensors' / 'manifest.json'
    data = json.loads(manifest_path.read_text())
    assert data.get('config_flow') is True
