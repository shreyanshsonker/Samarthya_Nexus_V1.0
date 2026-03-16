"""
E6.3 — LSTM Training Module
2-layer LSTM for residual correction on ARIMA output.
Architecture: LSTM(64) → Dropout(0.2) → LSTM(32) → Dropout(0.2) → Dense(16)
"""

import logging
from typing import Dict, Optional, Tuple

import numpy as np

from app.services.ml.model_registry import model_registry

logger = logging.getLogger(__name__)

# ── Constants per SAD §5.1 / AI Rules §4 ────────────────────────────────────
INPUT_STEPS = 96    # 24 hours of 15-min intervals
OUTPUT_STEPS = 16   # 4 hours of 15-min intervals
LSTM_UNITS_1 = 64
LSTM_UNITS_2 = 32
DROPOUT_RATE = 0.2
LEARNING_RATE = 0.001
PATIENCE = 10
EPOCHS = 100
BATCH_SIZE = 32


def build_lstm_model():
    """
    Builds the 2-layer LSTM model per the SAD specification.
    Input:  (batch, 96, 1)
    Output: (batch, 16)
    """
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dropout, Dense
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.losses import Huber

    model = Sequential([
        LSTM(LSTM_UNITS_1, return_sequences=True, input_shape=(INPUT_STEPS, 1)),
        Dropout(DROPOUT_RATE),
        LSTM(LSTM_UNITS_2, return_sequences=False),
        Dropout(DROPOUT_RATE),
        Dense(OUTPUT_STEPS),
    ])

    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss=Huber(),
        metrics=["mae"],
    )

    return model


def create_sequences(data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Creates sliding-window sequences from the 1D residuals array.

    Args:
        data: 1D numpy array of scaled residuals.

    Returns:
        (X, y) where X has shape (n_samples, 96, 1) and y has shape (n_samples, 16).
    """
    X, y = [], []
    total_window = INPUT_STEPS + OUTPUT_STEPS  # 96 + 16 = 112

    for i in range(len(data) - total_window + 1):
        X.append(data[i: i + INPUT_STEPS])
        y.append(data[i + INPUT_STEPS: i + total_window])

    X = np.array(X).reshape(-1, INPUT_STEPS, 1)
    y = np.array(y)
    return X, y


def train_lstm(
    scaled_residuals: np.ndarray,
) -> Tuple[Optional[object], Dict[str, float]]:
    """
    Trains the LSTM on scaled residuals with 80/20 train/val split.

    Args:
        scaled_residuals: 1D array of MinMaxScaler-normalized ARIMA residuals.

    Returns:
        (trained_model, metrics_dict) — metrics include val_loss, mae.
    """
    from tensorflow.keras.callbacks import EarlyStopping

    metrics: Dict[str, float] = {"val_loss": 0.0, "mae": 0.0, "data_points": len(scaled_residuals)}

    try:
        if len(scaled_residuals) < INPUT_STEPS + OUTPUT_STEPS + 10:
            logger.error(f"Insufficient residual data ({len(scaled_residuals)} points). Need ≥ {INPUT_STEPS + OUTPUT_STEPS + 10}.")
            return None, metrics

        X, y = create_sequences(scaled_residuals)

        if len(X) == 0:
            logger.error("No training sequences could be created from residuals.")
            return None, metrics

        # 80/20 split
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]

        logger.info(
            f"LSTM training: {len(X_train)} train / {len(X_val)} val sequences "
            f"(input: {INPUT_STEPS}×1, output: {OUTPUT_STEPS})"
        )

        model = build_lstm_model()

        early_stop = EarlyStopping(
            monitor="val_loss",
            patience=PATIENCE,
            restore_best_weights=True,
            verbose=1,
        )

        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            callbacks=[early_stop],
            verbose=0,
        )

        # Extract final metrics
        best_epoch = early_stop.stopped_epoch - PATIENCE if early_stop.stopped_epoch > 0 else len(history.history["val_loss"]) - 1
        best_epoch = max(0, best_epoch)
        metrics["val_loss"] = round(float(history.history["val_loss"][best_epoch]), 4)
        metrics["mae"] = round(float(history.history["val_mae"][best_epoch]), 4)

        logger.info(f"LSTM trained — val_loss: {metrics['val_loss']}, MAE: {metrics['mae']}")

        # Save via registry
        model_registry.save_lstm(model)

        return model, metrics

    except Exception as e:
        logger.error(f"LSTM training failed: {e}")
        return None, metrics


def predict_lstm(model: object, recent_residuals: np.ndarray) -> Optional[np.ndarray]:
    """
    Runs LSTM inference on the most recent 96 scaled residual values.

    Args:
        model: Trained Keras LSTM model.
        recent_residuals: 1D array of shape (96,) with scaled residuals.

    Returns:
        np.ndarray of shape (16,) — the residual corrections (still scaled).
    """
    try:
        if len(recent_residuals) < INPUT_STEPS:
            logger.error(f"Need {INPUT_STEPS} residual points, got {len(recent_residuals)}.")
            return None

        # Take last 96 entries
        input_data = recent_residuals[-INPUT_STEPS:].reshape(1, INPUT_STEPS, 1)
        prediction = model.predict(input_data, verbose=0)
        return prediction.flatten()

    except Exception as e:
        logger.error(f"LSTM prediction failed: {e}")
        return None
