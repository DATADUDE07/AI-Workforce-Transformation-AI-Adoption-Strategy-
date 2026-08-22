"""
04_scoring_framework.py
-----------------------
Builds the AI Adoption Priority Score (AAPS) for each role.
Every factor, weight, and formula is explicitly documented.

Libraries:
  pandas  — data manipulation
  numpy   — normalisation, array ops
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

utils.ensure_dirs()


# ══════════════════════════════════════════════════════════════════════════════
# FACTOR ENGINEERING
# Each factor is constructed from raw data columns, then normalised to [0,1].
# ══════════════════════════════════════════════════════════════════════════════

def build_factors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construct six raw AAPS factors from the master data frame.

    F1  Automation Potential  — directly maps to automation_potential_pct
    F2  Cost-Saving Potential — automation_potential x total_labor_cost (normalised)
    F3  Productivity Improvement — ai_productivity_uplift_pct
    F4  Implementation Feasibility — composite of ai_maturity_readiness
                                     and (1 − change_mgmt_complexity)
    F5  Quality / Risk — composite risk_score (HIGHER = more risky, will be inverted)
    F6  Human Judgment Requirement — decision_intensity (HIGHER = more judgment, will be inverted)
    """

    df = df.copy()

    # F1: Automation potential
    df["F1_raw"] = df["automation_potential_pct"]

    # F2: Cost-saving potential (dollar value of automatable cost pool)
    #     Using absolute dollar value so large-cost roles get higher weight
    df["F2_raw"] = df["automatable_labor_cost_usd"]

    # F3: Productivity improvement potential
    df["F3_raw"] = df["ai_productivity_uplift_pct"]

    # F4: Implementation feasibility
    #     Weighted: 60% AI readiness + 40% inverse of change management complexity
    df["F4_raw"] = (
        0.60 * df["ai_maturity_readiness"] +
        0.40 * (1 - df["change_mgmt_complexity"])
    )

    # F5: Quality / risk (this factor will be INVERTED in the AAPS formula)
    #     Uses pre-computed risk_score from 02_data_cleaning_eda
    df["F5_raw"] = df["risk_score"]

    # F6: Human judgment requirement (INVERTED in AAPS formula)
    df["F6_raw"] = df["decision_intensity"]

    return df


def normalise_factors(df: pd.DataFrame) -> pd.DataFrame:
    """Min-max normalise all six raw factors to [0, 1]."""
    df = df.copy()
    for i in range(1, 7):
        col_raw  = f"F{i}_raw"
        col_norm = f"F{i}_norm"
        df[col_norm] = utils.minmax_norm(df[col_raw])
    return df


# ══════════════════════════════════════════════════════════════════════════════
# AAPS COMPUTATION
# ══════════════════════════════════════════════════════════════════════════════

def compute_aaps(df: pd.DataFrame, weights: dict = None) -> pd.DataFrame:
    """
    Apply the AAPS formula with the specified weights.
    Default weights come from config.AAPS_WEIGHTS.

    Formula:
    AAPS = w1 x F1_norm
         + w2 x F2_norm
         + w3 x F3_norm
         + w4 x F4_norm
         + w5 x (1 − F5_norm)   ← inverted: lower risk = higher score
         + w6 x (1 − F6_norm)   ← inverted: lower judgment = higher score
    """
    if weights is None:
        weights = config.AAPS_WEIGHTS

    w1 = weights["automation_potential"]
    w2 = weights["cost_saving_potential"]
    w3 = weights["productivity_improvement"]
    w4 = weights["implementation_feasibility"]
    w5 = weights["quality_risk"]
    w6 = weights["human_judgment_requirement"]

    df = df.copy()
    df["AAPS"] = (
        w1 * df["F1_norm"] +
        w2 * df["F2_norm"] +
        w3 * df["F3_norm"] +
        w4 * df["F4_norm"] +
        w5 * (1 - df["F5_norm"]) +
        w6 * (1 - df["F6_norm"])
    ).round(4)

    return df


# ══════════════════════════════════════════════════════════════════════════════
# RISK SCORE
# ══════════════════════════════════════════════════════════════════════════════

def compute_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recompute the composite risk score (in case master doesn't have it).
    Formula:
      risk_score = 0.40 x quality_risk_score
                 + 0.30 x regulatory_sensitivity
                 + 0.20 x customer_impact
                 + 0.10 x change_mgmt_complexity
    """
    df = df.copy()
    df["risk_score"] = (
        config.RISK_WEIGHTS["quality_risk_score"]     * df["quality_risk_score"] +
        config.RISK_WEIGHTS["regulatory_sensitivity"] * df["regulatory_sensitivity"] +
        config.RISK_WEIGHTS["customer_impact"]        * df["customer_impact"] +
        config.RISK_WEIGHTS["change_mgmt_complexity"] * df["change_mgmt_complexity"]
    ).round(4)
    return df


# ══════════════════════════════════════════════════════════════════════════════
# CLASSIFICATION & RANKING
# ══════════════════════════════════════════════════════════════════════════════

def classify_and_rank(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # AI Classification (Full Auto / Augmentation / Low Suitability)
    df["ai_classification"] = df.apply(
        lambda r: utils.classify_ai_suitability(
            r["automation_potential_pct"], r["augmentation_potential_pct"]
        ), axis=1
    )

    # AAPS Rank (1 = highest priority)
    df["AAPS_rank"] = df["AAPS"].rank(ascending=False, method="min").astype(int)

    # RAG flag
    df["RAG"] = df.apply(
        lambda r: utils.rag_flag(r["AAPS"], r["risk_score"], r.get("payback_months", 999)),
        axis=1
    )

    # Phase assignment: Top 33% = Phase 1, next = Phase 2, bottom = Phase 3
    df["Phase"] = pd.qcut(df["AAPS"], q=3, labels=["Phase 3", "Phase 2", "Phase 1"])

    return df


# ══════════════════════════════════════════════════════════════════════════════
# PRINT SCORING TABLE
# ══════════════════════════════════════════════════════════════════════════════

def print_scoring_summary(df: pd.DataFrame):
    cols = [
        "role_name", "function", "AAPS_rank",
        "AAPS", "F1_norm", "F2_norm", "F3_norm", "F4_norm",
        "risk_score", "ai_classification", "Phase", "RAG"
    ]
    display = df[cols].sort_values("AAPS_rank")
    display.columns = [
        "Role", "Dept", "Rank",
        "AAPS", "F1_Auto", "F2_Cost", "F3_Prod", "F4_Feas",
        "RiskScore", "AI_Class", "Phase", "RAG"
    ]

    utils.subsection("AAPS Rankings (all 30 roles)")
    print(display.to_string(index=False))

    utils.subsection("Score by AI Classification")
    for cls in ["Full Automation", "AI Augmentation", "Low AI Suitability"]:
        subset = df[df["ai_classification"] == cls]
        if not subset.empty:
            print(f"\n  {cls} ({len(subset)} roles):")
            print(f"    Avg AAPS: {subset['AAPS'].mean():.3f}")
            print(f"    Avg Risk: {subset['risk_score'].mean():.3f}")
            print(f"    Avg Auto Potential: {utils.fmt_pct(subset['automation_potential_pct'].mean())}")
            print(f"    Total Auto Cost Pool: {utils.fmt_usd(subset['automatable_labor_cost_usd'].sum())}")
            print(f"    Roles: {', '.join(subset['role_name'].tolist())}")

    utils.subsection("RAG Summary")
    print(df["RAG"].value_counts().to_string())

    utils.subsection("Phase Summary")
    phase_summary = df.groupby("Phase").agg(
        Roles=("role_name", "count"),
        Avg_AAPS=("AAPS", "mean"),
        Total_Auto_Pool_MUSD=("automatable_labor_cost_usd", lambda x: round(x.sum() / 1e6, 2)),
        Avg_Risk=("risk_score", "mean"),
    )
    print(phase_summary.to_string())

    utils.subsection("Top 10 Roles by AAPS")
    top10 = df.nsmallest(10, "AAPS_rank")[
        ["role_name", "function", "AAPS", "automation_potential_pct",
         "automatable_labor_cost_usd", "risk_score", "ai_classification", "RAG"]
    ].copy()
    top10["automatable_labor_cost_usd"] = (top10["automatable_labor_cost_usd"] / 1e6).round(2)
    top10.columns = ["Role", "Dept", "AAPS", "Auto_Pct", "Auto_Pool_MUSD", "Risk", "Class", "RAG"]
    print(top10.to_string(index=False))


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    utils.section("04 — AAPS SCORING FRAMEWORK")

    # Load enriched master
    df = pd.read_csv(os.path.join(config.DATA_PROC, "roles_enriched.csv"))

    # Ensure risk_score is present (recompute for safety)
    df = compute_risk_score(df)

    # Build and normalise factors
    df = build_factors(df)
    df = normalise_factors(df)

    utils.subsection("Factor raw ranges (before normalisation)")
    for i in range(1, 7):
        col = f"F{i}_raw"
        print(f"  F{i}: min={df[col].min():.4f}, max={df[col].max():.4f}, mean={df[col].mean():.4f}")

    # Compute AAPS with baseline weights
    df = compute_aaps(df)
    df = classify_and_rank(df)

    print_scoring_summary(df)

    # Save scoring output
    out_path = os.path.join(config.DATA_PROC, "scoring_output.csv")
    df.to_csv(out_path, index=False)
    print(f"\n  Scoring output saved to: {out_path}")

    return df


if __name__ == "__main__":
    main()
