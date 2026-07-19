"""
scorer.py — Convert model probability into a 0-100 score + tier,
and apply the business-rule overrides from lead_scoring_rules.md.

Feature extraction is aligned to the X Education dataset columns.
"""

from __future__ import annotations

import numpy as np

from config import SPAM_DOMAINS, TARGET_COUNTRIES, TIER_THRESHOLDS, VIP_COMPANIES

# ── Tier → recommended sales action ───────────────────────────────────────────
TIER_ACTIONS: dict[str, str] = {
    "Hot":    "Contact immediately — high conversion likelihood (60%+).",
    "Warm":   "Follow up within 48 hours — strong engagement signals.",
    "Cold":   "Add to nurture campaign — monitor for re-engagement.",
    "Frozen": "Exclude from active outreach or move to long-term drip.",
}

# ── Asymmetrique index → numeric ───────────────────────────────────────────────
ASYM_INDEX_MAP = {
    "01.high":   1.0,
    "02.medium": 0.5,
    "03.low":    0.0,
}

# ── Lead quality → numeric ────────────────────────────────────────────────────
LEAD_QUALITY_MAP = {
    "high in relevance": 1.0,
    "might be":          0.75,
    "not sure":          0.5,
    "low in relevance":  0.25,
    "worst":             0.0,
}

# ── Positive last-activity signals ────────────────────────────────────────────
POSITIVE_ACTIVITIES = {
    "converted to lead",
    "email link clicked",
    "email opened",
    "form submitted on website",
    "page visited on website",
    "had a phone conversation",
    "view in browser link clicked",
    "resubscribed to emails",
    "olark chat conversation",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _yn(val: str | None) -> float:
    """Convert 'Yes'/'No'/None to 1.0/0.0."""
    if val is None:
        return 0.0
    return 1.0 if str(val).strip().lower() == "yes" else 0.0


def _asym_index(val: str | None) -> float:
    if val is None:
        return 0.5
    return ASYM_INDEX_MAP.get(str(val).strip().lower(), 0.5)


def _lead_quality(val: str | None) -> float:
    if val is None:
        return 0.5
    return LEAD_QUALITY_MAP.get(str(val).strip().lower(), 0.5)


def _last_activity_score(val: str | None) -> float:
    if val is None:
        return 0.0
    return 1.0 if str(val).strip().lower() in POSITIVE_ACTIVITIES else 0.0


def _is_spam_email(email: str) -> bool:
    try:
        domain = email.split("@")[1].lower()
    except IndexError:
        return False
    return domain in [d.lower() for d in SPAM_DOMAINS]


def _is_vip_company(company: str) -> bool:
    return company.strip().lower() in [c.lower() for c in VIP_COMPANIES]


def _is_target_country(country: str) -> bool:
    if not country:
        return False
    return country.strip().lower() in [c.lower() for c in TARGET_COUNTRIES]


# ── Core scoring ───────────────────────────────────────────────────────────────

def probability_to_score(probability: float) -> float:
    return round(float(np.clip(probability * 100, 0.0, 100.0)), 2)


def score_to_tier(score: float) -> str:
    hot_thresh  = TIER_THRESHOLDS["Hot"]  * 100
    warm_thresh = TIER_THRESHOLDS["Warm"] * 100
    cold_thresh = TIER_THRESHOLDS["Cold"] * 100

    if score >= hot_thresh:
        return "Hot"
    elif score >= warm_thresh:
        return "Warm"
    elif score >= cold_thresh:
        return "Cold"
    else:
        return "Frozen"


def apply_business_rules(
    score: float,
    country: str,
    company: str = "",
    email: str = "",
) -> float:
    """Apply Phase-5 business rule overrides."""
    # Rule 1: Spam email → disqualify
    if email and _is_spam_email(email):
        return 0.0

    # Rule 2: VIP company → always Hot floor
    if company and _is_vip_company(company):
        score = max(score, 90.0)

    # Rule 3: Non-target geography → cap at 40 if below 60
    if country and not _is_target_country(country) and score < 60:
        score = min(score, 40.0)

    return round(float(np.clip(score, 0.0, 100.0)), 2)


def calculate_score(
    probability: float,
    country: str = "India",
    company: str = "",
    email: str = "",
) -> tuple[float, str, str]:
    """
    Full pipeline: probability → score → business rules → tier → action.

    Returns:
        (score, tier, recommended_action)
    """
    raw_score   = probability_to_score(probability)
    final_score = apply_business_rules(raw_score, country, company, email)
    tier        = score_to_tier(final_score)
    action      = TIER_ACTIONS[tier]
    return final_score, tier, action


# ── Feature extraction: LeadFeatures → numpy array ───────────────────────────

# Lead quality string → numeric mapping (matches notebook encoding)
_LEAD_QUALITY_NUM = {
    "high in relevance": 3.0,
    "might be":          2.0,
    "not sure":          1.5,
    "low in relevance":  1.0,
    "worst":             0.0,
}

# Lead source → is_referral / is_organic_search flags
_REFERRAL_SOURCES = {"reference", "referral sites", "welingak website"}
_ORGANIC_SOURCES  = {"organic search", "direct traffic"}


def lead_to_feature_vector(lead, feature_names: list[str]) -> np.ndarray:
    """
    Map a LeadFeatures Pydantic object to a numpy array aligned to `feature_names`.

    Exactly reproduces the engineered features created by the preprocessing notebook:
      - Lead Number (numeric, use 0 for new leads)
      - TotalVisits, Total Time Spent on Website, Page Views Per Visit (raw)
      - Asymmetrique Activity Score, Asymmetrique Profile Score (raw)
      - Website_Engagement_Score   = TotalVisits × Page Views Per Visit
      - Page_Views_Score           = Page Views Per Visit (alias)
      - No_Contact_Preference      = 1 if Do Not Email OR Do Not Call
      - SMS_Sent_Flag              = placeholder (0 for API leads)
      - Email_Opened_Flag          = 1 if Last Activity == "Email Opened"
      - Lead_Quality_Score         = numeric encoding of Lead Quality field
      - Is_Referral                = 1 if Lead Source is a referral channel
      - Is_Organic_Search          = 1 if Lead Source is organic/direct
      - Total_Asymmetrique_Score   = Activity Score + Profile Score
      - Prospect ID_xxxx columns  = 0 for unknown/new leads (not in training set)
    """
    tv   = float(lead.total_visits or 0)
    tt   = float(lead.total_time_spent_on_website or 0)
    pv   = float(lead.page_views_per_visit or 0)
    aa_s = float(lead.asymmetrique_activity_score or 15)
    ap_s = float(lead.asymmetrique_profile_score or 15)
    dne  = _yn(lead.do_not_email)
    dnc  = _yn(lead.do_not_call)

    # Lead source derived flags
    src_lower = (lead.lead_source or "").strip().lower()
    is_referral     = 1.0 if src_lower in _REFERRAL_SOURCES else 0.0
    is_organic      = 1.0 if src_lower in _ORGANIC_SOURCES  else 0.0

    # Lead quality numeric
    lq_lower  = (lead.lead_quality or "").strip().lower()
    lq_num    = _LEAD_QUALITY_NUM.get(lq_lower, 1.5)   # default: not sure

    # Email_Opened_Flag
    la_lower  = (lead.last_activity or "").strip().lower()
    email_opened_flag = 1.0 if la_lower == "email opened" else 0.0

    # Prospect ID one-hot column for this lead (0 for all unless ID is in training set)
    prospect_id_col = f"prospect id_{(lead.prospect_id or '').lower()}"

    raw_map: dict[str, float] = {
        # ── Raw columns (case-insensitive lookup) ─────────────────────────
        "lead number":                           0.0,        # new lead, no number yet
        "totalvisits":                           tv,
        "total time spent on website":           tt,
        "page views per visit":                  pv,
        "asymmetrique activity score":           aa_s,
        "asymmetrique profile score":            ap_s,

        # ── Engineered features (must match notebook column names exactly) ─
        "website_engagement_score":              tv * pv,
        "page_views_score":                      pv,
        "no_contact_preference":                 float(dne or dnc),
        "sms_sent_flag":                         0.0,        # not captured in API
        "email_opened_flag":                     email_opened_flag,
        "lead_quality_score":                    lq_num,
        "is_referral":                           is_referral,
        "is_organic_search":                     is_organic,
        "total_asymmetrique_score":              aa_s + ap_s,

        # ── Legacy / alternative name variants ────────────────────────────
        "do not email":                          dne,
        "do not call":                           dnc,
        "search":                                _yn(lead.search),
        "magazine":                              _yn(lead.magazine),
        "newspaper article":                     _yn(lead.newspaper_article),
        "x education forums":                    _yn(lead.x_education_forums),
        "newspaper":                             _yn(lead.newspaper),
        "digital advertisement":                 _yn(lead.digital_advertisement),
        "through recommendations":               _yn(lead.through_recommendations),
        "receive more updates about our courses": _yn(lead.receive_more_updates),
        "a free copy of mastering the interview": _yn(lead.a_free_copy_of_mastering_the_interview),

        # ── Prospect ID one-hot: 1 only if this exact ID was in training data ──
        prospect_id_col:                         1.0,
    }

    # Build array: use case-insensitive match for all keys
    raw_map_lower = {k.lower(): v for k, v in raw_map.items()}
    return np.array(
        [raw_map_lower.get(name.lower(), 0.0) for name in feature_names],
        dtype=float,
    )


# ── Demo-mode heuristic (used by model_loader when no pkl exists) ─────────────

def demo_heuristic(lead) -> float:
    """
    Rule-based probability using the X Education dataset's known strong predictors.
    Weights are derived from typical feature importances in this domain:
      - Total time on website  (strongest predictor)
      - Total visits
      - Asymmetrique scores
      - Activity signals
      - Opt-out flags (negative)
    """
    tv   = float(lead.total_visits or 0)
    tt   = float(lead.total_time_spent_on_website or 0)
    pv   = float(lead.page_views_per_visit or 0)
    aa_s = float(lead.asymmetrique_activity_score or 15)
    ap_s = float(lead.asymmetrique_profile_score or 15)
    la   = _last_activity_score(lead.last_activity)
    lna  = _last_activity_score(lead.last_notable_activity)
    lq   = _lead_quality(lead.lead_quality)
    do_not_email = _yn(lead.do_not_email)
    free_copy    = _yn(lead.a_free_copy_of_mastering_the_interview)

    score = 0.0
    score += min(tt / 2000.0, 1.0)  * 0.30   # time on site — strongest signal
    score += min(tv / 15.0,   1.0)  * 0.20   # visits
    score += min(aa_s / 25.0, 1.0)  * 0.15   # asymmetrique activity
    score += min(ap_s / 25.0, 1.0)  * 0.10   # asymmetrique profile
    score += la                      * 0.10   # last activity positive
    score += lna                     * 0.05   # last notable activity positive
    score += lq                      * 0.05   # lead quality
    score += free_copy               * 0.03   # requested free copy → engaged
    score -= do_not_email            * 0.08   # opted out → negative signal

    # Deterministic noise for realism
    seed_val = int(tv * 100 + tt + aa_s * 10 + ap_s * 10) % 997
    rng = np.random.default_rng(seed_val)
    noise = rng.uniform(-0.04, 0.04)

    return float(np.clip(score + noise, 0.01, 0.99))
