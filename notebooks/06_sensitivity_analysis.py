"""
06_sensitivity_analysis.py
--------------------------
Tests the robustness of AAPS rankings to changes in factor weights.

Method:
  1. For each of the 6 AAPS weights, shift it by +/-SENSITIVITY_DELTA (10 pp)
     while keeping all other weights proportional so they still sum to 1.0.
  2. Re-compute AAPS and re-rank all 30 roles under each perturbation.
  3. Compute Spearman rank correlation between baseline ranking
     and each perturbed ranking.
  4. Identify "stable" roles (rank does not move > 3 positions) vs "sensitive".
  5. Generate a Tornado chart showing the rank-correlation impact per weight.

High Spearman rho (>= 0.85) across all perturbations confirms that the
ranking is robust and not an artefact of arbitrary weight choices.
"""

import os
import sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils
from notebooks.four_scoring_module import build_factors, normalise_factors, compute_aaps

utils.ensure_dirs()


# ══════════════════════════════════════════════════════════════════════════════
# WEIGHT PERTURBATION
# ══════════════════════════════════════════════════════════════════════════════

def perturb_weights(base_weights: dict, target_key: str, delta: float) -> dict:
    """
    Increase `target_key` weight by `delta`, decrease all others proportionally.
    Returns a new weight dict that still sums to 1.0.
    """
    new_weights = base_weights.copy()
    new_val = np.clip(base_weights[target_key] + delta, 0.01, 0.99)
    change  = new_val - base_weights[target_key]

    other_keys  = [k for k in base_weights if k != target_key]
    other_total = sum(base_weights[k] for k in other_keys)

    if other_total > 0:
        for k in other_keys:
            new_weights[k] = max(0.01, base_weights[k] - change * (base_weights[k] / other_total))

    new_weights[target_key] = new_val

    # Normalise to ensure exact sum = 1.0
    total = sum(new_weights.values())
    new_weights = {k: v / total for k, v in new_weights.items()}
    return new_weights


def run_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run weight perturbations for all 6 factors x {+delta, -delta}.
    Returns a DataFrame with perturbation label, Spearman rho, and rank changes.
    """
    base_weights = config.AAPS_WEIGHTS.copy()
    delta        = config.SENSITIVITY_DELTA

    # Baseline ranking
    df_base = compute_aaps(df, base_weights)
    baseline_ranks = df_base["AAPS"].rank(ascending=False, method="min")

    results = []

    for key in base_weights:
        for sign, label_suffix in [(+delta, f"+{int(delta*100)}pp"), (-delta, f"-{int(delta*100)}pp")]:
            perturbed = perturb_weights(base_weights, key, sign)
            df_pert   = compute_aaps(df.copy(), perturbed)
            pert_ranks = df_pert["AAPS"].rank(ascending=False, method="min")

            rho, pval    = spearmanr(baseline_ranks, pert_ranks)
            max_rank_move = (pert_ranks - baseline_ranks).abs().max()
            avg_rank_move = (pert_ranks - baseline_ranks).abs().mean()

            results.append({
                "weight":        key,
                "perturbation":  label_suffix,
                "new_weight":    round(perturbed[key], 3),
                "spearman_rho":  round(rho, 4),
                "p_value":       round(pval, 4),
                "max_rank_move": int(max_rank_move),
                "avg_rank_move": round(avg_rank_move, 2),
                "perturbed_weights": perturbed,
            })

    return pd.DataFrame(results)


# ══════════════════════════════════════════════════════════════════════════════
# ROLE-LEVEL STABILITY
# ══════════════════════════════════════════════════════════════════════════════

def compute_role_stability(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each role, compute the maximum rank movement across all 12 perturbations.
    Roles with max movement <= 3 are "Stable", otherwise "Sensitive".
    """
    base_weights  = config.AAPS_WEIGHTS.copy()
    delta         = config.SENSITIVITY_DELTA
    df_base       = compute_aaps(df.copy(), base_weights)
    baseline_ranks = df_base["AAPS"].rank(ascending=False, method="min")

    all_pert_ranks = []
    for key in base_weights:
        for sign in [+delta, -delta]:
            perturbed  = perturb_weights(base_weights, key, sign)
            df_pert    = compute_aaps(df.copy(), perturbed)
            pert_ranks = df_pert["AAPS"].rank(ascending=False, method="min")
            all_pert_ranks.append(pert_ranks.values)

    all_pert_matrix = np.array(all_pert_ranks)   # shape: (12, 30)
    baseline_arr    = baseline_ranks.values

    max_moves = np.max(np.abs(all_pert_matrix - baseline_arr), axis=0)
    avg_moves = np.mean(np.abs(all_pert_matrix - baseline_arr), axis=0)

    stability_df = df_base[["role_id", "role_name", "function", "AAPS"]].copy()
    stability_df["baseline_rank"] = baseline_arr.astype(int)
    stability_df["max_rank_move"] = max_moves.astype(int)
    stability_df["avg_rank_move"] = avg_moves.round(2)
    stability_df["stability"]     = stability_df["max_rank_move"].apply(
        lambda x: "Stable" if x <= 3 else "Sensitive"
    )
    stability_df = stability_df.sort_values("baseline_rank")
    return stability_df


# ══════════════════════════════════════════════════════════════════════════════
# TORNADO CHART — Spearman rho by weight factor
# ══════════════════════════════════════════════════════════════════════════════

def plot_tornado(sens_df: pd.DataFrame):
    """
    Horizontal bar chart showing minimum Spearman rho (worst case) per weight.
    Lower rho means ranking is more sensitive to that weight.
    """
    # Get min Spearman rho per weight (worst-case perturbation)
    worst_case = sens_df.groupby("weight")["spearman_rho"].min().reset_index()
    worst_case.columns = ["weight", "min_spearman_rho"]
    worst_case = worst_case.sort_values("min_spearman_rho")

    labels = {
        "automation_potential":      "F1: Automation Potential (0.25)",
        "cost_saving_potential":     "F2: Cost-Saving Potential (0.25)",
        "productivity_improvement":  "F3: Productivity Improvement (0.15)",
        "implementation_feasibility":"F4: Implementation Feasibility (0.15)",
        "quality_risk":              "F5: Quality / Risk (0.10)",
        "human_judgment_requirement":"F6: Human Judgment (0.10)",
    }
    worst_case["label"] = worst_case["weight"].map(labels)
    worst_case["color"] = worst_case["min_spearman_rho"].apply(
        lambda x: config.COLOR_PALETTE["green"] if x >= 0.90
        else (config.COLOR_PALETTE["amber"] if x >= 0.80
              else config.COLOR_PALETTE["red"])
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(worst_case["label"], worst_case["min_spearman_rho"],
                   color=worst_case["color"], edgecolor="white", height=0.6)

    ax.axvline(x=0.85, color=config.COLOR_PALETTE["red"],    linestyle="--", linewidth=1.2, label="Minimum acceptable rho = 0.85")
    ax.axvline(x=0.90, color=config.COLOR_PALETTE["amber"],  linestyle=":",  linewidth=1.2, label="rho = 0.90 (strong robustness)")
    ax.axvline(x=1.00, color="grey",                         linestyle="-",  linewidth=0.5)

    for bar, (_, row) in zip(bars, worst_case.iterrows()):
        ax.text(bar.get_width() - 0.005, bar.get_y() + bar.get_height() / 2,
                f"rho = {row['min_spearman_rho']:.3f}", va="center", ha="right",
                fontsize=9, fontweight="bold", color="white")

    ax.set_xlim(0.70, 1.01)
    ax.set_xlabel("Minimum Spearman Rank Correlation (rho) with Baseline", fontsize=10)
    ax.set_title("Sensitivity Analysis — Robustness of AAPS Rankings to Weight Changes\n"
                 "(Worst-case +/-10 pp perturbation per factor)", fontsize=11, fontweight="bold")
    ax.legend(fontsize=8, loc="lower right")

    # Interpretation annotation
    ax.text(0.715, -0.8, "← Less robust to weight changes",
            fontsize=8, color=config.COLOR_PALETTE["red"], style="italic")
    ax.text(0.93, -0.8, "More robust →",
            fontsize=8, color=config.COLOR_PALETTE["green"], style="italic")

    plt.tight_layout()
    path = os.path.join(config.CHARTS_DIR, "06_sensitivity_tornado.png")
    plt.savefig(path, dpi=config.CHART_DPI, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════════
# PRINT RESULTS
# ══════════════════════════════════════════════════════════════════════════════

def print_sensitivity_results(sens_df: pd.DataFrame, stability_df: pd.DataFrame):
    utils.subsection("Spearman rho by weight perturbation")
    print(sens_df[[
        "weight", "perturbation", "new_weight", "spearman_rho", "max_rank_move", "avg_rank_move"
    ]].to_string(index=False))

    utils.subsection("Overall robustness verdict")
    min_rho = sens_df["spearman_rho"].min()
    avg_rho = sens_df["spearman_rho"].mean()
    print(f"  Minimum Spearman rho across all perturbations: {min_rho:.4f}")
    print(f"  Average Spearman rho across all perturbations: {avg_rho:.4f}")
    if min_rho >= 0.85:
        print("  VERDICT: Rankings are ROBUST — weight choices do not materially change conclusions.")
    else:
        print("  VERDICT: Some rankings are SENSITIVE — note weight-dependent roles in recommendations.")

    utils.subsection("Role stability (max rank movement across all perturbations)")
    print(stability_df.to_string(index=False))

    sensitive_roles = stability_df[stability_df["stability"] == "Sensitive"]
    if not sensitive_roles.empty:
        print(f"\n  Sensitive roles (rank moves >3 positions under some weight change):")
        print(sensitive_roles[["role_name", "function", "baseline_rank", "max_rank_move"]].to_string(index=False))


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    utils.section("06 — SENSITIVITY ANALYSIS")

    df = pd.read_csv(os.path.join(config.DATA_PROC, "scoring_output.csv"))

    utils.subsection("Running 12 weight perturbations (6 factors x +/-10pp)")
    sens_df = run_sensitivity(df)

    utils.subsection("Computing role-level rank stability")
    stability_df = compute_role_stability(df)

    print_sensitivity_results(sens_df, stability_df)
    plot_tornado(sens_df)

    sens_df.to_csv(os.path.join(config.DATA_PROC, "sensitivity_results.csv"), index=False)
    stability_df.to_csv(os.path.join(config.DATA_PROC, "role_stability.csv"), index=False)
    print(f"\n  Sensitivity results saved to: {config.DATA_PROC}")

    return sens_df, stability_df


if __name__ == "__main__":
    main()
