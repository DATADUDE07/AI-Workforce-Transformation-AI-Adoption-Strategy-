"""
07_visualizations.py
--------------------
Generates 9 business-focused matplotlib charts.
Every chart includes a business interpretation comment.

All charts saved as PNG to outputs/charts/.
No plt.show() calls — script runs headlessly.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

utils.ensure_dirs()

# Apply consistent style
try:
    plt.style.use(config.CHART_STYLE)
except OSError:
    plt.style.use("seaborn-v0_8-whitegrid")

CP = config.COLOR_PALETTE


def save(fig, filename: str):
    path = os.path.join(config.CHARTS_DIR, filename)
    fig.savefig(path, dpi=config.CHART_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 — Labor cost by department (horizontal bar, sorted)
# Business interpretation: Identifies the largest cost centres and therefore
# the departments with the most to gain from AI-driven cost reduction.
# ══════════════════════════════════════════════════════════════════════════════

def chart1_cost_by_department(master: pd.DataFrame):
    by_dept = master.groupby("function").agg(
        total_cost=("total_annual_labor_cost_usd", "sum"),
        headcount =("total_headcount", "sum"),
    ).sort_values("total_cost")

    fig, ax = plt.subplots(figsize=(config.CHART_FIG_WIDTH, 6))
    colors = [CP["primary"] if i < len(by_dept) - 3 else CP["accent"]
              for i in range(len(by_dept))]
    bars = ax.barh(by_dept.index, by_dept["total_cost"] / 1e6, color=colors, height=0.6)

    for bar, (_, row) in zip(bars, by_dept.iterrows()):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"${bar.get_width():.1f}M  ({int(row['headcount'])} FTE)",
                va="center", fontsize=9, color=CP["primary"])

    ax.set_xlabel("Annual Labor Cost (USD Millions)", fontsize=11)
    ax.set_title("Annual Labor Cost by Business Function\n"
                 "Highlighted bars = top 3 cost centres — highest AI savings potential",
                 fontsize=12, fontweight="bold")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}M"))

    # Legend
    patch_hi = mpatches.Patch(color=CP["accent"], label="Top 3 Cost Centres")
    patch_lo = mpatches.Patch(color=CP["primary"], label="Other Departments")
    ax.legend(handles=[patch_hi, patch_lo], loc="lower right", fontsize=9)

    fig.tight_layout()
    save(fig, "01_labor_cost_by_department.png")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 — AI automation potential by function (grouped bar)
# Business interpretation: Functions with high automation AND high readiness
# are the best candidates for Phase 1 deployment.
# ══════════════════════════════════════════════════════════════════════════════

def chart2_automation_by_function(master: pd.DataFrame):
    by_dept = master.groupby("function").agg(
        auto_pct  =("automation_potential_pct",   "mean"),
        aug_pct   =("augmentation_potential_pct", "mean"),
        readiness =("ai_maturity_readiness",      "mean"),
    ).sort_values("auto_pct", ascending=False)

    x     = np.arange(len(by_dept))
    width = 0.28
    fig, ax = plt.subplots(figsize=(config.CHART_FIG_WIDTH, 6))

    b1 = ax.bar(x - width,     by_dept["auto_pct"]  * 100, width, color=CP["secondary"], label="Automation Potential %")
    b2 = ax.bar(x,             by_dept["aug_pct"]   * 100, width, color=CP["accent"],    label="Augmentation Potential %")
    b3 = ax.bar(x + width,     by_dept["readiness"] * 100, width, color=CP["green"],     label="AI Readiness %")

    ax.set_xticks(x)
    ax.set_xticklabels(by_dept.index, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Percentage (%)", fontsize=11)
    ax.set_title("AI Automation & Augmentation Potential by Business Function\n"
                 "High automation + high readiness = Phase 1 priority",
                 fontsize=12, fontweight="bold")
    ax.axhline(60, color=CP["red"], linestyle="--", linewidth=1, alpha=0.7, label="Full Automation threshold (60%)")
    ax.legend(fontsize=9)
    ax.set_ylim(0, 100)

    fig.tight_layout()
    save(fig, "02_automation_potential_by_function.png")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 3 — Cost savings vs implementation cost (bubble chart)
# Business interpretation: Roles in the top-left quadrant deliver the most
# savings at the lowest investment — the best value propositions.
# ══════════════════════════════════════════════════════════════════════════════

def chart3_savings_vs_impl_cost(scenarios: pd.DataFrame, master: pd.DataFrame):
    mod = scenarios[scenarios["scenario"] == "Moderate"].copy()
    # scenarios CSV already has function and total_headcount columns

    fig, ax = plt.subplots(figsize=(config.CHART_FIG_WIDTH, 7))

    dept_colors = {d: c for d, c in zip(mod["function"].unique(),
        [CP["primary"], CP["secondary"], CP["accent"], CP["green"], CP["red"],
         CP["amber"], CP["grey"], "#8E44AD", "#16A085", "#E74C3C"])}

    for _, row in mod.iterrows():
        color  = dept_colors.get(row["function"], CP["grey"])
        size   = max(30, row["total_headcount"] * 1.2)
        ax.scatter(row["impl_cost_adj"] / 1e3, row["net_annual_benefit"] / 1e3,
                   s=size, color=color, alpha=0.75, edgecolors="white", linewidth=0.8)

    # Label only roles with net_benefit > $1M
    for _, row in mod[mod["net_annual_benefit"] > 1e6].iterrows():
        ax.annotate(
            row["role_name"].replace(" / ", "/\n"),
            (row["impl_cost_adj"] / 1e3, row["net_annual_benefit"] / 1e3),
            textcoords="offset points", xytext=(5, 5), fontsize=7, color=CP["primary"]
        )

    ax.axhline(0, color="grey", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Implementation Cost (USD Thousands)", fontsize=11)
    ax.set_ylabel("Net Annual Benefit (USD Thousands)", fontsize=11)
    ax.set_title("Cost Savings vs. Implementation Cost — Moderate AI Scenario\n"
                 "Bubble size = team headcount | Top-left quadrant = best value",
                 fontsize=12, fontweight="bold")

    legend_patches = [mpatches.Patch(color=c, label=d) for d, c in dept_colors.items()]
    ax.legend(handles=legend_patches, fontsize=8, loc="upper right", ncol=2,
              framealpha=0.9, title="Department")

    fig.tight_layout()
    save(fig, "03_savings_vs_impl_cost.png")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 4 — Productivity improvement by role (top 15)
# Business interpretation: Roles with high productivity uplift represent
# augmentation value — AI makes each employee more productive.
# ══════════════════════════════════════════════════════════════════════════════

def chart4_productivity_by_role(master: pd.DataFrame):
    top15 = master.nlargest(15, "ai_productivity_uplift_pct")[
        ["role_name", "function", "ai_productivity_uplift_pct", "ai_classification"]
    ].sort_values("ai_productivity_uplift_pct")

    color_map = {
        "Full Automation": CP["green"],
        "AI Augmentation": CP["accent"],
        "Low AI Suitability": CP["grey"],
    }
    colors = top15["ai_classification"].map(color_map)

    fig, ax = plt.subplots(figsize=(config.CHART_FIG_WIDTH, 6))
    bars = ax.barh(top15["role_name"], top15["ai_productivity_uplift_pct"] * 100,
                   color=colors, height=0.65)

    for bar in bars:
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{bar.get_width():.1f}%", va="center", fontsize=9)

    legend_patches = [mpatches.Patch(color=c, label=l) for l, c in color_map.items()]
    ax.legend(handles=legend_patches, fontsize=9, loc="lower right")
    ax.set_xlabel("AI Productivity Uplift (%)", fontsize=11)
    ax.set_title("Top 15 Roles by AI Productivity Improvement Potential\n"
                 "Colour indicates AI classification category",
                 fontsize=12, fontweight="bold")
    ax.set_xlim(0, max(top15["ai_productivity_uplift_pct"]) * 130)

    fig.tight_layout()
    save(fig, "04_productivity_by_role.png")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 5 — AAPS ranking (horizontal bar, coloured by RAG)
# Business interpretation: The AAPS score is a transparent, multi-factor
# ranking that should guide where to deploy AI resources first.
# ══════════════════════════════════════════════════════════════════════════════

def chart5_aaps_ranking(scoring: pd.DataFrame):
    df = scoring.sort_values("AAPS", ascending=True)

    rag_colors = {"Green": CP["green"], "Amber": CP["amber"], "Red": CP["red"]}
    colors = df["RAG"].map(rag_colors)

    fig, ax = plt.subplots(figsize=(config.CHART_FIG_WIDTH, 10))
    bars = ax.barh(df["role_name"], df["AAPS"], color=colors, height=0.7)

    for bar, (_, row) in zip(bars, df.iterrows()):
        ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height() / 2,
                f"{row['AAPS']:.3f}", va="center", fontsize=8)

    legend_patches = [mpatches.Patch(color=c, label=f"{l} Priority")
                      for l, c in rag_colors.items()]
    ax.legend(handles=legend_patches, fontsize=9, loc="lower right")
    ax.set_xlabel("AI Adoption Priority Score (AAPS)", fontsize=11)
    ax.set_title("AI Adoption Priority Score — All 30 Roles\n"
                 "Score = weighted composite of automation potential, cost savings,\n"
                 "productivity, feasibility, risk (inverted), and judgment (inverted)",
                 fontsize=12, fontweight="bold")
    ax.set_xlim(0, 1.05)
    ax.axvline(config.RAG["green"]["aaps_min"], color=CP["green"], linestyle="--",
               linewidth=1, alpha=0.6, label="Green threshold (0.70)")
    ax.axvline(config.RAG["amber"]["aaps_min"], color=CP["amber"], linestyle="--",
               linewidth=1, alpha=0.6, label="Amber threshold (0.40)")

    fig.tight_layout()
    save(fig, "05_aaps_ranking.png")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 6 — Automation potential vs human judgment (scatter quadrant)
# Business interpretation: Roles with high automation potential and low
# judgment requirements are ideal for full automation; those with high
# judgment should be augmented not replaced.
# ══════════════════════════════════════════════════════════════════════════════

def chart6_auto_vs_judgment(master: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(config.CHART_FIG_WIDTH, 7))

    class_colors = {
        "Full Automation":  CP["green"],
        "AI Augmentation":  CP["accent"],
        "Low AI Suitability": CP["red"],
    }

    for cls, grp in master.groupby("ai_classification"):
        ax.scatter(
            grp["decision_intensity"], grp["automation_potential_pct"],
            s=grp["total_annual_labor_cost_usd"] / 1e5,
            c=class_colors[cls], alpha=0.75, label=cls, edgecolors="white"
        )

    for _, row in master.iterrows():
        ax.annotate(
            row["role_name"].split(" ")[0],
            (row["decision_intensity"], row["automation_potential_pct"]),
            fontsize=6, alpha=0.75, color=CP["primary"]
        )

    # Quadrant lines
    ax.axvline(0.50, color="grey", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.axhline(0.50, color="grey", linestyle="--", linewidth=0.8, alpha=0.6)

    ax.text(0.05, 0.92, "Automate", fontsize=9, color=CP["green"],   style="italic", transform=ax.transAxes)
    ax.text(0.75, 0.92, "Human-Led\n(Low AI fit)", fontsize=9, color=CP["red"],   style="italic", transform=ax.transAxes)
    ax.text(0.05, 0.05, "Augment", fontsize=9,  color=CP["accent"], style="italic", transform=ax.transAxes)
    ax.text(0.75, 0.05, "Augment or\nDefer", fontsize=9, color=CP["amber"], style="italic", transform=ax.transAxes)

    ax.set_xlabel("Decision / Judgment Intensity (0 = low, 1 = high)", fontsize=11)
    ax.set_ylabel("Automation Potential (%)", fontsize=11)
    ax.set_title("Automation Potential vs. Human Judgment Requirement\n"
                 "Bubble size = annual labor cost | Quadrants define AI strategy",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)

    fig.tight_layout()
    save(fig, "06_auto_vs_judgment.png")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 7 — Cost savings under different scenarios (grouped bar)
# Business interpretation: Shows the range of outcomes and the trade-off
# between ambition (aggressive) and lower risk (conservative).
# ══════════════════════════════════════════════════════════════════════════════

def chart7_scenario_savings(scenarios: pd.DataFrame, master: pd.DataFrame):
    dept_scenario = []
    for sc_name, sc_df in scenarios.groupby("scenario"):
        # scenarios CSV already has function column - no merge needed
        agg = sc_df.groupby("function")["net_annual_benefit"].sum().reset_index()
        agg["scenario"] = sc_name
        dept_scenario.append(agg)

    combined = pd.concat(dept_scenario)
    pivot    = combined.pivot(index="function", columns="scenario", values="net_annual_benefit") / 1e6
    pivot    = pivot.sort_values("Moderate", ascending=False)

    x     = np.arange(len(pivot))
    width = 0.25
    sc_colors = {
        "Conservative": CP["grey"],
        "Moderate":     CP["secondary"],
        "Aggressive":   CP["green"],
    }

    fig, ax = plt.subplots(figsize=(config.CHART_FIG_WIDTH, 6))
    for i, (sc, color) in enumerate(sc_colors.items()):
        offset = (i - 1) * width
        bars   = ax.bar(x + offset, pivot.get(sc, 0), width, label=sc, color=color, alpha=0.9)

    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Net Annual Benefit (USD Millions)", fontsize=11)
    ax.set_title("Net Annual AI Benefit by Department and Scenario\n"
                 "Moderate scenario recommended — best balance of savings and risk",
                 fontsize=12, fontweight="bold")
    ax.axhline(0, color="grey", linewidth=0.8)
    ax.legend(title="Scenario", fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.1f}M"))

    fig.tight_layout()
    save(fig, "07_scenario_savings_by_department.png")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 8 — ROI vs implementation complexity (scatter)
# Business interpretation: Top-right = high ROI AND easy to implement (quick wins).
# Bottom-right = hard to implement = require strong business case.
# ══════════════════════════════════════════════════════════════════════════════

def chart8_roi_vs_complexity(scenarios: pd.DataFrame, master: pd.DataFrame):
    mod = scenarios[scenarios["scenario"] == "Moderate"].copy()
    extra_cols = [c for c in ["change_mgmt_complexity"] if c not in mod.columns and c in master.columns]
    if extra_cols:
        mod = mod.merge(master[["role_id"] + extra_cols], on="role_id", how="left")
    mod = mod[mod["roi_year1"] < 10]   # Filter extreme outliers for readability

    rag_colors = {"Green": CP["green"], "Amber": CP["amber"], "Red": CP["red"]}
    mod = mod.merge(
        master[["role_id", "RAG"]].rename(columns={"role_id": "role_id"}),
        on="role_id", how="left"
    ) if "RAG" in master.columns else mod.assign(RAG="Amber")

    fig, ax = plt.subplots(figsize=(config.CHART_FIG_WIDTH, 7))
    for _, row in mod.iterrows():
        color = rag_colors.get(row.get("RAG", "Amber"), CP["amber"])
        ax.scatter(row["change_mgmt_complexity"], row["roi_year1"],
                   s=max(50, row["total_headcount"] * 1.5),
                   c=color, alpha=0.75, edgecolors="white")

    for _, row in mod[mod["roi_year1"] > 0.5].iterrows():
        ax.annotate(
            row["role_name"].split(" ")[0],
            (row["change_mgmt_complexity"], row["roi_year1"]),
            textcoords="offset points", xytext=(4, 4), fontsize=7
        )

    ax.axvline(0.50, color="grey", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.axhline(0,    color="grey", linewidth=0.8)

    ax.text(0.02, 0.92, "Easy + High ROI\n(Quick Win)", fontsize=9, color=CP["green"],
            style="italic", transform=ax.transAxes)
    ax.text(0.70, 0.92, "Hard + High ROI\n(Strategic Bet)", fontsize=9, color=CP["amber"],
            style="italic", transform=ax.transAxes)
    ax.text(0.02, 0.05, "Easy + Low ROI\n(Low Priority)", fontsize=9, color=CP["grey"],
            style="italic", transform=ax.transAxes)
    ax.text(0.70, 0.05, "Hard + Low ROI\n(Avoid / Defer)", fontsize=9, color=CP["red"],
            style="italic", transform=ax.transAxes)

    legend_patches = [mpatches.Patch(color=c, label=f"{l}") for l, c in rag_colors.items()]
    ax.legend(handles=legend_patches, fontsize=9, title="RAG Priority")
    ax.set_xlabel("Change Management Complexity (0 = simple, 1 = very complex)", fontsize=11)
    ax.set_ylabel("Year-1 ROI (x)", fontsize=11)
    ax.set_title("ROI vs. Implementation Complexity — Moderate Scenario\n"
                 "Bubble size = team headcount",
                 fontsize=12, fontweight="bold")

    fig.tight_layout()
    save(fig, "08_roi_vs_complexity.png")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 9 — Risk score vs AI adoption opportunity (2x2 matrix)
# Business interpretation: This is the key strategic decision framework.
# High opportunity + low risk = deploy first.
# High opportunity + high risk = deploy with governance controls.
# ══════════════════════════════════════════════════════════════════════════════

def chart9_risk_vs_opportunity(master: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(config.CHART_FIG_WIDTH, 7))

    # Quadrant backgrounds
    ax.axhspan(0, 0.50, xmin=0, xmax=0.5, alpha=0.04, color=CP["amber"])
    ax.axhspan(0.50, 1.0, xmin=0, xmax=0.5, alpha=0.04, color=CP["green"])
    ax.axhspan(0, 0.50, xmin=0.5, xmax=1.0, alpha=0.04, color=CP["red"])
    ax.axhspan(0.50, 1.0, xmin=0.5, xmax=1.0, alpha=0.04, color=CP["amber"])

    class_markers = {
        "Full Automation":    "o",
        "AI Augmentation":    "s",
        "Low AI Suitability": "^",
    }
    class_colors = {
        "Full Automation":    CP["green"],
        "AI Augmentation":   CP["accent"],
        "Low AI Suitability": CP["red"],
    }

    for cls in master["ai_classification"].unique():
        sub = master[master["ai_classification"] == cls]
        ax.scatter(
            sub["automation_potential_pct"], sub["risk_score"],
            s=(sub["total_annual_labor_cost_usd"] / 8e4).clip(upper=400),
            marker=class_markers[cls], color=class_colors[cls],
            alpha=0.78, edgecolors="white", linewidth=0.8, label=cls
        )

    for _, row in master.iterrows():
        ax.annotate(row["role_name"].split(" ")[0],
                    (row["automation_potential_pct"], row["risk_score"]),
                    fontsize=6.5, alpha=0.8, color=CP["primary"],
                    xytext=(3, 3), textcoords="offset points")

    ax.axvline(0.50, color="grey", linestyle="--", linewidth=1, alpha=0.7)
    ax.axhline(0.50, color="grey", linestyle="--", linewidth=1, alpha=0.7)

    labels = [
        (0.12, 0.75, "[R] Proceed with\nGovernance Controls", CP["amber"]),
        (0.55, 0.75, "[R] Defer / Augment\nOnly", CP["red"]),
        (0.55, 0.12, "[G] QUICK WIN\nDeploy First", CP["green"]),
        (0.12, 0.12, "[B] Augment &\nMonitor", CP["secondary"]),
    ]
    for x, y, txt, c in labels:
        ax.text(x, y, txt, fontsize=9, color=c, fontweight="bold",
                ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.7))

    ax.set_xlabel("Automation Potential (0 = low, 1 = high)", fontsize=11)
    ax.set_ylabel("Risk Score (0 = low, 1 = high)", fontsize=11)
    ax.set_title("AI Risk vs. Opportunity Matrix\n"
                 "Bubble size = annual labor cost | Shape = AI category",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, loc="upper left")
    ax.set_xlim(-0.02, 1.05)
    ax.set_ylim(-0.02, 1.05)

    fig.tight_layout()
    save(fig, "09_risk_vs_opportunity.png")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    utils.section("07 — VISUALIZATIONS")

    master   = pd.read_csv(os.path.join(config.DATA_PROC, "roles_enriched.csv"))
    scoring  = pd.read_csv(os.path.join(config.DATA_PROC, "scoring_output.csv"))
    scenarios = pd.read_csv(os.path.join(config.DATA_PROC, "scenario_results.csv"))

    # Merge RAG into master if available from scoring
    if "RAG" in scoring.columns:
        master = master.merge(scoring[["role_id", "RAG", "AAPS", "Phase"]], on="role_id", how="left")

    print("\n  Generating 9 business charts...")
    chart1_cost_by_department(master)
    chart2_automation_by_function(master)
    chart3_savings_vs_impl_cost(scenarios, master)
    chart4_productivity_by_role(master)
    chart5_aaps_ranking(scoring)
    chart6_auto_vs_judgment(master)
    chart7_scenario_savings(scenarios, master)
    chart8_roi_vs_complexity(scenarios, master)
    chart9_risk_vs_opportunity(master)

    print(f"\n  All 9 charts saved to: {config.CHARTS_DIR}")


if __name__ == "__main__":
    main()
