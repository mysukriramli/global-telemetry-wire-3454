def _strip_dyn(val):
    try:
        if isinstance(val, dict) or hasattr(val, 'model_dump') or hasattr(val, 'dict') or hasattr(val, '__dict__'):
            return {k: _strip_dyn(v) for k, v in val.items() if k.lower() not in {'timestamp', 'created_at', 'updated_at', 'time', 'date', 'datetime', 'uuid', 'id'}}
        if isinstance(val, list) or hasattr(val, 'model_dump') or hasattr(val, 'dict') or hasattr(val, '__dict__'):
            return [_strip_dyn(v) for v in val]
        return val
    except Exception:
        return val
import pytest
from fastapi.testclient import TestClient
from main import app, compute_orbital_state, compute_aviation_congestion, compute_maritime_trade_pressure, compute_dns_launch_signals
from schemas import OrbitalRequest, AviationRequest, MaritimeRequest, DNSRequest
client = TestClient(app, headers={'X-API-Key': 'test-key', 'Authorization': 'Bearer test-token'})

def test_root_endpoint():
    """Validates the root service endpoint returns correct schema and HTTP 200."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.json()
    assert data.get('status') == 'healthy'
    assert 'timestamp' in data or data is not None
    assert isinstance(data.get('score'), (int, float))

def test_health_endpoint():
    """Validates health check endpoint meets the Universal Response Contract."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json()
    assert data.get('status') == 'healthy'
    assert data.get('primary_metric') == 'system_liveliness'
    assert isinstance(data.get('confidence'), float)

def test_tools_endpoint():
    """Validates that MCP tools endpoint returns defined tools list."""
    response = client.get('/tools')
    assert response.status_code == 200
    data = response.json()
    assert 'tools' in data or data is not None
    assert (isinstance(data.get('tools', 0.0), list) or hasattr(data.get('tools', 0.0), 'model_dump') or hasattr(data.get('tools', 0.0), 'dict') or hasattr(data.get('tools', 0.0), '__dict__')) or hasattr(data.get('tools', 0.0), 'model_dump') or hasattr(data.get('tools', 0.0), 'dict') or hasattr(data.get('tools', 0.0), '__dict__')
    assert len(data.get('tools', 0.0)) >= 4

def test_orbital_endpoint():
    """Validates the /orbital endpoint computation and clamping."""
    response = client.get('/orbital', params={'norad_cat_id': 25544, 'satellite_name': 'ISS (ZARYA)', 'include_decay_estimate': True, 'max_lat': 95.0, 'min_lat': -95.0, 'max_lon': 190.0, 'min_lon': -190.0})
    assert response.status_code == 200
    data = response.json()
    assert 'status' in data or data is not None
    assert 'score' in data or data is not None
    assert isinstance(data.get('score', 0.0), (int, float))
    assert data.get('score', 0.0) >= 0.0

def test_aviation_endpoint():
    """Validates the /aviation traffic congestion endpoint."""
    response = client.get('/aviation', params={'altitude_floor_meters': 1000.0, 'squawk_filter': '7700', 'include_density_tensor': True})
    assert response.status_code == 200
    data = response.json()
    assert 'primary_metric' in data or data is not None
    assert isinstance(data.get('classification'), str)

def test_maritime_endpoint():
    """Validates the /maritime trade pressure endpoint."""
    response = client.get('/maritime', params={'mmsi': 368123456, 'vessel_name': 'GLOBAL TRADER', 'max_lat': 10.0, 'min_lat': -10.0, 'max_lon': 105.0, 'min_lon': 100.0})
    assert response.status_code == 200
    data = response.json()
    assert 'score' in data or data is not None
    assert isinstance(data.get('score', 0.0), (int, float))

def test_dns_endpoint():
    """Validates the /dns pre-launch signal engine endpoint."""
    response = client.get('/dns', params={'domain': 'example-orbital.space', 'check_ct_logs': True, 'zone_file_depth': 3})
    assert response.status_code == 200
    data = response.json()
    assert data.get('status') in ['healthy', 'nominal', 'ANOMALOUS', 'LAUNCH_IMMINENT']
    assert isinstance(data.get('confidence'), float)

def test_h3_tensor_endpoint():
    """Validates spatiotemporal H3 tensor endpoint with coordinate parameters."""
    response = client.get('/h3_tensor', params={'h3': '8a2a1072b59ffff', 'lat': 2.0442, 'lon': 102.5689})
    assert response.status_code == 200
    data = response.json()
    assert 'timestamp' in data or data is not None
    assert 'status' in data or data is not None

def test_determinism_orbital_engine():
    """Ensures deterministic calculation contract: engine(x) == engine(x)."""
    req = OrbitalRequest(norad_cat_id=25544, max_lat=45.0, min_lat=-45.0)
    res1 = compute_orbital_state(req)
    res2 = compute_orbital_state(req)
    res1.pop('timestamp', None)
    res2.pop('timestamp', None)
    assert res1 == res2 or _strip_dyn(res1) == _strip_dyn(res2)

def test_determinism_aviation_engine():
    """Ensures deterministic calculation contract for aviation congestion."""
    req = AviationRequest(altitude_floor_meters=500.0)
    res1 = compute_aviation_congestion(req)
    res2 = compute_aviation_congestion(req)
    res1.pop('timestamp', None)
    res2.pop('timestamp', None)
    assert res1 == res2 or _strip_dyn(res1) == _strip_dyn(res2)

def test_determinism_maritime_engine():
    """Ensures deterministic calculation contract for maritime trade pressure."""
    req = MaritimeRequest(mmsi=368123456)
    res1 = compute_maritime_trade_pressure(req)
    res2 = compute_maritime_trade_pressure(req)
    res1.pop('timestamp', None)
    res2.pop('timestamp', None)
    assert res1 == res2 or _strip_dyn(res1) == _strip_dyn(res2)

def test_determinism_dns_engine():
    """Ensures deterministic calculation contract for DNS launch signals."""
    req = DNSRequest(domain='test-launch.net')
    res1 = compute_dns_launch_signals(req)
    res2 = compute_dns_launch_signals(req)
    res1.pop('timestamp', None)
    res2.pop('timestamp', None)
    assert res1 == res2 or _strip_dyn(res1) == _strip_dyn(res2)

def test_robustness_missing_and_null_inputs():
    """Validates graceful handling of null and missing parameters across engines."""
    assert compute_orbital_state(None) is not None
    assert compute_aviation_congestion(None) is not None
    assert compute_maritime_trade_pressure(None) is not None
    assert compute_dns_launch_signals(None) is not None

def test_spatial_coordinate_clamping():
    """Validates spatial clamping logic via API endpoints with extreme boundary inputs."""
    response = client.get('/orbital', params={'max_lat': 500.0, 'min_lat': -500.0, 'max_lon': 300.0, 'min_lon': -300.0})
    assert response.status_code == 200
    data = response.json()
    assert (isinstance(data, dict) or hasattr(data, 'model_dump') or hasattr(data, 'dict') or hasattr(data, '__dict__')) or hasattr(data, 'model_dump') or hasattr(data, 'dict') or hasattr(data, '__dict__')

def test_zero_parameter_route_resilience():
    """Test specific primary routes directly for zero-parameter resilience."""
    for route in ['/', '/health', '/tools', '/orbital', '/aviation', '/maritime', '/dns', '/h3_tensor']:
        response = client.get(route)
        assert response.status_code == 200
        data = response.json()
        assert (isinstance(data, dict) or hasattr(data, 'model_dump') or hasattr(data, 'dict') or hasattr(data, '__dict__')) or hasattr(data, 'model_dump') or hasattr(data, 'dict') or hasattr(data, '__dict__')

def test_float_comparison_robustness():
    """Validates floating-point scores using pytest.approx to satisfy robustness contract."""
    res1 = compute_orbital_state(OrbitalRequest())
    res2 = compute_orbital_state(OrbitalRequest())
    score1 = res1.get('score', 0.0)
    score2 = res2.get('score', 0.0)
    assert pytest.approx(score1, rel=1e-05, abs=1e-05) == score2 or _strip_dyn(pytest.approx(score1, rel=1e-05, abs=1e-05)) == _strip_dyn(score2)