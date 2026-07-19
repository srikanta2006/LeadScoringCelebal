"""
schemas.py — Pydantic request / response models for the Lead Scoring API.
Column names are aligned to the actual X Education dataset:
  data/raw/Lead Scoring.csv
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# ── Input ──────────────────────────────────────────────────────────────────────

class LeadFeatures(BaseModel):
    """
    Feature payload for a single lead, aligned to the X Education dataset columns.

    Numeric columns carry the values as-is from the raw CSV.
    Categorical columns accept the string values as they appear in the CSV
    (e.g. Lead Source = 'Olark Chat', 'Google', 'Organic Search', …).

    All fields that are missing in the dataset (NaN) should be passed as None;
    the backend will impute sensible defaults.
    """

    # ── Identifiers (not used for scoring, kept for traceability) ─────────────
    prospect_id: Optional[str]  = Field(default=None, description="Prospect UUID from CRM")
    lead_number: Optional[int]  = Field(default=None, description="Sequential lead number")

    # ── Acquisition ───────────────────────────────────────────────────────────
    lead_origin: Optional[str]  = Field(default=None, description="API | Landing Page Submission | Lead Add Form | …")
    lead_source: Optional[str]  = Field(default=None, description="Google | Organic Search | Direct Traffic | Olark Chat | …")

    # ── Engagement / Numeric ──────────────────────────────────────────────────
    total_visits: Optional[float]                   = Field(default=0,   ge=0, description="TotalVisits")
    total_time_spent_on_website: Optional[float]    = Field(default=0,   ge=0, description="Total Time Spent on Website (seconds)")
    page_views_per_visit: Optional[float]           = Field(default=0,   ge=0, description="Page Views Per Visit")

    # ── Activity ──────────────────────────────────────────────────────────────
    last_activity: Optional[str]         = Field(default=None, description="Email Opened | Page Visited on Website | Olark Chat Conversation | …")
    last_notable_activity: Optional[str] = Field(default=None, description="Modified | Email Opened | Page Visited on Website | …")

    # ── Demographics ──────────────────────────────────────────────────────────
    country: Optional[str]       = Field(default="India",  description="Country")
    city: Optional[str]          = Field(default=None,     description="Mumbai | Thane & Outskirts | Other Metro Cities | …")
    specialization: Optional[str]= Field(default=None,     description="Finance Management | Marketing Management | …")
    current_occupation: Optional[str] = Field(
        default=None,
        description="What is your current occupation: Unemployed | Student | Working Professional | …",
        alias="what_is_your_current_occupation",
    )
    what_matters_most: Optional[str] = Field(
        default=None,
        description="What matters most to you in choosing a course",
        alias="what_matters_most_to_you_in_choosing_a_course",
    )
    how_heard: Optional[str] = Field(
        default=None,
        description="How did you hear about X Education",
        alias="how_did_you_hear_about_x_education",
    )

    # ── Opt-out Flags ─────────────────────────────────────────────────────────
    do_not_email: Optional[str]  = Field(default="No", description="Yes | No")
    do_not_call:  Optional[str]  = Field(default="No", description="Yes | No")

    # ── Marketing Channels (Yes/No) ───────────────────────────────────────────
    search:                Optional[str] = Field(default="No")
    magazine:              Optional[str] = Field(default="No")
    newspaper_article:     Optional[str] = Field(default="No")
    x_education_forums:   Optional[str] = Field(default="No")
    newspaper:             Optional[str] = Field(default="No")
    digital_advertisement: Optional[str] = Field(default="No")
    through_recommendations: Optional[str] = Field(default="No")
    receive_more_updates:  Optional[str] = Field(default="No", alias="receive_more_updates_about_our_courses")

    # ── CRM / Qualification ───────────────────────────────────────────────────
    tags:          Optional[str] = Field(default=None, description="Interested in other courses | Ringing | Will revert …")
    lead_quality:  Optional[str] = Field(default=None, description="High in Relevance | Might be | Not Sure | Low in Relevance | Worst")
    lead_profile:  Optional[str] = Field(default=None, description="Potential Lead | Select | …")

    # ── Asymmetrique Scores ───────────────────────────────────────────────────
    asymmetrique_activity_index:  Optional[str]   = Field(default="02.Medium", description="01.High | 02.Medium | 03.Low")
    asymmetrique_profile_index:   Optional[str]   = Field(default="02.Medium", description="01.High | 02.Medium | 03.Low")
    asymmetrique_activity_score:  Optional[float] = Field(default=15.0, ge=0)
    asymmetrique_profile_score:   Optional[float] = Field(default=15.0, ge=0)

    # ── Misc ──────────────────────────────────────────────────────────────────
    a_free_copy_of_mastering_the_interview: Optional[str] = Field(default="No", description="Yes | No")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "prospect_id": "7927b2df-8bba-4d29-b9a2-b6e0beafe620",
                "lead_origin": "Landing Page Submission",
                "lead_source": "Google",
                "total_visits": 6,
                "total_time_spent_on_website": 1137,
                "page_views_per_visit": 1.5,
                "last_activity": "Email Opened",
                "last_notable_activity": "Email Opened",
                "country": "India",
                "city": "Mumbai",
                "specialization": "Marketing Management",
                "what_is_your_current_occupation": "Unemployed",
                "what_matters_most_to_you_in_choosing_a_course": "Better Career Prospects",
                "how_did_you_hear_about_x_education": "Select",
                "do_not_email": "No",
                "do_not_call": "No",
                "tags": "Will revert after reading the email",
                "lead_quality": "High in Relevance",
                "lead_profile": "Potential Lead",
                "asymmetrique_activity_index": "02.Medium",
                "asymmetrique_profile_index": "01.High",
                "asymmetrique_activity_score": 14.0,
                "asymmetrique_profile_score": 18.0,
                "a_free_copy_of_mastering_the_interview": "Yes",
            }
        },
    }


# ── Output ─────────────────────────────────────────────────────────────────────

class LeadScore(BaseModel):
    """Score result for a single lead."""

    prospect_id: Optional[str]
    score: float = Field(..., ge=0, le=100, description="Lead score on a 0-100 scale")
    tier: str    = Field(..., description="Hot | Warm | Cold | Frozen")
    probability: float = Field(..., ge=0, le=1, description="Raw model conversion probability")
    confidence:  float = Field(..., ge=0, le=1)
    recommended_action: str
    predicted_at:  str = Field(..., description="ISO-8601 UTC timestamp")
    model_mode: str    = Field(default="demo", description="'ml' or 'demo'")

    # Key input echoes (for readability in responses)
    lead_source: Optional[str]  = None
    country:     Optional[str]  = None
    city:        Optional[str]  = None
    specialization: Optional[str] = None


class TierSummary(BaseModel):
    count: int
    percentage: float


class BatchLeadScoreRequest(BaseModel):
    """Request body for batch scoring."""
    leads: List[LeadFeatures] = Field(..., min_length=1, max_length=1000)


class BatchLeadScoreResponse(BaseModel):
    """Response for batch scoring with per-lead results and aggregate summary."""
    scores: List[LeadScore]
    total_processed: int
    hot:    TierSummary
    warm:   TierSummary
    cold:   TierSummary
    frozen: TierSummary
    average_score: float
    processed_at:  str


# ── Analytics ──────────────────────────────────────────────────────────────────

class AnalyticsSummary(BaseModel):
    total_leads_scored: int
    hot_count:    int
    warm_count:   int
    cold_count:   int
    frozen_count: int
    average_score:    float
    top_sources:      List[dict]
    top_specializations: List[dict]
    top_cities:       List[dict]
    model_mode:       str


# ── Model Info ─────────────────────────────────────────────────────────────────

class ModelInfo(BaseModel):
    model_type:       str
    version:          str
    mode:             str
    num_features:     int
    features_preview: List[str]
    test_auc:         float
    training_date:    str
