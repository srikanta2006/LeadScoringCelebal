"""
app.py — Main FastAPI application for the X Education Lead Scoring API.

Endpoints
---------
GET  /                        Redirect to /docs
GET  /health                  Health check
GET  /api/model/info          Model metadata
POST /api/score/single        Score one lead
POST /api/score/batch         Score up to 500 leads at once
POST /api/score/upload        Upload a CSV file and score all leads
GET  /api/analytics/summary   Aggregate stats (in-memory, resets on restart)

Run with:  python run.py
Docs at:   http://localhost:8000/docs
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timezone
from io import BytesIO
from typing import List

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

import config as cfg
from model_loader import get_model
from schemas import (
    AnalyticsSummary,
    BatchLeadScoreRequest,
    BatchLeadScoreResponse,
    LeadFeatures,
    LeadScore,
    ModelInfo,
    TierSummary,
)
from scorer import calculate_score, lead_to_feature_vector

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ── In-memory analytics store (resets on server restart) ──────────────────────
_analytics: dict = defaultdict(int)          # tier → count
_source_counts: dict   = defaultdict(int)
_spec_counts: dict     = defaultdict(int)     # specialization
_city_counts: dict     = defaultdict(int)
_score_sum: float = 0.0
_total_scored: int = 0


def _record_analytics(score_result: LeadScore, lead: LeadFeatures) -> None:
    global _score_sum, _total_scored
    _analytics[score_result.tier.lower()] += 1
    _source_counts[lead.lead_source or "Unknown"] += 1
    _spec_counts[lead.specialization or "Unknown"] += 1
    _city_counts[lead.city or "Unknown"] += 1
    _score_sum += score_result.score
    _total_scored += 1


# ── App factory ────────────────────────────────────────────────────────────────

app = FastAPI(
    title=cfg.APP_TITLE,
    description=cfg.APP_DESCRIPTION,
    version=cfg.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Restrict to your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Core scoring helper ────────────────────────────────────────────────────────

def _score_single_lead(lead: LeadFeatures) -> LeadScore:
    """Run the full scoring pipeline for one LeadFeatures object."""
    model   = get_model()
    features = lead_to_feature_vector(lead, model.feature_names)
    probability = model.predict_proba(features)
    score, tier, action = calculate_score(
        probability=probability,
        country=lead.country or "India",
    )
    return LeadScore(
        prospect_id=lead.prospect_id,
        score=score,
        tier=tier,
        probability=round(probability, 4),
        confidence=round(probability, 4),
        recommended_action=action,
        predicted_at=datetime.now(timezone.utc).isoformat(),
        model_mode=model.mode,
        lead_source=lead.lead_source,
        country=lead.country,
        city=lead.city,
        specialization=lead.specialization,
    )


def _tier_summary(tier: str, total: int) -> TierSummary:
    count = _analytics.get(tier.lower(), 0)
    pct = round(count / total * 100, 1) if total > 0 else 0.0
    return TierSummary(count=count, percentage=pct)


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get(
    "/health",
    summary="Health check",
    tags=["System"],
)
async def health_check():
    model = get_model()
    return {
        "status": "healthy",
        "model_mode": model.mode,
        "app_version": cfg.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get(
    "/api/model/info",
    response_model=ModelInfo,
    summary="Model metadata",
    tags=["System"],
)
async def model_info():
    model = get_model()
    return ModelInfo(
        model_type=cfg.MODEL_TYPE,
        version=cfg.MODEL_VERSION,
        mode=model.mode,
        num_features=model.num_features,
        features_preview=model.feature_names[:10],
        test_auc=cfg.REPORTED_TEST_AUC,
        training_date=cfg.TRAINING_DATE,
    )


@app.post(
    "/api/score/single",
    response_model=LeadScore,
    summary="Score a single lead",
    tags=["Scoring"],
    status_code=status.HTTP_200_OK,
)
async def score_single(lead: LeadFeatures):
    """
    Submit one lead's features and receive a score (0-100), tier, and
    recommended sales action.
    """
    try:
        result = _score_single_lead(lead)
        _record_analytics(result, lead)
        return result
    except Exception as exc:
        logger.exception("Error scoring lead %s", lead.email)
        raise HTTPException(status_code=400, detail=str(exc))


@app.post(
    "/api/score/batch",
    response_model=BatchLeadScoreResponse,
    summary="Score multiple leads at once (max 500)",
    tags=["Scoring"],
    status_code=status.HTTP_200_OK,
)
async def score_batch(request: BatchLeadScoreRequest):
    """
    Submit a list of leads (up to 500) and receive scores for all of them,
    along with a tier-breakdown summary.
    """
    scores: List[LeadScore] = []
    try:
        for lead in request.leads:
            result = _score_single_lead(lead)
            _record_analytics(result, lead)
            scores.append(result)
    except Exception as exc:
        logger.exception("Error in batch scoring")
        raise HTTPException(status_code=400, detail=str(exc))

    total = len(scores)
    avg_score = round(sum(s.score for s in scores) / total, 2) if total else 0.0

    tier_counts: dict[str, int] = defaultdict(int)
    for s in scores:
        tier_counts[s.tier] += 1

    def _local_summary(tier: str) -> TierSummary:
        c = tier_counts.get(tier, 0)
        return TierSummary(count=c, percentage=round(c / total * 100, 1) if total else 0.0)

    return BatchLeadScoreResponse(
        scores=scores,
        total_processed=total,
        hot=_local_summary("Hot"),
        warm=_local_summary("Warm"),
        cold=_local_summary("Cold"),
        frozen=_local_summary("Frozen"),
        average_score=avg_score,
        processed_at=datetime.now(timezone.utc).isoformat(),
    )


@app.post(
    "/api/score/upload",
    summary="Upload a CSV file and score all leads",
    tags=["Scoring"],
)
async def upload_and_score(file: UploadFile = File(...)):
    """
    Upload a CSV whose columns match the `LeadFeatures` schema.
    Returns scored results directly in the response.

    **Required CSV columns:**
    `email, name, company, industry, country, page_views, time_spent_minutes,
    email_opened, clicked_link, form_submitted, last_activity_days_ago, source`
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted.")

    contents = await file.read()
    try:
        df = pd.read_csv(BytesIO(contents))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {exc}")

    # Normalise column headers: lowercase + strip spaces
    df.columns = df.columns.str.strip().str.lower()

    # Required columns from the X Education dataset
    required_cols = {
        "totalvisits",
        "total time spent on website",
        "page views per visit",
    }
    missing = required_cols - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"CSV is missing required columns: {sorted(missing)}",
        )

    # Column rename map: raw CSV name → LeadFeatures field name
    rename_map = {
        "totalvisits":                          "total_visits",
        "total time spent on website":          "total_time_spent_on_website",
        "page views per visit":                 "page_views_per_visit",
        "lead origin":                          "lead_origin",
        "lead source":                          "lead_source",
        "do not email":                         "do_not_email",
        "do not call":                          "do_not_call",
        "last activity":                        "last_activity",
        "last notable activity":                "last_notable_activity",
        "how did you hear about x education":   "how_heard",
        "what is your current occupation":      "current_occupation",
        "what matters most to you in choosing a course": "what_matters_most",
        "newspaper article":                    "newspaper_article",
        "x education forums":                   "x_education_forums",
        "digital advertisement":                "digital_advertisement",
        "through recommendations":              "through_recommendations",
        "receive more updates about our courses": "receive_more_updates",
        "update me on supply chain content":    "update_supply_chain",
        "get updates on dm content":            "get_dm_updates",
        "lead profile":                         "lead_profile",
        "lead quality":                         "lead_quality",
        "asymmetrique activity index":          "asymmetrique_activity_index",
        "asymmetrique profile index":           "asymmetrique_profile_index",
        "asymmetrique activity score":          "asymmetrique_activity_score",
        "asymmetrique profile score":           "asymmetrique_profile_score",
        "a free copy of mastering the interview": "a_free_copy_of_mastering_the_interview",
    }
    df.rename(columns=rename_map, inplace=True)

    # Safe defaults for optional fields
    for col, default in [
        ("country", "India"), ("city", None), ("specialization", None),
        ("lead_origin", None), ("lead_source", None),
        ("do_not_email", "No"), ("do_not_call", "No"),
        ("last_activity", None), ("last_notable_activity", None),
        ("current_occupation", None), ("what_matters_most", None),
        ("tags", None), ("lead_quality", None), ("lead_profile", None),
        ("asymmetrique_activity_index", "02.Medium"),
        ("asymmetrique_profile_index",  "02.Medium"),
        ("asymmetrique_activity_score", 15.0),
        ("asymmetrique_profile_score",  15.0),
        ("a_free_copy_of_mastering_the_interview", "No"),
    ]:
        if col not in df.columns:
            df[col] = default
        else:
            df[col] = df[col].fillna(default) if default is not None else df[col]

    scored_rows = []
    errors: list[str] = []
    for idx, row in df.iterrows():
        try:
            lead = LeadFeatures(
                prospect_id=str(row.get("prospect id", "")) or None,
                lead_origin=str(row.get("lead_origin", "")) or None,
                lead_source=str(row.get("lead_source", "")) or None,
                total_visits=float(row.get("total_visits", 0) or 0),
                total_time_spent_on_website=float(row.get("total_time_spent_on_website", 0) or 0),
                page_views_per_visit=float(row.get("page_views_per_visit", 0) or 0),
                last_activity=str(row.get("last_activity", "")) or None,
                last_notable_activity=str(row.get("last_notable_activity", "")) or None,
                country=str(row.get("country", "India") or "India"),
                city=str(row.get("city", "")) or None,
                specialization=str(row.get("specialization", "")) or None,
                current_occupation=str(row.get("current_occupation", "")) or None,
                what_matters_most=str(row.get("what_matters_most", "")) or None,
                do_not_email=str(row.get("do_not_email", "No") or "No"),
                do_not_call=str(row.get("do_not_call", "No") or "No"),
                tags=str(row.get("tags", "")) or None,
                lead_quality=str(row.get("lead_quality", "")) or None,
                lead_profile=str(row.get("lead_profile", "")) or None,
                asymmetrique_activity_index=str(row.get("asymmetrique_activity_index", "02.Medium") or "02.Medium"),
                asymmetrique_profile_index=str(row.get("asymmetrique_profile_index", "02.Medium") or "02.Medium"),
                asymmetrique_activity_score=float(row.get("asymmetrique_activity_score", 15) or 15),
                asymmetrique_profile_score=float(row.get("asymmetrique_profile_score", 15) or 15),
                a_free_copy_of_mastering_the_interview=str(row.get("a_free_copy_of_mastering_the_interview", "No") or "No"),
            )
            result = _score_single_lead(lead)
            _record_analytics(result, lead)
            scored_rows.append(result.model_dump())
        except Exception as exc:
            errors.append(f"Row {idx}: {exc}")

    return {
        "message": "Batch scoring completed.",
        "total_leads": len(df),
        "scored_successfully": len(scored_rows),
        "errors": errors[:20],
        "results": scored_rows,
    }


@app.get(
    "/api/analytics/summary",
    response_model=AnalyticsSummary,
    summary="Aggregate scoring analytics (in-memory)",
    tags=["Analytics"],
)
async def analytics_summary():
    """
    Returns aggregate stats about all leads scored since the server started.
    Resets on server restart (no persistence layer yet).
    """
    total = _total_scored or 1   # avoid division by zero

    top_sources = sorted(
        [{"source": k, "count": v} for k, v in _source_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:10]

    top_specializations = sorted(
        [{"specialization": k, "count": v} for k, v in _spec_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:10]

    top_cities = sorted(
        [{"city": k, "count": v} for k, v in _city_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:10]

    return AnalyticsSummary(
        total_leads_scored=_total_scored,
        hot_count=_analytics.get("hot", 0),
        warm_count=_analytics.get("warm", 0),
        cold_count=_analytics.get("cold", 0),
        frozen_count=_analytics.get("frozen", 0),
        average_score=round(_score_sum / total, 2),
        top_sources=top_sources,
        top_specializations=top_specializations,
        top_cities=top_cities,
        model_mode=get_model().mode,
    )
