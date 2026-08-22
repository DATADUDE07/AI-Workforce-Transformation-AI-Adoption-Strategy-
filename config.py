"""
config.py — Central configuration for AI Workforce Analytics project.
All weights, scenario parameters, and constants live here so that
the sensitivity analysis only needs to touch this file.
"""

import os

# ─── Directory paths ─────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_RAW   = os.path.join(BASE_DIR, "data", "raw")
DATA_PROC  = os.path.join(BASE_DIR, "data", "processed")
DB_PATH    = os.path.join(BASE_DIR, "data", "ai_workforce.db")
CHARTS_DIR = os.path.join(BASE_DIR, "outputs", "charts")
EXCEL_PATH = os.path.join(BASE_DIR, "outputs", "AI_Workforce_Strategy.xlsx")

# ─── Reproducibility ─────────────────────────────────────────────────────────
RANDOM_SEED = 42

# ─── Labor cost assumptions ───────────────────────────────────────────────────
BENEFITS_LOAD       = 0.30   # 30 % employer cost on top of base salary
WORKING_WEEKS       = 48     # 52 weeks − 4 weeks leave / holidays
HOURS_PER_WEEK      = 40     # Standard full-time

# ─── Financial assumptions ───────────────────────────────────────────────────
DISCOUNT_RATE       = 0.10   # 10 % hurdle rate for NPV calculations
NPV_YEARS           = 3      # 3-year NPV horizon

# ─── AAPS weight set (baseline) ──────────────────────────────────────────────
# Weights must sum to 1.0
# See implementation_plan.md Section C for detailed rationale.
AAPS_WEIGHTS = {
    "automation_potential":      0.25,
    "cost_saving_potential":     0.25,
    "productivity_improvement":  0.15,
    "implementation_feasibility":0.15,
    "quality_risk":              0.10,   # inverted in formula
    "human_judgment_requirement":0.10,   # inverted in formula
}

# ─── Risk score weights ───────────────────────────────────────────────────────
RISK_WEIGHTS = {
    "quality_risk_score":     0.40,
    "regulatory_sensitivity": 0.30,
    "customer_impact":        0.20,
    "change_mgmt_complexity": 0.10,
}

# ─── Scenario parameters ─────────────────────────────────────────────────────
# adoption_rate      : fraction of automatable tasks actually captured
# productivity_mult  : fraction of potential productivity uplift realised
# impl_cost_mult     : multiplier on baseline implementation cost
# ongoing_cost_mult  : multiplier on baseline ongoing AI cost
# risk_material_pct  : fraction of quality_risk_score that materialises
# rollout_months     : total deployment timeline

SCENARIOS = {
    "Conservative": {
        "adoption_rate":     0.40,
        "productivity_mult": 0.50,
        "impl_cost_mult":    1.20,
        "ongoing_cost_mult": 1.00,
        "risk_material_pct": 0.80,
        "rollout_months":    36,
    },
    "Moderate": {
        "adoption_rate":     0.65,
        "productivity_mult": 0.75,
        "impl_cost_mult":    1.00,
        "ongoing_cost_mult": 1.00,
        "risk_material_pct": 0.60,
        "rollout_months":    24,
    },
    "Aggressive": {
        "adoption_rate":     0.85,
        "productivity_mult": 0.90,
        "impl_cost_mult":    0.90,
        "ongoing_cost_mult": 1.10,
        "risk_material_pct": 0.40,
        "rollout_months":    18,
    },
}

# ─── RAG thresholds ───────────────────────────────────────────────────────────
RAG = {
    "green": {"aaps_min": 0.70, "risk_max": 0.40, "payback_max_months": 12},
    "amber": {"aaps_min": 0.40, "risk_max": 0.65, "payback_max_months": 24},
    # red = anything not green or amber
}

# ─── AAPS classification thresholds ──────────────────────────────────────────
AUTOMATION_THRESHOLD    = 0.60   # automation_potential >= this → "Full Automation" candidate
AUGMENTATION_THRESHOLD  = 0.40   # augmentation_potential >= this AND auto < threshold → "Augmentation"
# Otherwise: "Low AI Suitability"

# ─── Sensitivity analysis parameters ─────────────────────────────────────────
# How much to shift each weight (absolute percentage points) for tornado analysis
SENSITIVITY_DELTA = 0.10   # ±10 pp

# ─── Chart style ─────────────────────────────────────────────────────────────
CHART_STYLE      = "seaborn-v0_8-whitegrid"
CHART_FIG_WIDTH  = 12
CHART_FIG_HEIGHT = 6
CHART_DPI        = 150
COLOR_PALETTE = {
    "primary":   "#1A3C5E",
    "secondary": "#2E86C1",
    "accent":    "#E8A838",
    "green":     "#27AE60",
    "amber":     "#F39C12",
    "red":       "#C0392B",
    "grey":      "#95A5A6",
}
