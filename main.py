"""
main.py — Orchestrator
----------------------
Runs all 8 scripts in sequence.
Each step saves its outputs before the next step begins.
"""

import os
import sys
import time

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import utils

def run_step(step_num: int, module_path: str, fn_name: str = "main"):
    """Dynamically import and run a script's main() function."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(f"step_{step_num}", module_path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fn = getattr(mod, fn_name, None)
    if fn:
        return fn()


def main():
    utils.section("AI WORKFORCE ANALYTICS — FULL PIPELINE")
    print(f"  Project root: {config.BASE_DIR}")
    print(f"  Start time:   {time.strftime('%Y-%m-%d %H:%M:%S')}")

    nb = os.path.join(config.BASE_DIR, "notebooks")
    steps = [
        (1, os.path.join(nb, "01_data_generation.py"),    "Data Generation"),
        (2, os.path.join(nb, "02_data_cleaning_eda.py"),  "Data Cleaning & EDA"),
        (3, os.path.join(nb, "03_sql_analysis.py"),       "SQL Analysis"),
        (4, os.path.join(nb, "04_scoring_framework.py"),  "AAPS Scoring Framework"),
        (5, os.path.join(nb, "05_scenario_analysis.py"),  "Scenario Analysis"),
        (6, os.path.join(nb, "06_sensitivity_analysis.py"), "Sensitivity Analysis"),
        (7, os.path.join(nb, "07_visualizations.py"),     "Visualizations"),
        (8, os.path.join(nb, "08_excel_export.py"),       "Excel Export"),
    ]

    for step_num, path, label in steps:
        print(f"\n{'-'*70}")
        print(f"  STEP {step_num}: {label}")
        print(f"{'-'*70}")
        t0 = time.time()
        run_step(step_num, path)
        elapsed = time.time() - t0
        print(f"\n  OK Step {step_num} complete ({elapsed:.1f}s)")

    utils.section("PIPELINE COMPLETE")
    print(f"  Raw data:      {config.DATA_RAW}")
    print(f"  Processed:     {config.DATA_PROC}")
    print(f"  Database:      {config.DB_PATH}")
    print(f"  Charts:        {config.CHARTS_DIR}")
    print(f"  Excel:         {config.EXCEL_PATH}")
    print(f"\n  End time: {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
