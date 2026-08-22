"""
05_scenario_analysis.py
-----------------------
Computes per-role and aggregate financial outcomes under three AI scenarios:
  Conservative, Moderate, Aggressive

Key metrics per scenario:
  - Labor savings
  - Productivity gain value
  - Implementation cost (adjusted by scenario multiplier)
  - Ongoing AI cost
  - Net annual benefit
  - ROI (Year 1)
  - Payback period (months)
  - 3-year NPV
  - Risk-adjusted net benefit (quality risk materialisation factored in)
  - Savings as % of total labor cost

All formulas are documented inline. Results are validated against the
constraint: savings <= total labor cost.
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
# PER-ROLE SCENARIO COMPUTATION
# ══════════════════════════════════════════════════════════════════════════════

def compute_scenario(df: pd.DataFrame, scenario_name: str, params: dict) -> pd.DataFrame:
    """
    Compute financial outcomes for a single scenario.

    Parameters
    ----------
    df           : master DataFrame with all role-level data
    scenario_name: 'Conservative' | 'Moderate' | 'Aggressive'
    params       : dict from config.SCENARIOS

    Formulas
    --------
    labor_savings = total_labor_cost x automation_potential x adoption_rate
    productivity_gain_value = total_labor_cost x productivity_uplift x productivity_mult
    impl_cost_adj = implementation_cost x impl_cost_mult
    net_annual_benefit = labor_savings + productivity_gain_value − ongoing_ai_cost_adj
    roi_year1 = (net_annual_benefit − impl_cost_adj) / impl_cost_adj
    payback_months = impl_cost_adj / (net_annual_benefit / 12)
    npv_3yr = Σ [net_annual_benefit / (1+r)^t] − impl_cost_adj  for t=1..3
    risk_adj_net_benefit = net_annual_benefit x (1 − risk_materialisation x risk_score)
    """

    ar   = params["adoption_rate"]
    pm   = params["productivity_mult"]
    icm  = params["impl_cost_mult"]
    ocm  = params["ongoing_cost_mult"]
    rmp  = params["risk_material_pct"]

    s = df.copy()
    s["scenario"] = scenario_name

    # Labor savings: fraction of automatable cost actually captured
    s["labor_savings"] = (
        s["total_annual_labor_cost_usd"] *
        s["automation_potential_pct"] *
        ar
    ).round(0)

    # Productivity gain: output value unlocked by AI assistance
    # Note: this is a VALUE of additional output, not a headcount reduction
    s["productivity_gain_value"] = (
        s["total_annual_labor_cost_usd"] *
        s["ai_productivity_uplift_pct"] *
        pm
    ).round(0)

    # Adjusted implementation and ongoing costs
    s["impl_cost_adj"]    = (s["implementation_cost_usd"] * icm).round(0)
    s["ongoing_cost_adj"] = (s["ongoing_ai_cost_per_year_usd"] * ocm).round(0)

    # Net annual benefit (Year 1+ = ongoing state after rollout)
    s["net_annual_benefit"] = (
        s["labor_savings"] + s["productivity_gain_value"] - s["ongoing_cost_adj"]
    ).round(0)

    # VALIDATION: savings cannot exceed total labor cost
    s["savings_pct_of_cost"] = (
        s["labor_savings"] / s["total_annual_labor_cost_usd"]
    ).round(4)

    # Constraint check
    overshoot = s[s["labor_savings"] > s["total_annual_labor_cost_usd"]]
    if not overshoot.empty:
        raise ValueError(f"[{scenario_name}] Labor savings exceed total cost for: "
                         f"{overshoot['role_name'].tolist()}")

    # ROI (Year 1)
    s["roi_year1"] = s.apply(
        lambda r: utils.roi(r["net_annual_benefit"], r["impl_cost_adj"]),
        axis=1
    ).round(4)

    # Payback period (months)
    s["payback_months"] = s.apply(
        lambda r: utils.payback_months(r["impl_cost_adj"], r["net_annual_benefit"]),
        axis=1
    ).round(1)

    # 3-year NPV (10% discount rate)
    s["npv_3yr"] = s.apply(
        lambda r: utils.npv(r["net_annual_benefit"], r["impl_cost_adj"]),
        axis=1
    ).round(0)

    # Risk-adjusted net benefit
    # Logic: if quality risk materialises, benefit is reduced proportionally
    s["risk_adj_net_benefit"] = (
        s["net_annual_benefit"] * (1 - rmp * s["risk_score"])
    ).round(0)

    # AI-assisted labor cost (remaining labor cost after automation savings)
    s["ai_assisted_labor_cost"] = (
        s["total_annual_labor_cost_usd"] - s["labor_savings"] + s["ongoing_cost_adj"]
    ).round(0)

    return s[[
        "role_id", "role_name", "function", "total_headcount",
        "avg_annual_salary_usd", "total_annual_labor_cost_usd",
        "automation_potential_pct", "ai_productivity_uplift_pct",
        "risk_score", "scenario",
        "labor_savings", "productivity_gain_value",
        "impl_cost_adj", "ongoing_cost_adj", "net_annual_benefit",
        "savings_pct_of_cost", "roi_year1", "payback_months", "npv_3yr",
        "risk_adj_net_benefit", "ai_assisted_labor_cost",
    ]]


# ══════════════════════════════════════════════════════════════════════════════
# AGGREGATE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

def aggregate_scenario(scenario_df: pd.DataFrame, scenario_name: str) -> dict:
    """Compute company-level totals for a scenario."""
    total_labor = scenario_df["total_annual_labor_cost_usd"].sum()
    return {
        "scenario":                   scenario_name,
        "total_headcount":            scenario_df["total_headcount"].sum(),
        "total_labor_cost":           total_labor,
        "total_labor_savings":        scenario_df["labor_savings"].sum(),
        "total_productivity_value":   scenario_df["productivity_gain_value"].sum(),
        "total_impl_cost":            scenario_df["impl_cost_adj"].sum(),
        "total_ongoing_cost":         scenario_df["ongoing_cost_adj"].sum(),
        "total_net_annual_benefit":   scenario_df["net_annual_benefit"].sum(),
        "savings_pct_of_labor":       scenario_df["labor_savings"].sum() / total_labor,
        "total_risk_adj_benefit":     scenario_df["risk_adj_net_benefit"].sum(),
        "portfolio_roi":              utils.roi(
                                          scenario_df["net_annual_benefit"].sum(),
                                          scenario_df["impl_cost_adj"].sum()
                                      ),
        "portfolio_payback_months":   utils.payback_months(
                                          scenario_df["impl_cost_adj"].sum(),
                                          scenario_df["net_annual_benefit"].sum()
                                      ),
        "total_npv_3yr":              scenario_df["npv_3yr"].sum(),
    }


# ══════════════════════════════════════════════════════════════════════════════
# OPTIMAL SCENARIO SELECTION
# ══════════════════════════════════════════════════════════════════════════════

def select_optimal_scenario(summary_df: pd.DataFrame) -> str:
    """
    Select the scenario that maximises risk-adjusted net benefit.
    The risk_adj_benefit already accounts for quality risk materialisation.
    We additionally normalise by total implementation cost to prefer
    capital-efficient scenarios.
    """
    summary_df = summary_df.copy()
    summary_df["efficiency_ratio"] = (
        summary_df["total_risk_adj_benefit"] / summary_df["total_impl_cost"]
    )
    optimal = summary_df.loc[summary_df["efficiency_ratio"].idxmax(), "scenario"]
    return optimal


# ══════════════════════════════════════════════════════════════════════════════
# PRINT RESULTS
# ══════════════════════════════════════════════════════════════════════════════

def print_scenario_results(all_scenarios: pd.DataFrame, summary_df: pd.DataFrame, optimal: str):
    utils.subsection("Company-level scenario comparison")
    display = summary_df.copy()
    for col in ["total_labor_cost", "total_labor_savings", "total_productivity_value",
                "total_impl_cost", "total_ongoing_cost", "total_net_annual_benefit",
                "total_risk_adj_benefit", "total_npv_3yr"]:
        display[col] = display[col].apply(lambda x: f"${x/1e6:.1f}M")
    display["savings_pct_of_labor"] = display["savings_pct_of_labor"].apply(utils.fmt_pct)
    display["portfolio_roi"]         = display["portfolio_roi"].apply(lambda x: f"{x*100:.1f}%")
    display["portfolio_payback_months"] = display["portfolio_payback_months"].apply(lambda x: f"{x:.1f} mo")
    print(display[[
        "scenario", "total_labor_savings", "total_productivity_value",
        "total_impl_cost", "total_net_annual_benefit",
        "savings_pct_of_labor", "portfolio_roi", "portfolio_payback_months",
        "total_npv_3yr",
    ]].to_string(index=False))

    utils.subsection(f"Optimal scenario: {optimal}")
    print(f"  Based on risk-adjusted net benefit / implementation cost efficiency ratio.")

    utils.subsection("Top 10 roles by net benefit (Moderate scenario)")
    mod = all_scenarios[all_scenarios["scenario"] == "Moderate"].copy()
    mod = mod.sort_values("net_annual_benefit", ascending=False).head(10)
    mod["net_annual_benefit_MUSD"] = (mod["net_annual_benefit"] / 1e6).round(2)
    mod["labor_savings_MUSD"]      = (mod["labor_savings"] / 1e6).round(2)
    mod["roi_year1_pct"]           = (mod["roi_year1"] * 100).round(1)
    print(mod[["role_name", "function", "labor_savings_MUSD",
               "net_annual_benefit_MUSD", "roi_year1_pct", "payback_months"]].to_string(index=False))

    utils.subsection("Quality risk check — Moderate scenario")
    high_risk = all_scenarios[
        (all_scenarios["scenario"] == "Moderate") &
        (all_scenarios["risk_score"] > 0.55)
    ][["role_name", "function", "risk_score", "labor_savings", "net_annual_benefit"]].copy()
    high_risk["labor_savings"] = high_risk["labor_savings"].apply(utils.fmt_usd)
    high_risk["net_annual_benefit"] = high_risk["net_annual_benefit"].apply(utils.fmt_usd)
    if not high_risk.empty:
        print("  High-risk roles requiring careful governance:")
        print(high_risk.to_string(index=False))
    else:
        print("  No roles with risk_score > 0.55 under moderate scenario.")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    utils.section("05 — SCENARIO ANALYSIS")

    df = pd.read_csv(os.path.join(config.DATA_PROC, "roles_enriched.csv"))

    # Run all three scenarios
    scenario_dfs = []
    summaries    = []

    for name, params in config.SCENARIOS.items():
        utils.subsection(f"Running scenario: {name}")
        s_df = compute_scenario(df, name, params)
        scenario_dfs.append(s_df)
        agg  = aggregate_scenario(s_df, name)
        summaries.append(agg)
        print(f"  Net annual benefit: {utils.fmt_usd(agg['total_net_annual_benefit'])}")
        print(f"  Payback: {agg['portfolio_payback_months']:.1f} months")
        print(f"  3-yr NPV: {utils.fmt_usd(agg['total_npv_3yr'])}")

    all_scenarios = pd.concat(scenario_dfs, ignore_index=True)
    summary_df    = pd.DataFrame(summaries)
    optimal       = select_optimal_scenario(summary_df)

    print_scenario_results(all_scenarios, summary_df, optimal)

    # Save outputs
    all_scenarios.to_csv(os.path.join(config.DATA_PROC, "scenario_results.csv"), index=False)
    summary_df.to_csv(os.path.join(config.DATA_PROC, "scenario_summary.csv"), index=False)

    print(f"\n  Scenario results saved to: {config.DATA_PROC}")
    return all_scenarios, summary_df, optimal


if __name__ == "__main__":
    main()
