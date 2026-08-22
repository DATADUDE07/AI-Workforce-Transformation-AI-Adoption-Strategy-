"""
02_data_cleaning_eda.py
-----------------------
Loads all four raw CSVs, validates integrity, performs EDA,
and saves enriched / merged frames to data/processed/.

Libraries:
  pandas  — data loading, cleaning, merging, descriptive stats
  numpy   — numeric operations
  matplotlib — visualisation of distributions & correlations
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend for script execution
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

utils.ensure_dirs()


# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════

def load_data():
    roles  = pd.read_csv(os.path.join(config.DATA_RAW, "roles.csv"))
    emp    = pd.read_csv(os.path.join(config.DATA_RAW, "employees.csv"))
    tasks  = pd.read_csv(os.path.join(config.DATA_RAW, "tasks.csv"))
    ai     = pd.read_csv(os.path.join(config.DATA_RAW, "ai_assumptions.csv"))
    return roles, emp, tasks, ai


# ══════════════════════════════════════════════════════════════════════════════
# DATA QUALITY CHECKS
# ══════════════════════════════════════════════════════════════════════════════

def run_quality_checks(roles, emp, tasks, ai):
    utils.subsection("Missing values")
    for name, df in [("roles", roles), ("employees", emp), ("tasks", tasks), ("ai_assumptions", ai)]:
        nulls = df.isnull().sum().sum()
        print(f"  {name:<18}: {nulls} null values")

    utils.subsection("Dtype validation")
    expected_numeric = {
        "roles": ["avg_annual_salary_usd", "num_employees", "task_repetitiveness_pct",
                  "decision_intensity", "customer_impact", "regulatory_sensitivity",
                  "skill_complexity", "current_error_rate_pct", "ai_maturity_readiness"],
        "employees": ["total_headcount", "total_annual_labor_cost_usd", "cost_per_productive_hour"],
        "ai":        ["automation_potential_pct", "augmentation_potential_pct",
                      "ai_productivity_uplift_pct", "implementation_cost_usd"],
    }
    all_ok = True
    for name, cols in expected_numeric.items():
        df_map = {"roles": roles, "employees": emp, "ai": ai}
        df = df_map[name]
        for col in cols:
            if not np.issubdtype(df[col].dtype, np.number):
                print(f"  [WARN] {name}.{col} is not numeric: {df[col].dtype}")
                all_ok = False
    if all_ok:
        print("  All expected numeric columns are correctly typed.")

    utils.subsection("Range checks (0–1 for percentage columns)")
    pct_checks = [
        (roles, "task_repetitiveness_pct"),
        (roles, "decision_intensity"),
        (roles, "customer_impact"),
        (roles, "regulatory_sensitivity"),
        (roles, "skill_complexity"),
        (roles, "current_error_rate_pct"),
        (roles, "ai_maturity_readiness"),
        (ai,    "automation_potential_pct"),
        (ai,    "augmentation_potential_pct"),
        (ai,    "human_oversight_required_pct"),
        (ai,    "ai_productivity_uplift_pct"),
        (ai,    "quality_risk_score"),
        (ai,    "change_mgmt_complexity"),
    ]
    for df, col in pct_checks:
        if df[col].min() < 0 or df[col].max() > 1:
            print(f"  [WARN] {col} out of [0,1]: min={df[col].min():.3f}, max={df[col].max():.3f}")
        else:
            print(f"  {col:<40}: OK  [{df[col].min():.3f}, {df[col].max():.3f}]")

    utils.subsection("Cross-table consistency")
    # automation + augmentation <= 1.0
    combined = ai["automation_potential_pct"] + ai["augmentation_potential_pct"]
    over = combined[combined > 1.0]
    if over.empty:
        print("  automation + augmentation <= 1.0: OK")
    else:
        print(f"  [WARN] {len(over)} roles exceed sum of 1.0")

    # Labor cost = headcount * salary * (1 + benefits)
    merged_check = emp.copy()
    expected_cost = merged_check["total_headcount"] * merged_check["avg_annual_salary_usd"] * (1 + config.BENEFITS_LOAD)
    diff = abs(merged_check["total_annual_labor_cost_usd"] - expected_cost)
    if (diff > 1).any():
        print(f"  [WARN] Labor cost formula mismatch for {(diff > 1).sum()} rows")
    else:
        print("  Labor cost formula consistency: OK")

    # Task time_pct sums per role
    sums = tasks.groupby("role_id")["time_pct"].sum()
    bad = sums[abs(sums - 1.0) > 0.01]
    if not bad.empty:
        print(f"  [WARN] time_pct != 1.0 for: {bad.index.tolist()}")
    else:
        print(f"  Task time_pct sums: OK (all roles sum to 1.0 +/- 0.01)")

    # Savings must not exceed labor cost
    print("  Savings-vs-cost check deferred to script 05 (scenario analysis).")


# ══════════════════════════════════════════════════════════════════════════════
# BUILD MASTER ANALYSIS FRAME
# ══════════════════════════════════════════════════════════════════════════════

def build_master_frame(roles, emp, ai):
    """Merge all role-level tables into one wide analysis frame."""
    df = roles.merge(emp.drop(columns=["avg_annual_salary_usd"]), on="role_id")
    df = df.merge(ai, on="role_id")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# DESCRIPTIVE STATISTICS
# ══════════════════════════════════════════════════════════════════════════════

def print_descriptive_stats(master, tasks):
    utils.subsection("Company-level totals")
    print(f"  Total headcount:              {master['total_headcount'].sum():>8,}")
    print(f"  Total annual labor cost:      {utils.fmt_usd(master['total_annual_labor_cost_usd'].sum())}")
    print(f"  Avg salary (all roles):       {utils.fmt_usd(master['avg_annual_salary_usd'].mean())}")
    print(f"  Median salary (all roles):    {utils.fmt_usd(master['avg_annual_salary_usd'].median())}")
    print(f"  Avg automation potential:     {utils.fmt_pct(master['automation_potential_pct'].mean())}")
    print(f"  Avg augmentation potential:   {utils.fmt_pct(master['augmentation_potential_pct'].mean())}")
    print(f"  Weighted avg productivity uplift: {utils.fmt_pct((master['ai_productivity_uplift_pct'] * master['total_headcount']).sum() / master['total_headcount'].sum())}")

    utils.subsection("Cost by function")
    by_func = master.groupby("function").agg(
        headcount=("total_headcount", "sum"),
        total_cost=("total_annual_labor_cost_usd", "sum"),
        avg_auto_potential=("automation_potential_pct", "mean"),
    ).sort_values("total_cost", ascending=False)
    by_func["cost_pct"] = by_func["total_cost"] / by_func["total_cost"].sum()
    print(by_func.to_string())

    utils.subsection("Role-level descriptive stats")
    cols = ["avg_annual_salary_usd", "total_headcount", "total_annual_labor_cost_usd",
            "automation_potential_pct", "augmentation_potential_pct",
            "ai_productivity_uplift_pct", "quality_risk_score"]
    print(master[cols].describe().round(2).to_string())

    utils.subsection("Task category distribution")
    cat_counts = tasks["task_category"].value_counts()
    auto_rate  = tasks.groupby("task_category")["automatable"].mean().round(3)
    aug_rate   = tasks.groupby("task_category")["augmentable"].mean().round(3)
    summary = pd.DataFrame({"count": cat_counts, "auto_rate": auto_rate, "aug_rate": aug_rate})
    print(summary.to_string())


# ══════════════════════════════════════════════════════════════════════════════
# ANOMALY DETECTION
# ══════════════════════════════════════════════════════════════════════════════

def detect_anomalies(master):
    utils.subsection("Anomaly detection (IQR method on salary and automation potential)")
    for col in ["avg_annual_salary_usd", "automation_potential_pct", "total_annual_labor_cost_usd"]:
        q1, q3 = master[col].quantile(0.25), master[col].quantile(0.75)
        iqr    = q3 - q1
        lower  = q1 - 1.5 * iqr
        upper  = q3 + 1.5 * iqr
        outliers = master[(master[col] < lower) | (master[col] > upper)][["role_name", col]]
        if not outliers.empty:
            print(f"\n  Outliers in '{col}':")
            print(outliers.to_string(index=False))
        else:
            print(f"  No outliers in '{col}'")


# ══════════════════════════════════════════════════════════════════════════════
# CORRELATION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def compute_correlations(master):
    utils.subsection("Correlation with automation_potential_pct")
    predictors = [
        "task_repetitiveness_pct", "decision_intensity", "customer_impact",
        "regulatory_sensitivity", "skill_complexity", "ai_maturity_readiness",
        "current_error_rate_pct", "avg_annual_salary_usd",
    ]
    correlations = master[predictors + ["automation_potential_pct"]].corr()["automation_potential_pct"].drop("automation_potential_pct")
    correlations = correlations.sort_values(ascending=False)
    for var, corr in correlations.items():
        direction = "^ auto" if corr > 0 else "v auto"
        print(f"  {var:<35}: r = {corr:+.3f}  {direction}")
    return correlations


# ══════════════════════════════════════════════════════════════════════════════
# EDA CHART — Correlation heatmap (saved; NOT interactive)
# ══════════════════════════════════════════════════════════════════════════════

def plot_correlation_heatmap(master):
    cols = [
        "task_repetitiveness_pct", "decision_intensity", "customer_impact",
        "regulatory_sensitivity", "skill_complexity", "ai_maturity_readiness",
        "automation_potential_pct", "augmentation_potential_pct",
        "ai_productivity_uplift_pct", "quality_risk_score",
    ]
    corr_matrix = master[cols].corr()

    short_labels = [
        "Repetitiveness", "Decision\nIntensity", "Customer\nImpact",
        "Regulatory\nSensitivity", "Skill\nComplexity", "AI\nReadiness",
        "Auto\nPotential", "Aug\nPotential", "Productivity\nUplift", "Quality\nRisk"
    ]

    fig, ax = plt.subplots(figsize=(11, 9))
    im = ax.imshow(corr_matrix.values, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_xticks(range(len(cols)))
    ax.set_yticks(range(len(cols)))
    ax.set_xticklabels(short_labels, fontsize=8)
    ax.set_yticklabels(short_labels, fontsize=8)
    plt.xticks(rotation=45, ha="right")

    for i in range(len(cols)):
        for j in range(len(cols)):
            val = corr_matrix.iloc[i, j]
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    fontsize=7, color="black" if abs(val) < 0.6 else "white")

    ax.set_title("Correlation Matrix — AI Adoption Driver Variables", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Variable", fontsize=10)
    ax.set_ylabel("Variable", fontsize=10)
    plt.tight_layout()
    path = os.path.join(config.CHARTS_DIR, "00_eda_correlation_heatmap.png")
    plt.savefig(path, dpi=config.CHART_DPI, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════════
# DERIVED METRICS (added to master frame)
# ══════════════════════════════════════════════════════════════════════════════

def add_derived_metrics(master):
    """
    Add key derived columns to the master frame:
    - automatable_labor_cost_usd: portion of cost that could theoretically be automated
    - augmentable_labor_cost_usd: portion relevant to augmentation
    - total_ai_opportunity_cost: combined addressable cost
    - implementation_cost_per_head: normalised implementation cost
    - weighted_risk_score: composite risk
    """
    master = master.copy()

    master["automatable_labor_cost_usd"] = (
        master["total_annual_labor_cost_usd"] * master["automation_potential_pct"]
    ).round(0)

    master["augmentable_labor_cost_usd"] = (
        master["total_annual_labor_cost_usd"] * master["augmentation_potential_pct"]
    ).round(0)

    master["total_ai_opportunity_cost_usd"] = (
        master["automatable_labor_cost_usd"] + master["augmentable_labor_cost_usd"]
    ).round(0)

    master["impl_cost_per_head_usd"] = (
        master["implementation_cost_usd"] / master["total_headcount"]
    ).round(0)

    # Composite risk score (matches utils.py formula)
    master["risk_score"] = (
        config.RISK_WEIGHTS["quality_risk_score"]     * master["quality_risk_score"] +
        config.RISK_WEIGHTS["regulatory_sensitivity"] * master["regulatory_sensitivity"] +
        config.RISK_WEIGHTS["customer_impact"]        * master["customer_impact"] +
        config.RISK_WEIGHTS["change_mgmt_complexity"] * master["change_mgmt_complexity"]
    ).round(3)

    # AI suitability classification
    master["ai_classification"] = master.apply(
        lambda r: utils.classify_ai_suitability(
            r["automation_potential_pct"], r["augmentation_potential_pct"]
        ), axis=1
    )

    utils.subsection("Derived metric summary")
    total_auto_pool = master["automatable_labor_cost_usd"].sum()
    total_aug_pool  = master["augmentable_labor_cost_usd"].sum()
    total_labor     = master["total_annual_labor_cost_usd"].sum()
    print(f"  Total automatable labor cost pool: {utils.fmt_usd(total_auto_pool)} ({total_auto_pool/total_labor:.1%} of total)")
    print(f"  Total augmentable labor cost pool: {utils.fmt_usd(total_aug_pool)} ({total_aug_pool/total_labor:.1%} of total)")
    print(f"  Total AI addressable cost pool:    {utils.fmt_usd(total_auto_pool + total_aug_pool)}")
    print(f"\n  AI Classification breakdown:")
    print(master["ai_classification"].value_counts().to_string())

    return master


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    utils.section("02 — DATA CLEANING & EDA")

    roles, emp, tasks, ai = load_data()
    print(f"  Loaded {len(roles)} roles, {len(emp)} employee records, "
          f"{len(tasks)} tasks, {len(ai)} AI assumption records.")

    utils.subsection("Data quality checks")
    run_quality_checks(roles, emp, tasks, ai)

    master = build_master_frame(roles, emp, ai)
    print(f"\n  Master frame: {master.shape[0]} rows x {master.shape[1]} columns")

    print_descriptive_stats(master, tasks)
    detect_anomalies(master)
    compute_correlations(master)
    plot_correlation_heatmap(master)

    master = add_derived_metrics(master)

    # Save enriched master
    out_path = os.path.join(config.DATA_PROC, "roles_enriched.csv")
    master.to_csv(out_path, index=False)
    print(f"\n  Enriched master frame saved to: {out_path}")

    # Save enriched tasks
    tasks.to_csv(os.path.join(config.DATA_PROC, "tasks_enriched.csv"), index=False)
    print(f"  Enriched tasks saved to: {config.DATA_PROC}/tasks_enriched.csv")

    return master


if __name__ == "__main__":
    main()
