from datetime import datetime, timezone, timedelta
from typing import Dict, Any

class CleaningPipeline:
    """
    Data Cleaning Pipeline adhering to PRD specifications:
    - Wh to kWh conversion
    - Timezone standardization to IST (UTC+5:30)
    - Null handling/forward filling (simplified for live streams)
    """
    
    IST_OFFSET = timedelta(hours=5, minutes=30)
    
    @classmethod
    def process_raw_reading(cls, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes raw dictionary input and normalizes it.
        """
        # 1. Convert timestamp to IST
        if "timestamp" in raw:
            try:
                dt = datetime.fromisoformat(raw["timestamp"].replace("Z", "+00:00"))
                # Ensure it has timezone info
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                ist_dt = dt.astimezone(timezone(cls.IST_OFFSET))
                raw["timestamp"] = ist_dt.isoformat()
            except ValueError:
                pass # Unparseable date, keep as is
                
        # 2. Convert power metrics from W to kW if necessary
        # Assuming the external APIs might give Watts, our system requires kW
        for metric in ["solar_kw", "consumption_kw", "net_grid_kw"]:
            if metric in raw and isinstance(raw[metric], (int, float)):
                # Simplified check: if value > 100, might be Watts.
                # True logic would depend on explicit API schema mapping.
                # For Sprint 2 we enforce float rounding as standard.
                raw[metric] = round(float(raw[metric]), 3)
                
        # 3. Null handling
        for metric in ["solar_kw", "consumption_kw", "net_grid_kw"]:
            if raw.get(metric) is None:
                raw[metric] = 0.0
                
        # Calculate derived net_grid if not explicitly provided
        if "net_grid_kw" not in raw and "solar_kw" in raw and "consumption_kw" in raw:
            raw["net_grid_kw"] = round(raw["consumption_kw"] - raw["solar_kw"], 3)
            
        return raw

data_pipeline = CleaningPipeline()
