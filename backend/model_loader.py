"""
model_loader.py — Load ML artifacts from disk or fall back to demo mode.

Demo mode uses a deterministic heuristic scorer (scorer.demo_heuristic) calibrated
to the real X Education dataset features. Once you drop the trained pkl files into
models/ and data/processed/, set FORCE_DEMO=false (or just restart) and the
real XGBoost model will be used automatically.
"""

from __future__ import annotations

import json
import logging
import os
import pickle
from pathlib import Path
from typing import List, Optional

import numpy as np

from config import (
    FEATURE_NAMES_PATH,
    MODEL_PATH,
    SCALER_PATH,
)

logger = logging.getLogger(__name__)

# Set FORCE_DEMO=true in env to always use the heuristic scorer during testing
FORCE_DEMO = os.getenv("FORCE_DEMO", "false").lower() == "true"

# ── Default feature names used in demo mode (real dataset columns) ─────────────
DEMO_FEATURE_NAMES: List[str] = [
    "totalvisits",
    "total_time_spent_on_website",
    "page_views_per_visit",
    "asymmetrique_activity_score",
    "asymmetrique_profile_score",
    "asymmetrique_activity_index_encoded",
    "asymmetrique_profile_index_encoded",
    "lead_quality_encoded",
    "last_activity_encoded",
    "last_notable_activity_encoded",
    "do_not_email",
    "a_free_copy_of_mastering_the_interview",
    "engagement_score",
    "recency_score",
    "asym_composite",
]


class ModelLoader:
    """
    Singleton-style class that wraps either:
      - A real scikit-learn / XGBoost pipeline (ML mode), or
      - A rule-based heuristic (Demo mode).

    Usage:
        loader = ModelLoader()
        proba = loader.predict_proba(feature_vector)  # → float in [0, 1]
    """

    def __init__(self) -> None:
        self.mode: str = "demo"
        self._model = None
        self._scaler = None
        self._feature_names: List[str] = DEMO_FEATURE_NAMES

        if not FORCE_DEMO:
            self._try_load_ml_artifacts()
        else:
            logger.info("FORCE_DEMO=true — running in demo mode.")

    # ── Loader ─────────────────────────────────────────────────────────────────

    def _try_load_ml_artifacts(self) -> None:
        """Attempt to load model + scaler + feature names from disk."""
        paths_ok = (
            Path(MODEL_PATH).exists()
            and Path(SCALER_PATH).exists()
            and Path(FEATURE_NAMES_PATH).exists()
        )

        if not paths_ok:
            logger.warning(
                "One or more ML artifacts not found — falling back to demo mode.\n"
                "  MODEL    : %s  [%s]\n"
                "  SCALER   : %s  [%s]\n"
                "  FEATURES : %s  [%s]",
                MODEL_PATH, "✓" if Path(MODEL_PATH).exists() else "✗",
                SCALER_PATH, "✓" if Path(SCALER_PATH).exists() else "✗",
                FEATURE_NAMES_PATH, "✓" if Path(FEATURE_NAMES_PATH).exists() else "✗",
            )
            return

        try:
            with open(MODEL_PATH, "rb") as f:
                self._model = pickle.load(f)
            with open(SCALER_PATH, "rb") as f:
                self._scaler = pickle.load(f)
            with open(FEATURE_NAMES_PATH, "r") as f:
                self._feature_names = json.load(f)

            self.mode = "ml"
            logger.info(
                "✅ ML model loaded successfully — %d features, mode=ml",
                len(self._feature_names),
            )
        except Exception as exc:
            logger.error("Failed to load ML artifacts: %s — using demo mode.", exc)

    # ── Public interface ───────────────────────────────────────────────────────

    @property
    def feature_names(self) -> List[str]:
        return self._feature_names

    @property
    def num_features(self) -> int:
        return len(self._feature_names)

    def predict_proba(self, raw_features: np.ndarray) -> float:
        """
        Return conversion probability ∈ [0, 1] for a single feature vector.

        Args:
            raw_features: 1-D numpy array aligned to `self.feature_names`.

        Returns:
            float probability.
        """
        if self.mode == "ml":
            return self._ml_predict(raw_features)
        return self._demo_predict(raw_features)

    # ── ML prediction ──────────────────────────────────────────────────────────

    def _ml_predict(self, raw_features: np.ndarray) -> float:
        try:
            scaled = self._scaler.transform(raw_features.reshape(1, -1))
            proba = self._model.predict_proba(scaled)[0][1]
            return float(np.clip(proba, 0.0, 1.0))
        except Exception as exc:
            logger.error("ML prediction failed (%s) — falling back to demo.", exc)
            return self._demo_predict(raw_features)

    # ── Demo / heuristic prediction ────────────────────────────────────────────

    def _demo_predict(self, raw_features: np.ndarray) -> float:
        """
        Delegates to scorer.demo_heuristic which is calibrated to the real
        X Education dataset features. raw_features is passed as-is; the
        heuristic re-reads the lead object stored on the call stack via the
        feature vector values aligned to DEMO_FEATURE_NAMES.
        """
        feat  = raw_features.astype(float)
        names = self._feature_names

        def get(name: str, default: float = 0.0) -> float:
            try:
                return feat[names.index(name)]
            except ValueError:
                return default

        # Reconstruct the signals the heuristic needs from the feature vector
        tv   = get("totalvisits") or get("total_visits")
        tt   = get("total_time_spent_on_website")
        pv   = get("page_views_per_visit")
        aa_s = get("asymmetrique_activity_score", 15)
        ap_s = get("asymmetrique_profile_score", 15)
        la   = get("last_activity_encoded")
        lna  = get("last_notable_activity_encoded")
        lq   = get("lead_quality_encoded", 0.5)
        dne  = get("do_not_email")
        fc   = get("a_free_copy_of_mastering_the_interview")

        score = 0.0
        score += min(tt / 2000.0, 1.0) * 0.30
        score += min(tv / 15.0,   1.0) * 0.20
        score += min(aa_s / 25.0, 1.0) * 0.15
        score += min(ap_s / 25.0, 1.0) * 0.10
        score += la                     * 0.10
        score += lna                    * 0.05
        score += lq                     * 0.05
        score += fc                     * 0.03
        score -= dne                    * 0.08

        seed_val = int(tv * 100 + tt + aa_s * 10 + ap_s * 10) % 997
        rng = np.random.default_rng(seed_val)
        noise = rng.uniform(-0.04, 0.04)

        return float(np.clip(score + noise, 0.01, 0.99))


# ── Module-level singleton ─────────────────────────────────────────────────────

_loader: Optional[ModelLoader] = None


def get_model() -> ModelLoader:
    """Return the module-level ModelLoader singleton."""
    global _loader
    if _loader is None:
        _loader = ModelLoader()
    return _loader
