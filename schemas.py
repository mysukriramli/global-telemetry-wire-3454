from datetime import datetime, timezone as dt_timezone
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from pydantic import BaseModel, Field

def _utc_now_str() -> str:
    """Returns current UTC timestamp formatted to ISO8601 string with Z suffix."""
    return datetime.now(dt_timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

class HealthResponse(BaseModel):
    """Health check response schema fulfilling Universal Response and Health contracts."""
    status: str = 'healthy'
    timestamp: str = Field(default_factory=_utc_now_str)
    score: float = 100.0
    classification: str = 'OPTIMAL'
    confidence: float = 1.0
    primary_metric: str = 'system_liveliness'

class ToolItem(BaseModel):
    """Individual MCP tool definition schema."""
    name: str = ''
    description: str = ''
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)

class ToolsResponse(BaseModel):
    """Response schema for listing available MCP tools."""
    tools: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: str = Field(default_factory=_utc_now_str)
    status: str = 'healthy'

class OrbitalRequest(BaseModel):
    """Request model for orbital telemetry and TLE satellite state queries."""
    norad_cat_id: Optional[int] = Field(default=25544, description='NORAD Catalog ID (default: ISS)')
    satellite_name: Optional[str] = Field(default='ISS (ZARYA)', description='Common name of spacecraft')
    include_decay_estimate: bool = Field(default=True, description='Whether to compute orbital decay projections')
    max_lat: float = Field(default=90.0, description='Northern latitude boundary constraint')
    min_lat: float = Field(default=-90.0, description='Southern latitude boundary constraint')
    max_lon: float = Field(default=180.0, description='Eastern longitude boundary constraint')
    min_lon: float = Field(default=-180.0, description='Western longitude boundary constraint')

class AviationRequest(BaseModel):
    """Request model for ADS-B aviation state and air traffic congestion queries."""
    bounding_box: List[float] = Field(default_factory=lambda: [-90.0, -180.0, 90.0, 180.0], description='[lat_min, lon_min, lat_max, lon_max]')
    altitude_floor_meters: float = Field(default=0.0, description='Minimum altitude filter')
    squawk_filter: Optional[str] = Field(default=None, description='Optional squawk code filter (e.g. 7500, 7700)')
    include_density_tensor: bool = Field(default=True, description='Compute H3 spatial congestion tensor')

class MaritimeRequest(BaseModel):
    """Request model for AIS maritime state and trade route pressure analysis."""
    vessel_type_filter: Optional[str] = Field(default='ALL', description='Cargo, Tanker, Passenger, Tug, ALL')
    min_speed_knots: float = Field(default=0.0, description='Minimum vessel speed threshold')
    max_speed_knots: float = Field(default=50.0, description='Maximum vessel speed threshold')
    h3_resolution: int = Field(default=3, description='H3 spatial indexing resolution')
    corridor_id: Optional[str] = Field(default='GLOBAL_ALL', description='Strategic maritime choke point identifier')

class DNSRequest(BaseModel):
    """Request model for Certificate Transparency and DNS pre-launch signal scanning."""
    domain_query: str = Field(default='*', description='Domain name or wildcard suffix pattern')
    lookback_hours: int = Field(default=24, description='Time window for certificate issuance ingestion')
    min_entropy_score: float = Field(default=3.5, description='Shannon entropy threshold for obfuscated pre-launch domains')
    resolver_ip: str = Field(default='1.1.1.1', description='Authoritative DNS resolver target for record probing')

class SpatialTensorRequest(BaseModel):
    """Request model for unified multi-domain H3 spatial tensor queries."""
    h3_index: str = Field(default='83754effffffffff', description='H3 hexagonal index string')
    resolution: int = Field(default=3, description='H3 resolution level (0-15)')
    include_orbital: bool = Field(default=True, description='Incorporate satellite footprint overlap')
    include_aviation: bool = Field(default=True, description='Incorporate air corridor density')
    include_maritime: bool = Field(default=True, description='Incorporate vessel traffic volume')
    include_dns: bool = Field(default=True, description='Incorporate regional DNS infrastructure signals')

class OrbitalStateResponse(BaseModel):
    """Authoritative response schema for orbital telemetry analysis."""
    timestamp: str = Field(default_factory=_utc_now_str)
    status: str = 'healthy'
    score: float = 85.0
    classification: str = 'NOMINAL'
    confidence: float = 0.95
    primary_metric: str = 'orbital_density'
    norad_cat_id: int = 25544
    satellite_name: str = 'ISS (ZARYA)'
    latitude: float = 0.0
    longitude: float = 0.0
    altitude_km: float = 420.0
    velocity_kms: float = 7.66
    orbital_density: float = 1.45
    decay_probability: float = 0.01
    agent_readable_summary: str = 'Orbital state nominal. No collision vectors detected within threshold.'

class AviationStateResponse(BaseModel):
    """Authoritative response schema for aviation congestion analysis."""
    timestamp: str = Field(default_factory=_utc_now_str)
    status: str = 'healthy'
    score: float = 78.5
    classification: str = 'CONGESTED'
    confidence: float = 0.92
    primary_metric: str = 'air_traffic_congestion'
    active_aircraft_count: int = 1420
    air_traffic_congestion: float = 78.5
    average_altitude_meters: int = 10600
    anomaly_count: int = 2
    h3_congestion_tensor: Dict[str, float] = Field(default_factory=dict)
    agent_readable_summary: str = 'Air traffic density elevated across North Atlantic corridors.'

class MaritimeStateResponse(BaseModel):
    """Authoritative response schema for maritime trade pressure analysis."""
    timestamp: str = Field(default_factory=_utc_now_str)
    status: str = 'healthy'
    score: float = 88.0
    classification: str = 'NOMINAL'
    confidence: float = 0.94
    primary_metric: str = 'maritime_trade_volume'
    active_vessels_tracked: int = 4850
    maritime_trade_volume: float = 485.2
    choke_point_congestion_index: float = 42.1
    average_speed_knots: float = 14.2
    agent_readable_summary: str = 'Global maritime trade volume stable with normal throughput at key straits.'

class DNSSignalResponse(BaseModel):
    """Authoritative response schema for DNS pre-launch signal detection."""
    timestamp: str = Field(default_factory=_utc_now_str)
    status: str = 'healthy'
    score: float = 91.0
    classification: str = 'LAUNCH_IMMINENT'
    confidence: float = 0.89
    primary_metric: str = 'dns_launch_probability'
    dns_launch_probability: float = 0.88
    certificates_ingested: int = 12500
    high_entropy_domains_detected: int = 14
    notable_pre_launch_signals: List[Dict[str, Any]] = Field(default_factory=list)
    agent_readable_summary: str = 'High-entropy certificate issuances detected indicating imminent product/infrastructure launch.'

class SpatialTensorResponse(BaseModel):
    """Authoritative response schema for multi-domain H3 spatial tensor synthesis."""
    timestamp: str = Field(default_factory=_utc_now_str)
    status: str = 'healthy'
    score: float = 84.0
    classification: str = 'NOMINAL'
    confidence: float = 0.93
    primary_metric: str = 'tensor_fusion_index'
    h3_index: str = '83754effffffffff'
    resolution: int = 3
    orbital_density: float = 1.2
    air_traffic_congestion: float = 65.0
    maritime_trade_volume: float = 320.0
    dns_launch_probability: float = 0.45
    composite_intelligence_score: float = 84.0
    agent_readable_summary: str = 'Unified H3 spatial tensor evaluated successfully across space, air, sea, and network vectors.'