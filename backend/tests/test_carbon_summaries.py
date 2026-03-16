import pytest
from unittest.mock import AsyncMock, patch
from app.services.carbon_service import carbon_service

@pytest.mark.asyncio
async def test_get_daily_summary_logic():
    household_id = "test-household"
    
    # Mock InfluxDB response
    mock_record_solar = AsyncMock()
    mock_record_solar.get_field.return_value = "solar_kw"
    mock_record_solar.get_value.return_value = 10.0 # 10.0 * 0.25 = 2.5 kWh
    
    mock_record_cons = AsyncMock()
    mock_record_cons.get_field.return_value = "consumption_kw"
    mock_record_cons.get_value.return_value = 20.0 # 20.0 * 0.25 = 5.0 kWh
    
    mock_table = AsyncMock()
    mock_table.records = [mock_record_solar, mock_record_cons]
    
    with patch("app.db.influxdb_client.influx_db.query_api.query", return_value=[mock_table]):
        summary = await carbon_service.get_daily_summary(household_id)
        
        assert summary["solar_kwh"] == 2.5
        assert summary["consumption_kwh"] == 5.0
        assert summary["saved_kg"] > 0

@pytest.mark.asyncio
async def test_get_weekly_summary_logic():
    household_id = "test-household"
    
    # Simple mock response
    with patch("app.db.influxdb_client.influx_db.query_api.query", return_value=[]):
        summary = await carbon_service.get_weekly_summary(household_id)
        assert isinstance(summary, list)
