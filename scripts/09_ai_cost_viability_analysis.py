"""
09_ai_cost_viability_analysis.py
---------------------------------
Answers the critical business question:
"Is AI actually cheaper than the humans it replaces — and under what conditions does it stop being cheaper?"

New analytical dimensions added:
1. Cost-Parity Flag      — Is AI cheaper than human for this role at moderate adoption?
2. Cost-Parity Threshold — Minimum adoption % needed for AI to break even vs. human cost
3. AI Cost Sensitivity   — How many roles flip to "AI is more expensive" if ongoing costs rise 25/50/100%?
4. AI vs Human Cost Per Hour — Fully-loaded cost comparison
5. Cost Efficiency Score — Combined metric ranking roles by cost-effectiveness of AI
"""

import os, sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE      = r"C:\Users\sahil\.gemini\antigravity\scratch\ai_workforce_analytics"
DATA_PROC = os.path.join(BASE, "dataset", "processed")
CHARTS    = os.path.join(BASE, "outputs", "charts")
STYLE     = "seaborn-v0_8-whitegrid"

# ── Load Data ─────────────────────────────────────────────────────────────────
master = pd.read_csv(os.path.join(DATA_PROC, "roles_enriched.csv"))

# Scenario adoption rates
CONSERVATIVE = 0.40
MODERATE     = 0.65
AGGRESSIVE   = 0.85

# Implementation cost amortization period (years)
AMORT_YEARS  = 3

print("="*70)
print("  09 -- AI COST VIABILITY ANALYSIS")
print("="*70)

# ══════════════════════════════════════════════════════════════════════════════
# 1. FULL COST ACCOUNTING PER ROLE (Moderate Scenario)
# ══════════════════════════════════════════════════════════════════════════════
df = master.copy()

# Human cost being replaced
df["human_labor_replaced_usd"] = (
    df["total_annual_labor_cost_usd"] * df["automation_potential_pct"] * MODERATE
)

# Total annual AI cost (ongoing + amortized implementation)
df["amortized_impl_cost_usd"] = df["implementation_cost_usd"] / AMORT_YEARS
df["total_ai_annual_cost_usd"] = df["ongoing_ai_cost_per_year_usd"] + df["amortized_impl_cost_usd"]

# Net position: positive = AI saves money, negative = AI costs more
df["net_cost_position_usd"] = df["human_labor_replaced_usd"] - df["total_ai_annual_cost_usd"]

# Flag: is AI cheaper than the human cost it replaces?
df["ai_is_cheaper"] = df["net_cost_position_usd"] > 0

# Cost efficiency ratio: how many $ saved per $ spent on AI
# > 1.0: AI returns more than it costs
# < 1.0: AI costs more than it saves
df["cost_efficiency_ratio"] = (
    df["human_labor_replaced_usd"] / df["total_ai_annual_cost_usd"].replace(0, np.nan)
).round(2)

print("\n--- COST VIABILITY SUMMARY (Moderate Scenario, 3-Year Amortization) ---")
total = len(df)
cheaper_count = df["ai_is_cheaper"].sum()
expensive_count = total - cheaper_count
print(f"  Roles where AI saves more than it costs : {cheaper_count} / {total}")
print(f"  Roles where AI costs MORE than it saves : {expensive_count} / {total}")
print(f"  Total human labor being replaced (moderate): ${df['human_labor_replaced_usd'].sum()/1e6:.1f}M")
print(f"  Total AI annual cost (incl. amortized impl): ${df['total_ai_annual_cost_usd'].sum()/1e6:.1f}M")
print(f"  Net position:                               ${df['net_cost_position_usd'].sum()/1e6:.1f}M")

print("\n--- Roles where AI is MORE EXPENSIVE than the humans it replaces ---")
expensive_roles = df[~df["ai_is_cheaper"]][
    ["role_name","function","human_labor_replaced_usd",
     "total_ai_annual_cost_usd","net_cost_position_usd","cost_efficiency_ratio"]
].sort_values("net_cost_position_usd")
expensive_roles["human_labor_replaced_usd"] = (expensive_roles["human_labor_replaced_usd"]/1e3).round(0).astype(int)
expensive_roles["total_ai_annual_cost_usd"] = (expensive_roles["total_ai_annual_cost_usd"]/1e3).round(0).astype(int)
expensive_roles["net_cost_position_usd"]    = (expensive_roles["net_cost_position_usd"]/1e3).round(0).astype(int)
expensive_roles.columns = ["Role","Function","Human_Saved_KUSD","AI_Cost_KUSD","Net_KUSD","Efficiency_Ratio"]
print(expensive_roles.to_string(index=False))


# ══════════════════════════════════════════════════════════════════════════════
# 2. COST-PARITY THRESHOLD
#    At what minimum adoption rate does AI just break even with its own cost?
#    Solve: total_labor_cost * automation_potential * X = total_ai_annual_cost
#    X = total_ai_annual_cost / (total_labor_cost * automation_potential)
# ══════════════════════════════════════════════════════════════════════════════
df["cost_parity_adoption_rate"] = (
    df["total_ai_annual_cost_usd"] /
    (df["total_annual_labor_cost_usd"] * df["automation_potential_pct"]).replace(0, np.nan)
)
df["cost_parity_adoption_rate"] = df["cost_parity_adoption_rate"].clip(0, 2)  # cap at 200%

# Flag: if threshold > 1.0, AI NEVER breaks even regardless of adoption
df["ai_never_breaks_even"] = df["cost_parity_adoption_rate"] > 1.0

print("\n--- COST-PARITY THRESHOLD (min adoption % for AI to break even) ---")
parity = df[["role_name","function","cost_parity_adoption_rate",
             "ai_never_breaks_even","cost_efficiency_ratio"]].copy()
parity["cost_parity_adoption_rate"] = (parity["cost_parity_adoption_rate"] * 100).round(1)
parity = parity.sort_values("cost_parity_adoption_rate", ascending=False)
print(parity.to_string(index=False))


# ══════════════════════════════════════════════════════════════════════════════
# 3. AI COST SENSITIVITY
#    If ongoing AI costs rise (e.g., LLM API price hikes, license increases),
#    at what cost increase does each role flip from viable to unviable?
# ══════════════════════════════════════════════════════════════════════════════
print("\n--- AI COST SENSITIVITY (How many roles flip to 'AI too expensive'?) ---")
sensitivity_results = []
for cost_increase_pct in [0, 10, 25, 50, 75, 100, 150, 200]:
    multiplier = 1 + cost_increase_pct / 100
    adj_ongoing = df["ongoing_ai_cost_per_year_usd"] * multiplier
    adj_total_ai_cost = adj_ongoing + df["amortized_impl_cost_usd"]
    net = df["human_labor_replaced_usd"] - adj_total_ai_cost
    n_viable = (net > 0).sum()
    sensitivity_results.append({
        "AI Cost Increase (%)": f"+{cost_increase_pct}%",
        "Roles Where AI Saves Money": n_viable,
        "Roles Where AI Too Expensive": total - n_viable,
    })
sens_df = pd.DataFrame(sensitivity_results)
print(sens_df.to_string(index=False))


# ══════════════════════════════════════════════════════════════════════════════
# 4. AI VS HUMAN COST PER PRODUCTIVE HOUR
# ══════════════════════════════════════════════════════════════════════════════
# Human cost per hour (already in master)
# AI cost per hour = total_ai_annual_cost / (productive_hours * headcount * automation_potential)
df["ai_hours_replaced"] = (
    df["productive_hours_per_year"] * df["total_headcount"] *
    df["automation_potential_pct"] * MODERATE
)
df["ai_cost_per_hour"] = (
    df["total_ai_annual_cost_usd"] / df["ai_hours_replaced"].replace(0, np.nan)
).round(2)

df["human_vs_ai_cost_ratio"] = (
    df["cost_per_productive_hour"] / df["ai_cost_per_hour"].replace(0, np.nan)
).round(2)
# > 1.0 means human is more expensive per hour → AI wins
# < 1.0 means AI is more expensive per hour → human wins

print("\n--- COST PER PRODUCTIVE HOUR: Human vs AI ---")
cph = df[["role_name","function","cost_per_productive_hour",
          "ai_cost_per_hour","human_vs_ai_cost_ratio"]].copy()
cph.columns = ["Role","Function","Human_$/Hr","AI_$/Hr","Human_Cost_Ratio"]
cph = cph.sort_values("Human_Cost_Ratio", ascending=False)
print(cph.to_string(index=False))


# ══════════════════════════════════════════════════════════════════════════════
# 5. VISUALIZATIONS
# ══════════════════════════════════════════════════════════════════════════════
plt.style.use(STYLE)
NAVY  = "#1B2A4A"
GREEN = "#27AE60"
RED   = "#E74C3C"
AMBER = "#F39C12"
BLUE  = "#2C6BAC"
GREY  = "#95A5A6"

# ── Chart A: Cost Efficiency Ratio by Role ─────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 8))
df_sorted = df.sort_values("cost_efficiency_ratio", ascending=True)
colors_bar = [GREEN if x >= 1.0 else RED for x in df_sorted["cost_efficiency_ratio"]]
bars = ax.barh(df_sorted["role_name"], df_sorted["cost_efficiency_ratio"],
               color=colors_bar, edgecolor="white", linewidth=0.5)
ax.axvline(1.0, color=NAVY, linewidth=2, linestyle="--", label="Break-Even (1.0x)")
ax.set_xlabel("Cost Efficiency Ratio  (Human Savings / AI Cost)", fontsize=11)
ax.set_title("AI Cost Efficiency by Role\nValues > 1.0: AI saves more than it costs | Values < 1.0: AI costs more than it saves",
             fontsize=13, fontweight="bold", color=NAVY)
ax.legend(fontsize=10)
for bar, val in zip(bars, df_sorted["cost_efficiency_ratio"]):
    ax.text(val + 0.05, bar.get_y() + bar.get_height()/2,
            f"{val:.2f}x", va="center", fontsize=7.5,
            color=GREEN if val >= 1.0 else RED)
plt.tight_layout()
path_a = os.path.join(CHARTS, "10_ai_cost_efficiency_ratio.png")
fig.savefig(path_a, dpi=150, bbox_inches="tight")
plt.close()
print(f"\n  Saved: {path_a}")

# ── Chart B: Cost-Parity Threshold per Role ────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 8))
df_p = df.sort_values("cost_parity_adoption_rate", ascending=True)
colors_p = [RED if x > 1.0 else (AMBER if x > 0.65 else GREEN)
            for x in df_p["cost_parity_adoption_rate"]]
bars2 = ax.barh(df_p["role_name"], df_p["cost_parity_adoption_rate"] * 100,
                color=colors_p, edgecolor="white", linewidth=0.5)
ax.axvline(65, color=NAVY, linewidth=2, linestyle="--", label="Moderate Scenario (65%)")
ax.axvline(100, color=RED, linewidth=1.5, linestyle=":", label="Theoretical Max (100%)")
ax.set_xlabel("Minimum Adoption Rate Needed for AI to Break Even (%)", fontsize=11)
ax.set_title("Cost-Parity Adoption Threshold by Role\nGreen < 65% (viable at Moderate) | Amber: 65-100% | Red: AI never breaks even",
             fontsize=13, fontweight="bold", color=NAVY)
ax.legend(fontsize=10)
plt.tight_layout()
path_b = os.path.join(CHARTS, "11_cost_parity_threshold.png")
fig.savefig(path_b, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {path_b}")

# ── Chart C: AI Cost Sensitivity — Viability as AI Costs Rise ─────────────
fig, ax = plt.subplots(figsize=(10, 5))
increases = [r["AI Cost Increase (%)"] for r in sensitivity_results]
viable    = [r["Roles Where AI Saves Money"] for r in sensitivity_results]
too_exp   = [r["Roles Where AI Too Expensive"] for r in sensitivity_results]
x = range(len(increases))
bars_v = ax.bar(x, viable,   color=GREEN, label="AI Saves Money", alpha=0.85)
bars_e = ax.bar(x, too_exp, bottom=viable, color=RED, label="AI Too Expensive", alpha=0.85)
ax.set_xticks(list(x))
ax.set_xticklabels(increases, fontsize=10)
ax.set_ylabel("Number of Roles", fontsize=11)
ax.set_xlabel("Increase in Annual AI Ongoing Costs (e.g., LLM API, licenses)", fontsize=11)
ax.set_title("AI Cost Sensitivity Analysis\nHow Rising AI Costs Erode Viability Across Roles",
             fontsize=13, fontweight="bold", color=NAVY)
ax.legend(fontsize=10)
for bar, val in zip(bars_v, viable):
    if val > 0:
        ax.text(bar.get_x() + bar.get_width()/2, val/2, str(val),
                ha="center", va="center", fontweight="bold", color="white", fontsize=10)
for bar, val in zip(bars_e, too_exp):
    if val > 0:
        v_h = [r["Roles Where AI Saves Money"] for r in sensitivity_results]
        ax.text(bar.get_x() + bar.get_width()/2,
                v_h[list(bars_e).index(bar)] + val/2,
                str(val),
                ha="center", va="center", fontweight="bold", color="white", fontsize=10)
plt.tight_layout()
path_c = os.path.join(CHARTS, "12_ai_cost_sensitivity.png")
fig.savefig(path_c, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {path_c}")

# ── Chart D: Human vs AI Cost Per Hour (Bubble) ────────────────────────────
fig, ax = plt.subplots(figsize=(12, 8))
df_cph = df.dropna(subset=["ai_cost_per_hour"])
colors_cph = [GREEN if r > 1 else RED for r in df_cph["human_vs_ai_cost_ratio"]]
sizes = (df_cph["total_headcount"] * 2).clip(20, 600)
sc = ax.scatter(df_cph["cost_per_productive_hour"],
                df_cph["ai_cost_per_hour"],
                s=sizes, c=colors_cph, alpha=0.75, edgecolors="white", linewidth=0.8)
# Diagonal: human cost == AI cost
max_val = max(df_cph["cost_per_productive_hour"].max(), df_cph["ai_cost_per_hour"].max()) * 1.1
ax.plot([0, max_val], [0, max_val], "k--", linewidth=1.2, alpha=0.5, label="Cost Parity Line (AI = Human)")
for _, row in df_cph.iterrows():
    ax.annotate(row["role_name"].split("(")[0].strip()[:18],
                (row["cost_per_productive_hour"], row["ai_cost_per_hour"]),
                fontsize=6.5, ha="left", va="bottom",
                xytext=(4, 2), textcoords="offset points")
ax.set_xlabel("Human Cost per Productive Hour ($)", fontsize=11)
ax.set_ylabel("AI Cost per Productive Hour ($) — incl. amortized impl.", fontsize=11)
ax.set_title("Human vs AI Cost Per Productive Hour\nBelow the diagonal line: AI is cheaper | Above: Humans are cheaper",
             fontsize=13, fontweight="bold", color=NAVY)
green_p = mpatches.Patch(color=GREEN, label="AI Cheaper (below diagonal)")
red_p   = mpatches.Patch(color=RED,   label="Human Cheaper (above diagonal)")
ax.legend(handles=[green_p, red_p, Line2D([0],[0],color="black",linestyle="--",label="Cost Parity")],
          fontsize=9)
ax.fill_between([0, max_val], [0, max_val], [max_val, max_val],
                alpha=0.04, color=RED, label="_nolegend_")
ax.fill_between([0, max_val], [0, 0], [0, max_val],
                alpha=0.04, color=GREEN, label="_nolegend_")
plt.tight_layout()
path_d = os.path.join(CHARTS, "13_human_vs_ai_cost_per_hour.png")
fig.savefig(path_d, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {path_d}")


# ══════════════════════════════════════════════════════════════════════════════
# 6. SAVE RESULTS
# ══════════════════════════════════════════════════════════════════════════════
cost_viability = df[[
    "role_id","role_name","function",
    "total_annual_labor_cost_usd",
    "human_labor_replaced_usd",
    "amortized_impl_cost_usd",
    "total_ai_annual_cost_usd",
    "net_cost_position_usd",
    "ai_is_cheaper",
    "cost_efficiency_ratio",
    "cost_parity_adoption_rate",
    "ai_never_breaks_even",
    "cost_per_productive_hour",
    "ai_cost_per_hour",
    "human_vs_ai_cost_ratio",
]].round(2)
cost_viability.to_csv(os.path.join(DATA_PROC, "ai_cost_viability.csv"), index=False)
sens_df.to_csv(os.path.join(DATA_PROC, "ai_cost_sensitivity.csv"), index=False)
print(f"\n  Results saved to: {DATA_PROC}")
print("\n  OK  Step 9: AI Cost Viability Analysis complete")
