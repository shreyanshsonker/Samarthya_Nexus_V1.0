"""
E6.7 — Model Registry
Manages versioned model files and symlinks for ARIMA + LSTM.
Logs training metrics to InfluxDB.
"""

import logging
import os
import pickle
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from app.config import settings
from app.db.influxdb_client import influx_db

logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))


class ModelRegistry:
    """
    Manages the backend/models/ directory:
      - arima_{timestamp}.pkl
      - lstm_{timestamp}.h5
      - current_arima  → symlink to latest ARIMA pickle
      - current_lstm   → symlink to latest LSTM h5
    """

    def __init__(self):
        # Resolve models dir relative to backend/
        self.models_dir = Path(settings.ML_MODELS_DIR).resolve()
        if not self.models_dir.is_absolute():
            # Fallback: relative to the working directory
            self.models_dir = Path.cwd() / settings.ML_MODELS_DIR
        self.models_dir.mkdir(parents=True, exist_ok=True)

    # ── Save ────────────────────────────────────────────────────────────

    def save_arima(self, model: Any) -> Path:
        """Pickle the ARIMA model with a timestamp filename."""
        ts = datetime.now(IST).strftime("%Y%m%d_%H%M%S")
        path = self.models_dir / f"arima_{ts}.pkl"
        with open(path, "wb") as f:
            pickle.dump(model, f)
        self._update_symlink("current_arima", path)
        logger.info(f"Saved ARIMA model → {path.name}")
        return path

    def save_lstm(self, model: Any) -> Path:
        """Save the Keras LSTM model with a timestamp filename."""
        ts = datetime.now(IST).strftime("%Y%m%d_%H%M%S")
        path = self.models_dir / f"lstm_{ts}.h5"
        model.save(str(path))
        self._update_symlink("current_lstm", path)
        logger.info(f"Saved LSTM model → {path.name}")
        return path

    # ── Load ────────────────────────────────────────────────────────────

    def load_current_arima(self) -> Optional[Any]:
        """Load the ARIMA model pointed to by current_arima symlink."""
        link = self.models_dir / "current_arima"
        if not link.exists():
            logger.warning("No current_arima symlink found.")
            return None
        target = link.resolve()
        with open(target, "rb") as f:
            return pickle.load(f)

    def load_current_lstm(self) -> Optional[Any]:
        """Load the Keras LSTM model pointed to by current_lstm symlink."""
        link = self.models_dir / "current_lstm"
        if not link.exists():
            logger.warning("No current_lstm symlink found.")
            return None
        target = link.resolve()
        try:
            from tensorflow.keras.models import load_model
            return load_model(str(target))
        except Exception as e:
            logger.error(f"Failed to load LSTM model: {e}")
            return None

    def load_current_models(self) -> Tuple[Optional[Any], Optional[Any]]:
        """Convenience: returns (arima_model, lstm_model)."""
        return self.load_current_arima(), self.load_current_lstm()

    # ── Metrics ─────────────────────────────────────────────────────────

    async def log_training_metrics(self, metrics: Dict[str, float]):
        """
        Logs training run metrics to InfluxDB ml_predictions measurement.
        Metrics dict should include: mae, val_loss, data_points.
        """
        if not influx_db.write_api:
            logger.warning("InfluxDB write_api unavailable — skipping metric log.")
            return

        try:
            point = {
                "measurement": "ml_training_runs",
                "tags": {"model_version": datetime.now(IST).strftime("%Y%m%d_%H%M%S")},
                "fields": {
                    "mae": float(metrics.get("mae", 0)),
                    "val_loss": float(metrics.get("val_loss", 0)),
                    "data_points": int(metrics.get("data_points", 0)),
                },
                "time": datetime.now(IST).isoformat(),
            }
            await influx_db.write_api.write(bucket=influx_db.bucket, record=point)
            logger.info(f"Logged training metrics: MAE={metrics.get('mae', '?')}")
        except Exception as e:
            logger.error(f"Failed to log training metrics: {e}")

    # ── Internal ────────────────────────────────────────────────────────

    def _update_symlink(self, link_name: str, target: Path):
        """Atomically update a symlink in the models directory."""
        link_path = self.models_dir / link_name
        tmp_link = self.models_dir / f".tmp_{link_name}"
        try:
            if tmp_link.exists() or tmp_link.is_symlink():
                tmp_link.unlink()
            os.symlink(target, tmp_link)
            os.replace(tmp_link, link_path)
        except Exception as e:
            logger.error(f"Failed to update symlink {link_name}: {e}")


model_registry = ModelRegistry()
