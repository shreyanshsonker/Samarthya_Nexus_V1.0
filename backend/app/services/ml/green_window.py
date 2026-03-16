"""
E6.8 — Green Window Detection
Sliding 2-hour window over 16-step forecast to find optimal solar utilization window.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.utils.constants import GRID_INTENSITY_MP_FALLBACK

logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

# 2-hour window = 8 × 15-min steps
WINDOW_STEPS = 8
STEP_MINUTES = 15


def detect_green_window(
    forecast: List[Dict[str, Any]],
    avg_consumption_kw: float = 1.5,
) -> Optional[Dict[str, Any]]:
    """
    Finds the optimal 2-hour Green Window within the 4-hour forecast horizon.

    Algorithm (per PRD §6.4 FR-GW-02):
      For each possible 2-hour window position:
        Score = Σ(predicted_solar - estimated_consumption)
      The window with the highest score is the Green Window.

    Args:
        forecast: List of 16 dicts with keys: timestamp, predicted_kw, lower, upper.
        avg_consumption_kw: Estimated average household consumption (default 1.5 kW).

    Returns:
        Dict with: start, end, avg_kw, saving_kg, recommendation — or None if no valid window.
    """
    if not forecast or len(forecast) < WINDOW_STEPS:
        logger.warning(f"Forecast has {len(forecast) if forecast else 0} steps — need ≥ {WINDOW_STEPS}.")
        return None

    best_score = float("-inf")
    best_start_idx = 0

    num_positions = len(forecast) - WINDOW_STEPS + 1

    for i in range(num_positions):
        window = forecast[i: i + WINDOW_STEPS]
        score = sum(step["predicted_kw"] - avg_consumption_kw for step in window)

        if score > best_score:
            best_score = score
            best_start_idx = i

    # Build output
    best_window = forecast[best_start_idx: best_start_idx + WINDOW_STEPS]
    avg_solar_kw = sum(s["predicted_kw"] for s in best_window) / WINDOW_STEPS

    # CO₂ saving calculation:
    # During Green Window, solar surplus avoids grid import.
    # saving = avg_surplus_kw × window_hours × grid_intensity
    avg_surplus = max(0, avg_solar_kw - avg_consumption_kw)
    window_hours = (WINDOW_STEPS * STEP_MINUTES) / 60.0  # 2 hours
    saving_kg = round(avg_surplus * window_hours * GRID_INTENSITY_MP_FALLBACK, 3)

    start_time = best_window[0]["timestamp"]
    end_time_dt = datetime.fromisoformat(best_window[-1]["timestamp"]) + timedelta(minutes=STEP_MINUTES)
    end_time = end_time_dt.isoformat()

    # Generate human-readable recommendation
    if avg_surplus > 0:
        recommendation = (
            f"Run high-power appliances between "
            f"{datetime.fromisoformat(start_time).strftime('%I:%M %p')} and "
            f"{end_time_dt.strftime('%I:%M %p')} "
            f"to maximize your solar energy usage and save ~{saving_kg} kg CO₂."
        )
    else:
        recommendation = (
            "Solar generation is lower than consumption in all windows. "
            "Consider reducing non-essential load during this period."
        )

    result = {
        "window": {
            "start": start_time,
            "end": end_time,
            "avg_kw": round(avg_solar_kw, 3),
            "saving_kg": saving_kg,
        },
        "recommendation": recommendation,
    }

    logger.info(f"Green Window: {start_time} → {end_time}, avg solar: {avg_solar_kw:.2f} kW, saving: {saving_kg} kg CO₂")
    return result
