"""
utils.py — Shared helper functions used across all scripts.
"""

import os
import numpy as np
import pandas as pd
import config


# --- Directory setup ----------------------------------------------------------

def ensure_dirs():
    """Create all required project directories if they don't exist."""
    for d in [config.DATA_RAW, config.DATA_PROC, config.CHARTS_DIR,
              os.path.join(config.BASE_DIR, "outputs")]:
        os.makedirs(d, exist_ok=True)


# --- Normalisation -----------------------------------------------------------

def minmax_norm(series: pd.Series) -> pd.Series:
    """Min-max normalise a pandas Series to [0, 1]."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - mn) / (mx - mn)


# --- Financial helpers --------------------------------------------------------

def npv(net_annual_benefit: float, impl_cost: float,
        rate: float = config.DISCOUNT_RATE,
        years: int = config.NPV_YEARS) -> float:
    """
    Compute NPV of a project over `years` years.
    Net annual benefit is assumed constant.
    """
    pv = sum(net_annual_benefit / ((1 + rate) ** yr) for yr in range(1, years + 1))
    return pv - impl_cost


def payback_months(impl_cost: float, net_annual_benefit: float) -> float:
    """Return payback period in months. Returns inf if benefit <= 0."""
    if net_annual_benefit <= 0:
        return float("inf")
    return impl_cost / (net_annual_benefit / 12)


def roi(net_annual_benefit: float, impl_cost: float) -> float:
    """Year-1 ROI as a decimal. Returns -1 if impl_cost = 0."""
    if impl_cost == 0:
        return float("inf")
    return (net_annual_benefit - impl_cost) / impl_cost


# --- RAG flag -----------------------------------------------------------------

def rag_flag(aaps: float, risk: float, payback: float) -> str:
    """Return 'Green', 'Amber', or 'Red' based on RAG thresholds."""
    g = config.RAG["green"]
    a = config.RAG["amber"]
    if aaps >= g["aaps_min"] and risk <= g["risk_max"] and payback <= g["payback_max_months"]:
        return "Green"
    if aaps >= a["aaps_min"] and risk <= a["risk_max"] and payback <= a["payback_max_months"]:
        return "Amber"
    return "Red"


# --- AI classification --------------------------------------------------------

def classify_ai_suitability(auto_pct: float, aug_pct: float) -> str:
    """
    Classify a role into one of three categories:
      - Full Automation: high automation potential
      - AI Augmentation: lower auto but meaningful augmentation
      - Low AI Suitability: neither threshold met
    """
    if auto_pct >= config.AUTOMATION_THRESHOLD:
        return "Full Automation"
    if aug_pct >= config.AUGMENTATION_THRESHOLD:
        return "AI Augmentation"
    return "Low AI Suitability"


# --- Printing helpers ---------------------------------------------------------

def section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def subsection(title: str):
    print(f"\n--- {title} ---")


def fmt_usd(value: float) -> str:
    """Format a dollar amount with commas and $ prefix."""
    return f"${value:,.0f}"


def fmt_pct(value: float) -> str:
    """Format a decimal as a percentage string."""
    return f"{value * 100:.1f}%"
