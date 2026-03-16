"""
E6.5 — SHAP Explainability Module
Wraps SHAP DeepExplainer around the LSTM model to produce top-3 feature importances.
"""

import logging
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

# Human-readable feature mapping (SAD §5.3)
FEATURE_NAME_MAP = {
    0: {"raw": "solar_kw_t-1", "label": "Solar generation 15 min ago"},
    1: {"raw": "solar_kw_t-2", "label": "Solar generation 30 min ago"},
    2: {"raw": "solar_kw_t-3", "label": "Solar generation 45 min ago"},
    3: {"raw": "solar_kw_t-4", "label": "Solar generation 1 hour ago"},
    4: {"raw": "solar_kw_t-8", "label": "Solar generation 2 hours ago"},
    5: {"raw": "solar_kw_t-12", "label": "Solar generation 3 hours ago"},
}


def compute_shap_explanations(
    lstm_model: Any,
    input_data: np.ndarray,
    background_data: Optional[np.ndarray] = None,
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """
    Compute SHAP values for LSTM inference and return top-k feature importances.

    Args:
        lstm_model: Trained Keras LSTM model.
        input_data: np.ndarray of shape (1, 96, 1) — the inference input.
        background_data: np.ndarray of shape (n, 96, 1) — background samples
                         for DeepExplainer. If None, uses a zero baseline.
        top_k: Number of top features to return.

    Returns:
        List of dicts: [{"feature": str, "label": str, "importance": float}, ...]
    """
    try:
        import shap

        if background_data is None:
            # Use a single zero-baseline as background
            background_data = np.zeros((1, input_data.shape[1], 1))

        explainer = shap.DeepExplainer(lstm_model, background_data)
        shap_values = explainer.shap_values(input_data)

        # shap_values may be a list (one per output neuron) — aggregate
        if isinstance(shap_values, list):
            # Average across all output steps
            sv = np.mean([np.abs(s) for s in shap_values], axis=0)
        else:
            sv = np.abs(shap_values)

        # sv shape: (1, 96, 1) — squeeze to (96,)
        feature_importance = sv.squeeze()

        # Get indices of top-k most important time steps
        top_indices = np.argsort(feature_importance)[-top_k:][::-1]

        explanations: List[Dict[str, Any]] = []
        for idx in top_indices:
            # Map time step index to human-readable name
            steps_ago = 96 - int(idx)  # how many steps back from most recent
            mapped = FEATURE_NAME_MAP.get(steps_ago - 1, None)

            if mapped:
                feature_name = mapped["raw"]
                label = mapped["label"]
            else:
                feature_name = f"solar_kw_t-{steps_ago}"
                label = f"Solar generation {steps_ago * 15} min ago"

            explanations.append({
                "feature": feature_name,
                "label": label,
                "importance": round(float(feature_importance[idx]), 4),
            })

        logger.info(f"SHAP top-{top_k}: {[(e['feature'], e['importance']) for e in explanations]}")
        return explanations

    except ImportError:
        logger.warning("SHAP library not available — returning empty explanations.")
        return []
    except Exception as e:
        logger.warning(f"SHAP computation failed (non-critical): {e}")
        return []
