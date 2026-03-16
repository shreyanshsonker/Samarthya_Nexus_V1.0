"""
E6.1 — ML Data Preparation Module
Queries InfluxDB for historical energy_readings, preprocesses for ARIMA-LSTM pipeline.
Generates synthetic 30-day mock data when InfluxDB is empty (bootstrap mode).
"""

import logging
import math
import random
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.stattools import adfuller

from app.db.influxdb_client import influx_db

logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

# ── Synthetic Data Generator (bootstrap / dev mode) ────────────────────────

def generate_mock_solar_series(days: int = 30, capacity_kw: float = 3.0) -> pd.DataFrame:
    """
    Generates `days` worth of 15-min bell-curve solar data for Gwalior (lat 26.2°N).
    Returns a DataFrame indexed by datetime with column 'solar_kw'.
    """
    random.seed(42)  # Fixed seed for reproducibility per SAD §2.2
    np.random.seed(42)

    end = datetime.now(tz=IST).replace(second=0, microsecond=0)
    # Round down to nearest 15-min
    end = end.replace(minute=(end.minute // 15) * 15)
    start = end - timedelta(days=days)

    timestamps = pd.date_range(start=start, end=end, freq="15min", tz=IST)
    values: List[float] = []

    for ts in timestamps:
        hour = ts.hour + ts.minute / 60.0
        if hour < 6.0 or hour > 18.0:
            values.append(0.0)
        else:
            mean = 13.0
            std_dev = 2.5
            base = capacity_kw * math.exp(-0.5 * ((hour - mean) / std_dev) ** 2)
            # Day-to-day cloud variation
            noise = random.uniform(0.85, 1.0)
            values.append(round(base * noise, 3))

    df = pd.DataFrame({"solar_kw": values}, index=timestamps)
    df.index.name = "timestamp"
    return df


# ── InfluxDB Query ──────────────────────────────────────────────────────────

async def query_influxdb_solar(days: int = 30) -> Optional[pd.DataFrame]:
    """
    Queries the last `days` of solar_kw from InfluxDB energy_readings measurement.
    Returns a DataFrame indexed by datetime, or None on failure.
    """
    if not influx_db.query_api:
        logger.warning("InfluxDB query_api not available.")
        return None

    try:
        flux_query = f"""
        from(bucket: "{influx_db.bucket}")
          |> range(start: -{days}d)
          |> filter(fn: (r) => r._measurement == "energy_readings")
          |> filter(fn: (r) => r._field == "solar_kw")
          |> sort(columns: ["_time"])
        """
        tables = await influx_db.query_api.query(flux_query)

        records = []
        for table in tables:
            for record in table.records:
                records.append({
                    "timestamp": record.get_time(),
                    "solar_kw": float(record.get_value()),
                })

        if not records:
            logger.info("InfluxDB returned 0 records — will use mock data.")
            return None

        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).dt.tz_convert(IST)
        df = df.set_index("timestamp").sort_index()
        return df

    except Exception as e:
        logger.error(f"InfluxDB solar query failed: {e}")
        return None


# ── Preprocessing ───────────────────────────────────────────────────────────

def preprocess_solar_series(df: pd.DataFrame) -> Tuple[pd.DataFrame, MinMaxScaler]:
    """
    Full preprocessing pipeline:
    1. Resample to 15-min intervals with forward-fill
    2. Flag outliers (3σ from rolling mean)
    3. ADF stationarity test (log only — differencing handled by ARIMA)
    4. MinMaxScaler normalization
    Returns (processed_df, fitted_scaler).
    """
    # 1. Resample to strict 15-min grid + forward-fill gaps
    df = df.resample("15min").mean()
    df = df.ffill().bfill()  # bfill for leading NaNs if any

    # 2. Outlier flagging (3σ clip)
    rolling_mean = df["solar_kw"].rolling(window=8, min_periods=1).mean()
    rolling_std = df["solar_kw"].rolling(window=8, min_periods=1).std().fillna(0)
    upper = rolling_mean + 3 * rolling_std
    lower = (rolling_mean - 3 * rolling_std).clip(lower=0)
    df["solar_kw"] = df["solar_kw"].clip(lower=lower, upper=upper)

    # 3. ADF stationarity test (informational)
    try:
        adf_result = adfuller(df["solar_kw"].dropna(), autolag="AIC")
        p_value = adf_result[1]
        logger.info(f"ADF test p-value: {p_value:.4f} — {'stationary' if p_value <= 0.05 else 'non-stationary (ARIMA will difference)'}")
    except Exception as e:
        logger.warning(f"ADF test skipped: {e}")

    # 4. MinMaxScaler normalization
    scaler = MinMaxScaler(feature_range=(0, 1))
    df["solar_kw_scaled"] = scaler.fit_transform(df[["solar_kw"]])

    return df, scaler


# ── Public API ──────────────────────────────────────────────────────────────

async def prepare_training_data(days: int = 30) -> Tuple[pd.DataFrame, MinMaxScaler]:
    """
    High-level entry point: fetch data (InfluxDB or mock), preprocess, return.
    """
    df = await query_influxdb_solar(days)
    if df is None or len(df) < 96:  # Need at least 24h of data
        logger.info("Using synthetic mock data for ML training (bootstrap mode).")
        df = generate_mock_solar_series(days)

    df, scaler = preprocess_solar_series(df)
    logger.info(f"Prepared {len(df)} data points for training ({df.index.min()} → {df.index.max()}).")
    return df, scaler
