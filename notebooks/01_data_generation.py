"""
01_data_generation.py
---------------------
Generates four synthetic CSVs that form the foundation of the analysis.

DATA PROVENANCE NOTE
--------------------
• Salary ranges are anchored to publicly available benchmarks:
  - U.S. Bureau of Labor Statistics (BLS) Occupational Employment Statistics (2023)
  - Glassdoor / LinkedIn Salary Insights (2023–2024 ranges for tech-sector roles)
• Automation potential scores are informed by published research:
  - McKinsey Global Institute "A future that works" (2017, updated 2023)
  - MIT / Stanford GenAI productivity studies (2022–2024)
  - Oxford Martin School "The Future of Employment" (Frey & Osborne, 2013)
• All specific values (headcounts, exact salaries, exact potentials) are
  SYNTHETIC and do not represent any real company.
• Role logic rules (described inline) ensure internal consistency.
"""

import numpy as np
import pandas as pd
import os
import sys

# Make project root importable regardless of working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

np.random.seed(config.RANDOM_SEED)
utils.ensure_dirs()


# ══════════════════════════════════════════════════════════════════════════════
# ROLE DEFINITIONS
# Each dict encodes domain knowledge. Values are not arbitrary:
# - repetitiveness ↑ when tasks are rule-based (data entry, invoicing)
# - decision_intensity ↑ when the role requires judgment (legal, strategy)
# - customer_impact ↑ when role interacts directly with external customers
# - regulatory_sensitivity ↑ for Finance, Legal, Healthcare-adjacent roles
# - ai_maturity_readiness ↑ when mature AI tooling exists (coding, analytics)
# ══════════════════════════════════════════════════════════════════════════════

ROLE_DEFINITIONS = [
    # -- Engineering ----------------------------------------------------------
    {
        "role_id": "ENG-001", "role_name": "Software Engineer",
        "function": "Engineering", "role_level": "Mid",
        "avg_annual_salary_usd": 130000, "num_employees": 420,
        "task_repetitiveness_pct": 0.28, "decision_intensity": 0.70,
        "customer_impact": 0.30, "regulatory_sensitivity": 0.20,
        "skill_complexity": 0.88, "current_error_rate_pct": 0.08,
        "ai_maturity_readiness": 0.82,
    },
    {
        "role_id": "ENG-002", "role_name": "QA / Test Engineer",
        "function": "Engineering", "role_level": "Mid",
        "avg_annual_salary_usd": 105000, "num_employees": 180,
        "task_repetitiveness_pct": 0.62, "decision_intensity": 0.45,
        "customer_impact": 0.20, "regulatory_sensitivity": 0.15,
        "skill_complexity": 0.65, "current_error_rate_pct": 0.06,
        "ai_maturity_readiness": 0.78,
    },
    {
        "role_id": "ENG-003", "role_name": "DevOps / Platform Engineer",
        "function": "Engineering", "role_level": "Senior",
        "avg_annual_salary_usd": 140000, "num_employees": 110,
        "task_repetitiveness_pct": 0.45, "decision_intensity": 0.60,
        "customer_impact": 0.25, "regulatory_sensitivity": 0.30,
        "skill_complexity": 0.82, "current_error_rate_pct": 0.05,
        "ai_maturity_readiness": 0.70,
    },
    # -- Data & Analytics -----------------------------------------------------
    {
        "role_id": "DAT-001", "role_name": "Data Analyst",
        "function": "Data & Analytics", "role_level": "Mid",
        "avg_annual_salary_usd": 95000, "num_employees": 150,
        "task_repetitiveness_pct": 0.55, "decision_intensity": 0.55,
        "customer_impact": 0.20, "regulatory_sensitivity": 0.25,
        "skill_complexity": 0.70, "current_error_rate_pct": 0.07,
        "ai_maturity_readiness": 0.80,
    },
    {
        "role_id": "DAT-002", "role_name": "Data Scientist",
        "function": "Data & Analytics", "role_level": "Senior",
        "avg_annual_salary_usd": 135000, "num_employees": 80,
        "task_repetitiveness_pct": 0.30, "decision_intensity": 0.72,
        "customer_impact": 0.15, "regulatory_sensitivity": 0.25,
        "skill_complexity": 0.92, "current_error_rate_pct": 0.06,
        "ai_maturity_readiness": 0.75,
    },
    {
        "role_id": "DAT-003", "role_name": "BI / Reporting Analyst",
        "function": "Data & Analytics", "role_level": "Junior",
        "avg_annual_salary_usd": 78000, "num_employees": 90,
        "task_repetitiveness_pct": 0.70, "decision_intensity": 0.35,
        "customer_impact": 0.15, "regulatory_sensitivity": 0.20,
        "skill_complexity": 0.55, "current_error_rate_pct": 0.09,
        "ai_maturity_readiness": 0.82,
    },
    # -- Finance ---------------------------------------------------------------
    {
        "role_id": "FIN-001", "role_name": "Financial Analyst",
        "function": "Finance", "role_level": "Mid",
        "avg_annual_salary_usd": 100000, "num_employees": 120,
        "task_repetitiveness_pct": 0.58, "decision_intensity": 0.62,
        "customer_impact": 0.15, "regulatory_sensitivity": 0.75,
        "skill_complexity": 0.72, "current_error_rate_pct": 0.05,
        "ai_maturity_readiness": 0.68,
    },
    {
        "role_id": "FIN-002", "role_name": "Accounts Payable / Receivable Clerk",
        "function": "Finance", "role_level": "Junior",
        "avg_annual_salary_usd": 58000, "num_employees": 85,
        "task_repetitiveness_pct": 0.88, "decision_intensity": 0.18,
        "customer_impact": 0.10, "regulatory_sensitivity": 0.65,
        "skill_complexity": 0.30, "current_error_rate_pct": 0.12,
        "ai_maturity_readiness": 0.85,
    },
    {
        "role_id": "FIN-003", "role_name": "Payroll Specialist",
        "function": "Finance", "role_level": "Junior",
        "avg_annual_salary_usd": 62000, "num_employees": 45,
        "task_repetitiveness_pct": 0.82, "decision_intensity": 0.22,
        "customer_impact": 0.12, "regulatory_sensitivity": 0.80,
        "skill_complexity": 0.38, "current_error_rate_pct": 0.04,
        "ai_maturity_readiness": 0.78,
    },
    {
        "role_id": "FIN-004", "role_name": "FP&A Manager",
        "function": "Finance", "role_level": "Manager",
        "avg_annual_salary_usd": 145000, "num_employees": 25,
        "task_repetitiveness_pct": 0.35, "decision_intensity": 0.82,
        "customer_impact": 0.10, "regulatory_sensitivity": 0.70,
        "skill_complexity": 0.85, "current_error_rate_pct": 0.03,
        "ai_maturity_readiness": 0.60,
    },
    # -- Human Resources -------------------------------------------------------
    {
        "role_id": "HR-001", "role_name": "HR Business Partner",
        "function": "Human Resources", "role_level": "Senior",
        "avg_annual_salary_usd": 110000, "num_employees": 40,
        "task_repetitiveness_pct": 0.30, "decision_intensity": 0.78,
        "customer_impact": 0.60, "regulatory_sensitivity": 0.55,
        "skill_complexity": 0.68, "current_error_rate_pct": 0.05,
        "ai_maturity_readiness": 0.50,
    },
    {
        "role_id": "HR-002", "role_name": "Recruiter / Talent Acquisition",
        "function": "Human Resources", "role_level": "Mid",
        "avg_annual_salary_usd": 85000, "num_employees": 65,
        "task_repetitiveness_pct": 0.52, "decision_intensity": 0.60,
        "customer_impact": 0.70, "regulatory_sensitivity": 0.40,
        "skill_complexity": 0.55, "current_error_rate_pct": 0.08,
        "ai_maturity_readiness": 0.65,
    },
    {
        "role_id": "HR-003", "role_name": "HR Operations / Admin",
        "function": "Human Resources", "role_level": "Junior",
        "avg_annual_salary_usd": 55000, "num_employees": 50,
        "task_repetitiveness_pct": 0.78, "decision_intensity": 0.22,
        "customer_impact": 0.35, "regulatory_sensitivity": 0.45,
        "skill_complexity": 0.32, "current_error_rate_pct": 0.10,
        "ai_maturity_readiness": 0.72,
    },
    # -- Sales -----------------------------------------------------------------
    {
        "role_id": "SAL-001", "role_name": "Account Executive (Enterprise)",
        "function": "Sales", "role_level": "Senior",
        "avg_annual_salary_usd": 155000, "num_employees": 200,
        "task_repetitiveness_pct": 0.22, "decision_intensity": 0.80,
        "customer_impact": 0.90, "regulatory_sensitivity": 0.20,
        "skill_complexity": 0.72, "current_error_rate_pct": 0.05,
        "ai_maturity_readiness": 0.55,
    },
    {
        "role_id": "SAL-002", "role_name": "Sales Development Rep (SDR)",
        "function": "Sales", "role_level": "Junior",
        "avg_annual_salary_usd": 68000, "num_employees": 180,
        "task_repetitiveness_pct": 0.65, "decision_intensity": 0.38,
        "customer_impact": 0.72, "regulatory_sensitivity": 0.10,
        "skill_complexity": 0.38, "current_error_rate_pct": 0.10,
        "ai_maturity_readiness": 0.70,
    },
    {
        "role_id": "SAL-003", "role_name": "Sales Operations Analyst",
        "function": "Sales", "role_level": "Mid",
        "avg_annual_salary_usd": 88000, "num_employees": 45,
        "task_repetitiveness_pct": 0.60, "decision_intensity": 0.45,
        "customer_impact": 0.20, "regulatory_sensitivity": 0.15,
        "skill_complexity": 0.58, "current_error_rate_pct": 0.07,
        "ai_maturity_readiness": 0.75,
    },
    # -- Customer Success / Support --------------------------------------------
    {
        "role_id": "CS-001", "role_name": "Customer Support Agent (Tier 1)",
        "function": "Customer Success", "role_level": "Junior",
        "avg_annual_salary_usd": 52000, "num_employees": 320,
        "task_repetitiveness_pct": 0.72, "decision_intensity": 0.28,
        "customer_impact": 0.92, "regulatory_sensitivity": 0.20,
        "skill_complexity": 0.28, "current_error_rate_pct": 0.12,
        "ai_maturity_readiness": 0.88,
    },
    {
        "role_id": "CS-002", "role_name": "Customer Success Manager",
        "function": "Customer Success", "role_level": "Mid",
        "avg_annual_salary_usd": 92000, "num_employees": 110,
        "task_repetitiveness_pct": 0.32, "decision_intensity": 0.70,
        "customer_impact": 0.88, "regulatory_sensitivity": 0.15,
        "skill_complexity": 0.62, "current_error_rate_pct": 0.06,
        "ai_maturity_readiness": 0.58,
    },
    {
        "role_id": "CS-003", "role_name": "Technical Support Specialist (Tier 2)",
        "function": "Customer Success", "role_level": "Mid",
        "avg_annual_salary_usd": 72000, "num_employees": 140,
        "task_repetitiveness_pct": 0.50, "decision_intensity": 0.52,
        "customer_impact": 0.80, "regulatory_sensitivity": 0.18,
        "skill_complexity": 0.58, "current_error_rate_pct": 0.09,
        "ai_maturity_readiness": 0.72,
    },
    # -- Legal -----------------------------------------------------------------
    {
        "role_id": "LEG-001", "role_name": "Contract / Paralegal Specialist",
        "function": "Legal", "role_level": "Mid",
        "avg_annual_salary_usd": 82000, "num_employees": 35,
        "task_repetitiveness_pct": 0.58, "decision_intensity": 0.55,
        "customer_impact": 0.20, "regulatory_sensitivity": 0.90,
        "skill_complexity": 0.70, "current_error_rate_pct": 0.04,
        "ai_maturity_readiness": 0.62,
    },
    {
        "role_id": "LEG-002", "role_name": "Corporate Counsel",
        "function": "Legal", "role_level": "Director",
        "avg_annual_salary_usd": 210000, "num_employees": 15,
        "task_repetitiveness_pct": 0.18, "decision_intensity": 0.92,
        "customer_impact": 0.30, "regulatory_sensitivity": 0.95,
        "skill_complexity": 0.95, "current_error_rate_pct": 0.02,
        "ai_maturity_readiness": 0.40,
    },
    # -- IT Operations ---------------------------------------------------------
    {
        "role_id": "ITO-001", "role_name": "IT Help Desk / Support",
        "function": "IT Operations", "role_level": "Junior",
        "avg_annual_salary_usd": 58000, "num_employees": 95,
        "task_repetitiveness_pct": 0.70, "decision_intensity": 0.30,
        "customer_impact": 0.60, "regulatory_sensitivity": 0.20,
        "skill_complexity": 0.38, "current_error_rate_pct": 0.10,
        "ai_maturity_readiness": 0.82,
    },
    {
        "role_id": "ITO-002", "role_name": "Systems / Network Administrator",
        "function": "IT Operations", "role_level": "Mid",
        "avg_annual_salary_usd": 95000, "num_employees": 60,
        "task_repetitiveness_pct": 0.50, "decision_intensity": 0.55,
        "customer_impact": 0.30, "regulatory_sensitivity": 0.40,
        "skill_complexity": 0.68, "current_error_rate_pct": 0.06,
        "ai_maturity_readiness": 0.65,
    },
    # -- Marketing -------------------------------------------------------------
    {
        "role_id": "MKT-001", "role_name": "Content Writer / Copywriter",
        "function": "Marketing", "role_level": "Mid",
        "avg_annual_salary_usd": 75000, "num_employees": 55,
        "task_repetitiveness_pct": 0.48, "decision_intensity": 0.52,
        "customer_impact": 0.55, "regulatory_sensitivity": 0.15,
        "skill_complexity": 0.58, "current_error_rate_pct": 0.07,
        "ai_maturity_readiness": 0.88,
    },
    {
        "role_id": "MKT-002", "role_name": "Digital Marketing Analyst",
        "function": "Marketing", "role_level": "Mid",
        "avg_annual_salary_usd": 82000, "num_employees": 40,
        "task_repetitiveness_pct": 0.60, "decision_intensity": 0.48,
        "customer_impact": 0.40, "regulatory_sensitivity": 0.12,
        "skill_complexity": 0.55, "current_error_rate_pct": 0.08,
        "ai_maturity_readiness": 0.80,
    },
    {
        "role_id": "MKT-003", "role_name": "Brand / Marketing Manager",
        "function": "Marketing", "role_level": "Manager",
        "avg_annual_salary_usd": 120000, "num_employees": 22,
        "task_repetitiveness_pct": 0.25, "decision_intensity": 0.78,
        "customer_impact": 0.60, "regulatory_sensitivity": 0.12,
        "skill_complexity": 0.72, "current_error_rate_pct": 0.05,
        "ai_maturity_readiness": 0.55,
    },
    # -- Product ---------------------------------------------------------------
    {
        "role_id": "PRD-001", "role_name": "Product Manager",
        "function": "Product", "role_level": "Senior",
        "avg_annual_salary_usd": 145000, "num_employees": 70,
        "task_repetitiveness_pct": 0.22, "decision_intensity": 0.85,
        "customer_impact": 0.65, "regulatory_sensitivity": 0.20,
        "skill_complexity": 0.82, "current_error_rate_pct": 0.05,
        "ai_maturity_readiness": 0.52,
    },
    {
        "role_id": "PRD-002", "role_name": "UX / Product Designer",
        "function": "Product", "role_level": "Mid",
        "avg_annual_salary_usd": 110000, "num_employees": 55,
        "task_repetitiveness_pct": 0.32, "decision_intensity": 0.68,
        "customer_impact": 0.70, "regulatory_sensitivity": 0.10,
        "skill_complexity": 0.75, "current_error_rate_pct": 0.06,
        "ai_maturity_readiness": 0.65,
    },
    {
        "role_id": "PRD-003", "role_name": "Technical Writer",
        "function": "Product", "role_level": "Mid",
        "avg_annual_salary_usd": 88000, "num_employees": 30,
        "task_repetitiveness_pct": 0.55, "decision_intensity": 0.42,
        "customer_impact": 0.45, "regulatory_sensitivity": 0.15,
        "skill_complexity": 0.55, "current_error_rate_pct": 0.07,
        "ai_maturity_readiness": 0.85,
    },
]


# ══════════════════════════════════════════════════════════════════════════════
# AI ASSUMPTION RULES
# automation_potential and augmentation_potential derived from:
# 1. task_repetitiveness_pct (high rep → higher auto potential)
# 2. decision_intensity (high decision → lower auto, higher aug)
# 3. ai_maturity_readiness (readiness enables higher potential)
# 4. regulatory_sensitivity (high reg → cap automation, add human oversight)
# Note: automation_potential + augmentation_potential <= 1.0 enforced below.
# ══════════════════════════════════════════════════════════════════════════════

def compute_ai_assumptions(role: dict) -> dict:
    rep   = role["task_repetitiveness_pct"]
    dec   = role["decision_intensity"]
    mat   = role["ai_maturity_readiness"]
    reg   = role["regulatory_sensitivity"]
    cust  = role["customer_impact"]
    n     = role["num_employees"]
    sal   = role["avg_annual_salary_usd"]

    # Base automation potential driven by repetitiveness and maturity
    auto_base = rep * 0.60 + mat * 0.40
    # Penalise for high decision intensity and regulatory exposure
    auto_pct  = auto_base * (1 - dec * 0.40) * (1 - reg * 0.25)
    auto_pct  = float(np.clip(auto_pct, 0.05, 0.90))

    # Augmentation potential: middle-complexity roles benefit most
    aug_base  = (1 - rep) * 0.40 + dec * 0.35 + mat * 0.25
    aug_pct   = aug_base * (1 - auto_pct * 0.50)   # less augmentation needed if fully automatable
    aug_pct   = float(np.clip(aug_pct, 0.05, 0.60))

    # Ensure combined <= 0.95 (at least 5% always needs human)
    if auto_pct + aug_pct > 0.95:
        scale  = 0.95 / (auto_pct + aug_pct)
        auto_pct *= scale
        aug_pct  *= scale

    # Human oversight: inversely proportional to automation confidence
    oversight = float(np.clip(1 - auto_pct * 0.80 + reg * 0.20, 0.15, 0.90))

    # Productivity uplift: driven by augmentation potential and maturity
    prod_uplift = float(np.clip(aug_pct * 0.60 + auto_pct * 0.30 + mat * 0.10, 0.05, 0.55))

    # Implementation cost: scales with team size and skill complexity
    skill  = role["skill_complexity"]
    impl_cost = n * sal * 0.08 * (1 + skill * 0.50) * (1 + reg * 0.30)
    impl_cost = float(round(impl_cost / 1000) * 1000)   # round to $1k

    # Ongoing AI cost: ~3-5% of labor cost per year
    ongoing_cost = float(round(n * sal * 0.04 * (1 + mat * 0.20) / 1000) * 1000)

    # Time to value: faster for high-maturity, high-repetitiveness roles
    ttv_months = int(round(24 * (1 - mat * 0.30) * (1 - rep * 0.20)))
    ttv_months = max(6, min(36, ttv_months))

    # Quality risk: high customer impact + high automation potential = risk
    quality_risk = float(np.clip(cust * 0.40 + auto_pct * 0.35 + (1 - skill) * 0.25, 0.10, 0.90))

    # Change management complexity: high-skill + low repetitiveness = harder change
    change_mgmt = float(np.clip(skill * 0.45 + dec * 0.35 + (1 - mat) * 0.20, 0.15, 0.90))

    # Scenario-specific automation percentages (% of auto_pct realised)
    s_cons = float(np.clip(auto_pct * config.SCENARIOS["Conservative"]["adoption_rate"], 0, 0.90))
    s_mod  = float(np.clip(auto_pct * config.SCENARIOS["Moderate"]["adoption_rate"],     0, 0.90))
    s_agg  = float(np.clip(auto_pct * config.SCENARIOS["Aggressive"]["adoption_rate"],   0, 0.90))

    return {
        "role_id":                      role["role_id"],
        "automation_potential_pct":     round(auto_pct,   3),
        "augmentation_potential_pct":   round(aug_pct,    3),
        "human_oversight_required_pct": round(oversight,  3),
        "ai_productivity_uplift_pct":   round(prod_uplift,3),
        "implementation_cost_usd":      impl_cost,
        "ongoing_ai_cost_per_year_usd": ongoing_cost,
        "time_to_value_months":         ttv_months,
        "quality_risk_score":           round(quality_risk, 3),
        "change_mgmt_complexity":       round(change_mgmt,  3),
        "scenario_conservative_auto_pct": round(s_cons, 3),
        "scenario_moderate_auto_pct":     round(s_mod,  3),
        "scenario_aggressive_auto_pct":   round(s_agg,  3),
    }


# ══════════════════════════════════════════════════════════════════════════════
# TASK DEFINITIONS
# ~5 tasks per role. time_pct values sum to 1.0 per role.
# automatable / augmentable flags based on task nature.
# ══════════════════════════════════════════════════════════════════════════════

TASK_DEFINITIONS = [
    # ENG-001 Software Engineer
    {"role_id":"ENG-001","task_name":"Code development & review",             "task_category":"Creative",   "time_pct":0.40,"automatable":False,"augmentable":True, "automation_confidence":0.35,"ai_tool_available":True, "notes":"AI assists but human judgment essential for architecture"},
    {"role_id":"ENG-001","task_name":"Automated test case generation",        "task_category":"Analysis",   "time_pct":0.15,"automatable":True, "augmentable":True, "automation_confidence":0.72,"ai_tool_available":True, "notes":"GitHub Copilot, Codium etc. high confidence"},
    {"role_id":"ENG-001","task_name":"Bug triage & documentation",            "task_category":"Data entry", "time_pct":0.15,"automatable":True, "augmentable":True, "automation_confidence":0.68,"ai_tool_available":True, "notes":"Structured pattern recognition"},
    {"role_id":"ENG-001","task_name":"Code refactoring & optimisation",       "task_category":"Creative",   "time_pct":0.15,"automatable":False,"augmentable":True, "automation_confidence":0.45,"ai_tool_available":True, "notes":"AI suggests, human decides"},
    {"role_id":"ENG-001","task_name":"System design & architecture review",   "task_category":"Decision",   "time_pct":0.15,"automatable":False,"augmentable":False,"automation_confidence":0.15,"ai_tool_available":False,"notes":"Requires deep contextual judgment"},

    # ENG-002 QA / Test Engineer
    {"role_id":"ENG-002","task_name":"Test case creation",                    "task_category":"Analysis",   "time_pct":0.25,"automatable":True, "augmentable":True, "automation_confidence":0.70,"ai_tool_available":True, "notes":"Highly structured; AI tools mature"},
    {"role_id":"ENG-002","task_name":"Automated regression test execution",   "task_category":"Data entry", "time_pct":0.30,"automatable":True, "augmentable":False,"automation_confidence":0.88,"ai_tool_available":True, "notes":"Fully automatable with CI/CD + AI"},
    {"role_id":"ENG-002","task_name":"Defect logging & triage",               "task_category":"Data entry", "time_pct":0.20,"automatable":True, "augmentable":True, "automation_confidence":0.75,"ai_tool_available":True, "notes":"Pattern-based classification"},
    {"role_id":"ENG-002","task_name":"User acceptance testing coordination",  "task_category":"Communication","time_pct":0.15,"automatable":False,"augmentable":True, "automation_confidence":0.30,"ai_tool_available":False,"notes":"Stakeholder interaction required"},
    {"role_id":"ENG-002","task_name":"Quality metrics reporting",             "task_category":"Analysis",   "time_pct":0.10,"automatable":True, "augmentable":False,"automation_confidence":0.82,"ai_tool_available":True, "notes":"Structured reporting"},

    # ENG-003 DevOps / Platform Engineer
    {"role_id":"ENG-003","task_name":"CI/CD pipeline management",             "task_category":"Analysis",   "time_pct":0.30,"automatable":True, "augmentable":True, "automation_confidence":0.65,"ai_tool_available":True, "notes":"Increasingly automated with AIOps"},
    {"role_id":"ENG-003","task_name":"Infrastructure provisioning (IaC)",     "task_category":"Creative",   "time_pct":0.25,"automatable":False,"augmentable":True, "automation_confidence":0.50,"ai_tool_available":True, "notes":"AI writes templates, human reviews"},
    {"role_id":"ENG-003","task_name":"Incident response & RCA",               "task_category":"Decision",   "time_pct":0.20,"automatable":False,"augmentable":True, "automation_confidence":0.40,"ai_tool_available":True, "notes":"AI diagnoses, human decides"},
    {"role_id":"ENG-003","task_name":"Security patching & compliance checks", "task_category":"Compliance", "time_pct":0.15,"automatable":True, "augmentable":True, "automation_confidence":0.70,"ai_tool_available":True, "notes":"Rule-based scanning automatable"},
    {"role_id":"ENG-003","task_name":"Capacity planning & monitoring",        "task_category":"Analysis",   "time_pct":0.10,"automatable":True, "augmentable":True, "automation_confidence":0.75,"ai_tool_available":True, "notes":"ML-based predictive monitoring"},

    # DAT-001 Data Analyst
    {"role_id":"DAT-001","task_name":"Data extraction & cleaning",            "task_category":"Data entry", "time_pct":0.30,"automatable":True, "augmentable":True, "automation_confidence":0.80,"ai_tool_available":True, "notes":"High-confidence automation"},
    {"role_id":"DAT-001","task_name":"Dashboard / report creation",           "task_category":"Analysis",   "time_pct":0.25,"automatable":True, "augmentable":True, "automation_confidence":0.72,"ai_tool_available":True, "notes":"AI-driven BI tools maturing"},
    {"role_id":"DAT-001","task_name":"Ad-hoc analysis & insight generation",  "task_category":"Analysis",   "time_pct":0.25,"automatable":False,"augmentable":True, "automation_confidence":0.45,"ai_tool_available":True, "notes":"Human judgment for context"},
    {"role_id":"DAT-001","task_name":"Data quality & validation",             "task_category":"Compliance", "time_pct":0.10,"automatable":True, "augmentable":True, "automation_confidence":0.78,"ai_tool_available":True, "notes":"Rule-based + ML anomaly detection"},
    {"role_id":"DAT-001","task_name":"Stakeholder communication & presentation","task_category":"Communication","time_pct":0.10,"automatable":False,"augmentable":True,"automation_confidence":0.20,"ai_tool_available":False,"notes":"Relationship and judgment"},

    # DAT-002 Data Scientist
    {"role_id":"DAT-002","task_name":"Model development & training",          "task_category":"Creative",   "time_pct":0.35,"automatable":False,"augmentable":True, "automation_confidence":0.35,"ai_tool_available":True, "notes":"AutoML assists but human critical"},
    {"role_id":"DAT-002","task_name":"Feature engineering",                   "task_category":"Analysis",   "time_pct":0.20,"automatable":False,"augmentable":True, "automation_confidence":0.45,"ai_tool_available":True, "notes":"Domain knowledge essential"},
    {"role_id":"DAT-002","task_name":"Data exploration & EDA",                "task_category":"Analysis",   "time_pct":0.20,"automatable":True, "augmentable":True, "automation_confidence":0.65,"ai_tool_available":True, "notes":"AI speeds up analysis"},
    {"role_id":"DAT-002","task_name":"Model evaluation & deployment",         "task_category":"Compliance", "time_pct":0.15,"automatable":False,"augmentable":True, "automation_confidence":0.40,"ai_tool_available":True, "notes":"Governance requires human sign-off"},
    {"role_id":"DAT-002","task_name":"Research & literature review",          "task_category":"Analysis",   "time_pct":0.10,"automatable":True, "augmentable":True, "automation_confidence":0.60,"ai_tool_available":True, "notes":"AI summarisation tools effective"},

    # DAT-003 BI / Reporting Analyst
    {"role_id":"DAT-003","task_name":"Scheduled report generation",           "task_category":"Data entry", "time_pct":0.35,"automatable":True, "augmentable":False,"automation_confidence":0.90,"ai_tool_available":True, "notes":"Highly repetitive; fully automatable"},
    {"role_id":"DAT-003","task_name":"Dashboard maintenance & updates",       "task_category":"Analysis",   "time_pct":0.25,"automatable":True, "augmentable":True, "automation_confidence":0.78,"ai_tool_available":True, "notes":"AI-driven BI platforms"},
    {"role_id":"DAT-003","task_name":"Data validation & reconciliation",      "task_category":"Compliance", "time_pct":0.20,"automatable":True, "augmentable":True, "automation_confidence":0.82,"ai_tool_available":True, "notes":"Rule-based"},
    {"role_id":"DAT-003","task_name":"Ad-hoc reporting requests",             "task_category":"Analysis",   "time_pct":0.12,"automatable":False,"augmentable":True, "automation_confidence":0.50,"ai_tool_available":True, "notes":"Natural language to SQL tools"},
    {"role_id":"DAT-003","task_name":"User training on BI tools",             "task_category":"Communication","time_pct":0.08,"automatable":False,"augmentable":True,"automation_confidence":0.25,"ai_tool_available":False,"notes":"Interpersonal"},

    # FIN-001 Financial Analyst
    {"role_id":"FIN-001","task_name":"Financial modelling & forecasting",     "task_category":"Analysis",   "time_pct":0.30,"automatable":False,"augmentable":True, "automation_confidence":0.45,"ai_tool_available":True, "notes":"AI enhances models; human oversees"},
    {"role_id":"FIN-001","task_name":"Variance analysis & reporting",         "task_category":"Analysis",   "time_pct":0.25,"automatable":True, "augmentable":True, "automation_confidence":0.70,"ai_tool_available":True, "notes":"Pattern-driven; AI can flag variances"},
    {"role_id":"FIN-001","task_name":"Budget preparation & tracking",         "task_category":"Data entry", "time_pct":0.20,"automatable":True, "augmentable":True, "automation_confidence":0.68,"ai_tool_available":True, "notes":"Structured process"},
    {"role_id":"FIN-001","task_name":"Regulatory & compliance reporting",     "task_category":"Compliance", "time_pct":0.15,"automatable":False,"augmentable":True, "automation_confidence":0.40,"ai_tool_available":True, "notes":"High regulatory stakes; human sign-off"},
    {"role_id":"FIN-001","task_name":"Executive financial presentations",     "task_category":"Communication","time_pct":0.10,"automatable":False,"augmentable":True,"automation_confidence":0.25,"ai_tool_available":True, "notes":"Judgment and communication"},

    # FIN-002 AP/AR Clerk
    {"role_id":"FIN-002","task_name":"Invoice processing & data entry",       "task_category":"Data entry", "time_pct":0.40,"automatable":True, "augmentable":False,"automation_confidence":0.92,"ai_tool_available":True, "notes":"OCR + AI; high automation confidence"},
    {"role_id":"FIN-002","task_name":"Payment reconciliation",                "task_category":"Data entry", "time_pct":0.25,"automatable":True, "augmentable":False,"automation_confidence":0.88,"ai_tool_available":True, "notes":"Rule-based matching"},
    {"role_id":"FIN-002","task_name":"Vendor / customer query resolution",    "task_category":"Customer",   "time_pct":0.20,"automatable":False,"augmentable":True, "automation_confidence":0.45,"ai_tool_available":True, "notes":"Chatbot for common queries"},
    {"role_id":"FIN-002","task_name":"Month-end close support",               "task_category":"Compliance", "time_pct":0.10,"automatable":True, "augmentable":True, "automation_confidence":0.72,"ai_tool_available":True, "notes":"Structured journal entries"},
    {"role_id":"FIN-002","task_name":"Audit documentation",                   "task_category":"Compliance", "time_pct":0.05,"automatable":True, "augmentable":True, "automation_confidence":0.65,"ai_tool_available":True, "notes":"Document assembly"},

    # FIN-003 Payroll Specialist
    {"role_id":"FIN-003","task_name":"Payroll calculation & processing",      "task_category":"Data entry", "time_pct":0.45,"automatable":True, "augmentable":False,"automation_confidence":0.90,"ai_tool_available":True, "notes":"Highly structured; minimal judgment"},
    {"role_id":"FIN-003","task_name":"Tax filing & compliance",               "task_category":"Compliance", "time_pct":0.25,"automatable":True, "augmentable":True, "automation_confidence":0.72,"ai_tool_available":True, "notes":"AI-driven payroll platforms handle this"},
    {"role_id":"FIN-003","task_name":"Employee query resolution",             "task_category":"Customer",   "time_pct":0.15,"automatable":False,"augmentable":True, "automation_confidence":0.42,"ai_tool_available":True, "notes":"Chatbot handles FAQs"},
    {"role_id":"FIN-003","task_name":"Benefits administration",               "task_category":"Data entry", "time_pct":0.10,"automatable":True, "augmentable":True, "automation_confidence":0.75,"ai_tool_available":True, "notes":"HRIS automation"},
    {"role_id":"FIN-003","task_name":"Payroll audit & reconciliation",        "task_category":"Compliance", "time_pct":0.05,"automatable":True, "augmentable":True, "automation_confidence":0.68,"ai_tool_available":True, "notes":"Rule-based checks"},

    # FIN-004 FP&A Manager
    {"role_id":"FIN-004","task_name":"Strategic financial planning",          "task_category":"Decision",   "time_pct":0.30,"automatable":False,"augmentable":True, "automation_confidence":0.20,"ai_tool_available":True, "notes":"AI provides scenarios; human decides"},
    {"role_id":"FIN-004","task_name":"Executive reporting & board prep",      "task_category":"Communication","time_pct":0.25,"automatable":False,"augmentable":True,"automation_confidence":0.30,"ai_tool_available":True, "notes":"AI drafts; human refines"},
    {"role_id":"FIN-004","task_name":"KPI monitoring & business partnering",  "task_category":"Analysis",   "time_pct":0.25,"automatable":False,"augmentable":True, "automation_confidence":0.40,"ai_tool_available":True, "notes":"AI flags anomalies"},
    {"role_id":"FIN-004","task_name":"Budget consolidation",                  "task_category":"Data entry", "time_pct":0.12,"automatable":True, "augmentable":True, "automation_confidence":0.65,"ai_tool_available":True, "notes":"Structured aggregation"},
    {"role_id":"FIN-004","task_name":"Scenario / sensitivity modelling",      "task_category":"Analysis",   "time_pct":0.08,"automatable":False,"augmentable":True, "automation_confidence":0.50,"ai_tool_available":True, "notes":"AI speeds up iteration"},

    # HR-001 HRBP
    {"role_id":"HR-001","task_name":"Employee relations & conflict resolution","task_category":"Decision",   "time_pct":0.30,"automatable":False,"augmentable":False,"automation_confidence":0.08,"ai_tool_available":False,"notes":"Human judgment essential"},
    {"role_id":"HR-001","task_name":"Performance management coaching",        "task_category":"Communication","time_pct":0.25,"automatable":False,"augmentable":True,"automation_confidence":0.15,"ai_tool_available":True, "notes":"AI provides data; human coaches"},
    {"role_id":"HR-001","task_name":"HR policy advisory & compliance",        "task_category":"Compliance", "time_pct":0.20,"automatable":False,"augmentable":True, "automation_confidence":0.35,"ai_tool_available":True, "notes":"AI retrieves policy; human advises"},
    {"role_id":"HR-001","task_name":"Workforce analytics reporting",          "task_category":"Analysis",   "time_pct":0.15,"automatable":True, "augmentable":True, "automation_confidence":0.65,"ai_tool_available":True, "notes":"Structured HR reporting"},
    {"role_id":"HR-001","task_name":"Change management programmes",           "task_category":"Communication","time_pct":0.10,"automatable":False,"augmentable":False,"automation_confidence":0.10,"ai_tool_available":False,"notes":"People-centric; human led"},

    # HR-002 Recruiter
    {"role_id":"HR-002","task_name":"Resume screening & shortlisting",        "task_category":"Data entry", "time_pct":0.30,"automatable":True, "augmentable":True, "automation_confidence":0.78,"ai_tool_available":True, "notes":"ATS + AI screening tools mature"},
    {"role_id":"HR-002","task_name":"Candidate outreach & scheduling",        "task_category":"Communication","time_pct":0.25,"automatable":True, "augmentable":True,"automation_confidence":0.72,"ai_tool_available":True, "notes":"Automated outreach tools"},
    {"role_id":"HR-002","task_name":"Interview coordination",                 "task_category":"Data entry", "time_pct":0.20,"automatable":True, "augmentable":True, "automation_confidence":0.70,"ai_tool_available":True, "notes":"Calendar automation"},
    {"role_id":"HR-002","task_name":"Candidate evaluation & decision",        "task_category":"Decision",   "time_pct":0.15,"automatable":False,"augmentable":True, "automation_confidence":0.25,"ai_tool_available":True, "notes":"Bias risk requires human oversight"},
    {"role_id":"HR-002","task_name":"Offer negotiation & onboarding",         "task_category":"Communication","time_pct":0.10,"automatable":False,"augmentable":True,"automation_confidence":0.20,"ai_tool_available":False,"notes":"Relationship"},

    # HR-003 HR Ops Admin
    {"role_id":"HR-003","task_name":"Employee data entry & maintenance",      "task_category":"Data entry", "time_pct":0.35,"automatable":True, "augmentable":False,"automation_confidence":0.88,"ai_tool_available":True, "notes":"HRIS automation high confidence"},
    {"role_id":"HR-003","task_name":"Benefits enrolment processing",          "task_category":"Data entry", "time_pct":0.25,"automatable":True, "augmentable":False,"automation_confidence":0.82,"ai_tool_available":True, "notes":"Structured data"},
    {"role_id":"HR-003","task_name":"Compliance & audit support",             "task_category":"Compliance", "time_pct":0.20,"automatable":True, "augmentable":True, "automation_confidence":0.68,"ai_tool_available":True, "notes":"Checklist driven"},
    {"role_id":"HR-003","task_name":"Employee query handling (tier 1)",       "task_category":"Customer",   "time_pct":0.12,"automatable":True, "augmentable":True, "automation_confidence":0.72,"ai_tool_available":True, "notes":"HR chatbot"},
    {"role_id":"HR-003","task_name":"Reporting & document preparation",       "task_category":"Data entry", "time_pct":0.08,"automatable":True, "augmentable":False,"automation_confidence":0.80,"ai_tool_available":True, "notes":"Template automation"},

    # SAL-001 Account Executive (Enterprise)
    {"role_id":"SAL-001","task_name":"Client relationship management",        "task_category":"Customer",   "time_pct":0.35,"automatable":False,"augmentable":True, "automation_confidence":0.10,"ai_tool_available":False,"notes":"Human relationship essential"},
    {"role_id":"SAL-001","task_name":"Deal negotiation & closing",            "task_category":"Decision",   "time_pct":0.25,"automatable":False,"augmentable":True, "automation_confidence":0.12,"ai_tool_available":True, "notes":"AI provides deal intel; human leads"},
    {"role_id":"SAL-001","task_name":"CRM data entry & opportunity tracking", "task_category":"Data entry", "time_pct":0.15,"automatable":True, "augmentable":True, "automation_confidence":0.75,"ai_tool_available":True, "notes":"AI auto-logs calls/emails"},
    {"role_id":"SAL-001","task_name":"Proposal & contract preparation",       "task_category":"Creative",   "time_pct":0.15,"automatable":False,"augmentable":True, "automation_confidence":0.45,"ai_tool_available":True, "notes":"AI drafts; human customises"},
    {"role_id":"SAL-001","task_name":"Pipeline & forecast reporting",         "task_category":"Analysis",   "time_pct":0.10,"automatable":True, "augmentable":True, "automation_confidence":0.70,"ai_tool_available":True, "notes":"AI-driven CRM forecasting"},

    # SAL-002 SDR
    {"role_id":"SAL-002","task_name":"Prospecting & lead research",           "task_category":"Data entry", "time_pct":0.30,"automatable":True, "augmentable":True, "automation_confidence":0.78,"ai_tool_available":True, "notes":"AI lead scoring & enrichment"},
    {"role_id":"SAL-002","task_name":"Cold outreach (email/LinkedIn)",        "task_category":"Communication","time_pct":0.30,"automatable":True, "augmentable":True,"automation_confidence":0.72,"ai_tool_available":True, "notes":"AI personalization at scale"},
    {"role_id":"SAL-002","task_name":"Discovery calls",                       "task_category":"Customer",   "time_pct":0.20,"automatable":False,"augmentable":True, "automation_confidence":0.20,"ai_tool_available":True, "notes":"AI coaching in real time"},
    {"role_id":"SAL-002","task_name":"CRM logging & follow-up scheduling",   "task_category":"Data entry", "time_pct":0.12,"automatable":True, "augmentable":False,"automation_confidence":0.82,"ai_tool_available":True, "notes":"Conversational AI logging"},
    {"role_id":"SAL-002","task_name":"Meeting scheduling & coordination",     "task_category":"Data entry", "time_pct":0.08,"automatable":True, "augmentable":False,"automation_confidence":0.88,"ai_tool_available":True, "notes":"AI scheduling tools"},

    # SAL-003 Sales Ops Analyst
    {"role_id":"SAL-003","task_name":"Sales data analysis & reporting",       "task_category":"Analysis",   "time_pct":0.35,"automatable":True, "augmentable":True, "automation_confidence":0.75,"ai_tool_available":True, "notes":"BI tools + AI insights"},
    {"role_id":"SAL-003","task_name":"CRM data quality management",           "task_category":"Data entry", "time_pct":0.25,"automatable":True, "augmentable":False,"automation_confidence":0.80,"ai_tool_available":True, "notes":"AI data cleansing"},
    {"role_id":"SAL-003","task_name":"Sales process improvement",             "task_category":"Analysis",   "time_pct":0.20,"automatable":False,"augmentable":True, "automation_confidence":0.40,"ai_tool_available":True, "notes":"Process mining tools"},
    {"role_id":"SAL-003","task_name":"Commission calculation & tracking",     "task_category":"Data entry", "time_pct":0.12,"automatable":True, "augmentable":False,"automation_confidence":0.88,"ai_tool_available":True, "notes":"Rule-based calculation"},
    {"role_id":"SAL-003","task_name":"Tool & platform administration",        "task_category":"Analysis",   "time_pct":0.08,"automatable":True, "augmentable":True, "automation_confidence":0.60,"ai_tool_available":True, "notes":"AIOps"},

    # CS-001 Customer Support Agent Tier 1
    {"role_id":"CS-001","task_name":"FAQ & common issue resolution",          "task_category":"Customer",   "time_pct":0.40,"automatable":True, "augmentable":True, "automation_confidence":0.85,"ai_tool_available":True, "notes":"AI chatbots handle >60% of tier-1"},
    {"role_id":"CS-001","task_name":"Ticket logging & categorisation",        "task_category":"Data entry", "time_pct":0.20,"automatable":True, "augmentable":False,"automation_confidence":0.90,"ai_tool_available":True, "notes":"Auto-categorisation"},
    {"role_id":"CS-001","task_name":"Order / account updates",                "task_category":"Data entry", "time_pct":0.20,"automatable":True, "augmentable":False,"automation_confidence":0.88,"ai_tool_available":True, "notes":"RPA + AI"},
    {"role_id":"CS-001","task_name":"Complex issue escalation",               "task_category":"Decision",   "time_pct":0.10,"automatable":False,"augmentable":True, "automation_confidence":0.25,"ai_tool_available":True, "notes":"AI routes; human resolves"},
    {"role_id":"CS-001","task_name":"Customer satisfaction follow-up",        "task_category":"Communication","time_pct":0.10,"automatable":True, "augmentable":True,"automation_confidence":0.70,"ai_tool_available":True, "notes":"Automated CSAT surveys"},

    # CS-002 Customer Success Manager
    {"role_id":"CS-002","task_name":"Customer health monitoring & QBRs",      "task_category":"Analysis",   "time_pct":0.30,"automatable":False,"augmentable":True, "automation_confidence":0.40,"ai_tool_available":True, "notes":"AI health scores; human presents"},
    {"role_id":"CS-002","task_name":"Renewal & expansion strategy",           "task_category":"Decision",   "time_pct":0.25,"automatable":False,"augmentable":True, "automation_confidence":0.20,"ai_tool_available":True, "notes":"Relationship-dependent"},
    {"role_id":"CS-002","task_name":"Onboarding programme delivery",          "task_category":"Communication","time_pct":0.20,"automatable":False,"augmentable":True,"automation_confidence":0.30,"ai_tool_available":True, "notes":"AI personalises; human delivers"},
    {"role_id":"CS-002","task_name":"Churn risk identification",              "task_category":"Analysis",   "time_pct":0.15,"automatable":True, "augmentable":True, "automation_confidence":0.72,"ai_tool_available":True, "notes":"ML churn prediction"},
    {"role_id":"CS-002","task_name":"CRM updates & activity logging",         "task_category":"Data entry", "time_pct":0.10,"automatable":True, "augmentable":False,"automation_confidence":0.80,"ai_tool_available":True, "notes":"AI auto-logging"},

    # CS-003 Technical Support Tier 2
    {"role_id":"CS-003","task_name":"Advanced technical troubleshooting",     "task_category":"Analysis",   "time_pct":0.40,"automatable":False,"augmentable":True, "automation_confidence":0.38,"ai_tool_available":True, "notes":"AI knowledge base; human solves"},
    {"role_id":"CS-003","task_name":"Known issue documentation",              "task_category":"Data entry", "time_pct":0.20,"automatable":True, "augmentable":True, "automation_confidence":0.72,"ai_tool_available":True, "notes":"AI drafts docs"},
    {"role_id":"CS-003","task_name":"Escalation to engineering",              "task_category":"Communication","time_pct":0.15,"automatable":False,"augmentable":True,"automation_confidence":0.25,"ai_tool_available":True, "notes":"Judgment required"},
    {"role_id":"CS-003","task_name":"Log analysis & diagnostics",             "task_category":"Analysis",   "time_pct":0.15,"automatable":True, "augmentable":True, "automation_confidence":0.68,"ai_tool_available":True, "notes":"AI log analysis"},
    {"role_id":"CS-003","task_name":"Customer communication & updates",       "task_category":"Customer",   "time_pct":0.10,"automatable":False,"augmentable":True, "automation_confidence":0.30,"ai_tool_available":True, "notes":"AI drafts; human sends"},

    # LEG-001 Paralegal
    {"role_id":"LEG-001","task_name":"Contract review & redlining",           "task_category":"Compliance", "time_pct":0.35,"automatable":True, "augmentable":True, "automation_confidence":0.65,"ai_tool_available":True, "notes":"Contract AI tools (Harvey, Kira)"},
    {"role_id":"LEG-001","task_name":"Legal research & precedent analysis",   "task_category":"Analysis",   "time_pct":0.25,"automatable":True, "augmentable":True, "automation_confidence":0.70,"ai_tool_available":True, "notes":"AI legal research tools"},
    {"role_id":"LEG-001","task_name":"Document management & filing",          "task_category":"Data entry", "time_pct":0.20,"automatable":True, "augmentable":False,"automation_confidence":0.85,"ai_tool_available":True, "notes":"Highly automatable"},
    {"role_id":"LEG-001","task_name":"Regulatory compliance tracking",        "task_category":"Compliance", "time_pct":0.12,"automatable":False,"augmentable":True, "automation_confidence":0.45,"ai_tool_available":True, "notes":"AI monitors; human interprets"},
    {"role_id":"LEG-001","task_name":"Due diligence support",                 "task_category":"Analysis",   "time_pct":0.08,"automatable":False,"augmentable":True, "automation_confidence":0.50,"ai_tool_available":True, "notes":"AI accelerates; human validates"},

    # LEG-002 Corporate Counsel
    {"role_id":"LEG-002","task_name":"Legal strategy & risk advisory",        "task_category":"Decision",   "time_pct":0.35,"automatable":False,"augmentable":True, "automation_confidence":0.12,"ai_tool_available":False,"notes":"Requires full judgment; high liability"},
    {"role_id":"LEG-002","task_name":"Contract negotiation",                  "task_category":"Decision",   "time_pct":0.25,"automatable":False,"augmentable":True, "automation_confidence":0.18,"ai_tool_available":True, "notes":"AI provides playbook; human negotiates"},
    {"role_id":"LEG-002","task_name":"Regulatory interpretation",             "task_category":"Compliance", "time_pct":0.20,"automatable":False,"augmentable":True, "automation_confidence":0.25,"ai_tool_available":True, "notes":"High liability; human essential"},
    {"role_id":"LEG-002","task_name":"Litigation support",                    "task_category":"Compliance", "time_pct":0.12,"automatable":False,"augmentable":True, "automation_confidence":0.30,"ai_tool_available":True, "notes":"AI e-discovery; human argues"},
    {"role_id":"LEG-002","task_name":"Board & executive advisory",            "task_category":"Communication","time_pct":0.08,"automatable":False,"augmentable":False,"automation_confidence":0.05,"ai_tool_available":False,"notes":"Senior judgment only"},

    # ITO-001 IT Help Desk
    {"role_id":"ITO-001","task_name":"Password reset & account unlocking",    "task_category":"Data entry", "time_pct":0.25,"automatable":True, "augmentable":False,"automation_confidence":0.95,"ai_tool_available":True, "notes":"Fully automatable with self-service"},
    {"role_id":"ITO-001","task_name":"Software installation & basic config",  "task_category":"Data entry", "time_pct":0.25,"automatable":True, "augmentable":True, "automation_confidence":0.80,"ai_tool_available":True, "notes":"Scripted automation"},
    {"role_id":"ITO-001","task_name":"Common technical issue resolution",     "task_category":"Customer",   "time_pct":0.25,"automatable":True, "augmentable":True, "automation_confidence":0.72,"ai_tool_available":True, "notes":"AI chatbot deflection"},
    {"role_id":"ITO-001","task_name":"Ticket routing & triage",               "task_category":"Data entry", "time_pct":0.15,"automatable":True, "augmentable":False,"automation_confidence":0.88,"ai_tool_available":True, "notes":"AI classification"},
    {"role_id":"ITO-001","task_name":"Hardware/device provisioning",          "task_category":"Data entry", "time_pct":0.10,"automatable":False,"augmentable":True, "automation_confidence":0.35,"ai_tool_available":False,"notes":"Physical activity required"},

    # ITO-002 Sys/Network Admin
    {"role_id":"ITO-002","task_name":"Server & infrastructure monitoring",    "task_category":"Analysis",   "time_pct":0.30,"automatable":True, "augmentable":True, "automation_confidence":0.78,"ai_tool_available":True, "notes":"AIOps monitoring tools"},
    {"role_id":"ITO-002","task_name":"Patch management",                      "task_category":"Data entry", "time_pct":0.25,"automatable":True, "augmentable":False,"automation_confidence":0.82,"ai_tool_available":True, "notes":"Automated patch orchestration"},
    {"role_id":"ITO-002","task_name":"Network configuration & management",    "task_category":"Creative",   "time_pct":0.20,"automatable":False,"augmentable":True, "automation_confidence":0.40,"ai_tool_available":True, "notes":"Intent-based networking emerging"},
    {"role_id":"ITO-002","task_name":"Security incident response",            "task_category":"Decision",   "time_pct":0.15,"automatable":False,"augmentable":True, "automation_confidence":0.35,"ai_tool_available":True, "notes":"SOAR tools assist; human decides"},
    {"role_id":"ITO-002","task_name":"Capacity planning",                     "task_category":"Analysis",   "time_pct":0.10,"automatable":True, "augmentable":True, "automation_confidence":0.72,"ai_tool_available":True, "notes":"ML-based forecasting"},

    # MKT-001 Content Writer
    {"role_id":"MKT-001","task_name":"Blog / article writing",                "task_category":"Creative",   "time_pct":0.35,"automatable":False,"augmentable":True, "automation_confidence":0.55,"ai_tool_available":True, "notes":"GenAI drafts; human edits & decides"},
    {"role_id":"MKT-001","task_name":"Social media content creation",         "task_category":"Creative",   "time_pct":0.25,"automatable":True, "augmentable":True, "automation_confidence":0.70,"ai_tool_available":True, "notes":"High AI confidence for standard posts"},
    {"role_id":"MKT-001","task_name":"Email copy & campaign writing",         "task_category":"Creative",   "time_pct":0.20,"automatable":True, "augmentable":True, "automation_confidence":0.72,"ai_tool_available":True, "notes":"AI personalisation at scale"},
    {"role_id":"MKT-001","task_name":"SEO research & optimisation",           "task_category":"Analysis",   "time_pct":0.12,"automatable":True, "augmentable":True, "automation_confidence":0.75,"ai_tool_available":True, "notes":"AI SEO tools mature"},
    {"role_id":"MKT-001","task_name":"Brand tone & creative strategy",        "task_category":"Decision",   "time_pct":0.08,"automatable":False,"augmentable":True, "automation_confidence":0.20,"ai_tool_available":False,"notes":"Requires human creative judgment"},

    # MKT-002 Digital Marketing Analyst
    {"role_id":"MKT-002","task_name":"Campaign performance analysis",         "task_category":"Analysis",   "time_pct":0.35,"automatable":True, "augmentable":True, "automation_confidence":0.78,"ai_tool_available":True, "notes":"AI-driven attribution"},
    {"role_id":"MKT-002","task_name":"A/B test design & analysis",            "task_category":"Analysis",   "time_pct":0.25,"automatable":False,"augmentable":True, "automation_confidence":0.50,"ai_tool_available":True, "notes":"AI optimises; human interprets"},
    {"role_id":"MKT-002","task_name":"Paid media bid management",             "task_category":"Data entry", "time_pct":0.20,"automatable":True, "augmentable":False,"automation_confidence":0.85,"ai_tool_available":True, "notes":"Programmatic advertising"},
    {"role_id":"MKT-002","task_name":"Reporting & dashboard creation",        "task_category":"Data entry", "time_pct":0.12,"automatable":True, "augmentable":False,"automation_confidence":0.82,"ai_tool_available":True, "notes":"BI automation"},
    {"role_id":"MKT-002","task_name":"Audience segmentation",                 "task_category":"Analysis",   "time_pct":0.08,"automatable":True, "augmentable":True, "automation_confidence":0.75,"ai_tool_available":True, "notes":"ML clustering"},

    # MKT-003 Brand / Marketing Manager
    {"role_id":"MKT-003","task_name":"Marketing strategy development",        "task_category":"Decision",   "time_pct":0.30,"automatable":False,"augmentable":True, "automation_confidence":0.15,"ai_tool_available":True, "notes":"AI provides insights; human decides"},
    {"role_id":"MKT-003","task_name":"Campaign planning & execution",         "task_category":"Creative",   "time_pct":0.25,"automatable":False,"augmentable":True, "automation_confidence":0.30,"ai_tool_available":True, "notes":"AI assists with personalisation"},
    {"role_id":"MKT-003","task_name":"Agency & vendor management",            "task_category":"Communication","time_pct":0.20,"automatable":False,"augmentable":False,"automation_confidence":0.08,"ai_tool_available":False,"notes":"Relationship management"},
    {"role_id":"MKT-003","task_name":"Budget allocation & tracking",          "task_category":"Data entry", "time_pct":0.15,"automatable":True, "augmentable":True, "automation_confidence":0.70,"ai_tool_available":True, "notes":"AI-driven attribution and budgeting"},
    {"role_id":"MKT-003","task_name":"Market research & competitive analysis","task_category":"Analysis",   "time_pct":0.10,"automatable":True, "augmentable":True, "automation_confidence":0.65,"ai_tool_available":True, "notes":"AI web scraping & synthesis"},

    # PRD-001 Product Manager
    {"role_id":"PRD-001","task_name":"Product strategy & roadmap planning",   "task_category":"Decision",   "time_pct":0.30,"automatable":False,"augmentable":True, "automation_confidence":0.12,"ai_tool_available":True, "notes":"Strategic judgment essential"},
    {"role_id":"PRD-001","task_name":"Customer & user research",              "task_category":"Analysis",   "time_pct":0.25,"automatable":False,"augmentable":True, "automation_confidence":0.35,"ai_tool_available":True, "notes":"AI summarises interviews; human interprets"},
    {"role_id":"PRD-001","task_name":"Requirement writing & PRDs",            "task_category":"Creative",   "time_pct":0.20,"automatable":False,"augmentable":True, "automation_confidence":0.45,"ai_tool_available":True, "notes":"AI drafts; human owns"},
    {"role_id":"PRD-001","task_name":"Sprint planning & backlog grooming",    "task_category":"Analysis",   "time_pct":0.15,"automatable":False,"augmentable":True, "automation_confidence":0.30,"ai_tool_available":True, "notes":"AI prioritises; PM decides"},
    {"role_id":"PRD-001","task_name":"Stakeholder alignment & communication", "task_category":"Communication","time_pct":0.10,"automatable":False,"augmentable":False,"automation_confidence":0.08,"ai_tool_available":False,"notes":"Relationship & leadership"},

    # PRD-002 UX Designer
    {"role_id":"PRD-002","task_name":"User research & usability testing",     "task_category":"Analysis",   "time_pct":0.30,"automatable":False,"augmentable":True, "automation_confidence":0.30,"ai_tool_available":True, "notes":"AI synthesises; human empathises"},
    {"role_id":"PRD-002","task_name":"Wireframing & prototyping",             "task_category":"Creative",   "time_pct":0.30,"automatable":False,"augmentable":True, "automation_confidence":0.40,"ai_tool_available":True, "notes":"AI design tools (Figma AI)"},
    {"role_id":"PRD-002","task_name":"Design system maintenance",             "task_category":"Data entry", "time_pct":0.20,"automatable":True, "augmentable":True, "automation_confidence":0.65,"ai_tool_available":True, "notes":"AI generates variants"},
    {"role_id":"PRD-002","task_name":"Accessibility review",                  "task_category":"Compliance", "time_pct":0.10,"automatable":True, "augmentable":True, "automation_confidence":0.72,"ai_tool_available":True, "notes":"Automated accessibility checkers"},
    {"role_id":"PRD-002","task_name":"Stakeholder design reviews",            "task_category":"Communication","time_pct":0.10,"automatable":False,"augmentable":False,"automation_confidence":0.10,"ai_tool_available":False,"notes":"Collaborative judgment"},

    # PRD-003 Technical Writer
    {"role_id":"PRD-003","task_name":"API & technical documentation",         "task_category":"Creative",   "time_pct":0.35,"automatable":True, "augmentable":True, "automation_confidence":0.68,"ai_tool_available":True, "notes":"AI generates doc from code comments"},
    {"role_id":"PRD-003","task_name":"User guides & help centre content",     "task_category":"Creative",   "time_pct":0.30,"automatable":True, "augmentable":True, "automation_confidence":0.72,"ai_tool_available":True, "notes":"GenAI high confidence"},
    {"role_id":"PRD-003","task_name":"Content review & editing",              "task_category":"Analysis",   "time_pct":0.20,"automatable":False,"augmentable":True, "automation_confidence":0.45,"ai_tool_available":True, "notes":"AI flags issues; human edits"},
    {"role_id":"PRD-003","task_name":"Doc structure & information architecture","task_category":"Creative", "time_pct":0.10,"automatable":False,"augmentable":True, "automation_confidence":0.30,"ai_tool_available":True, "notes":"Creative judgment"},
    {"role_id":"PRD-003","task_name":"SME interviews & knowledge capture",    "task_category":"Communication","time_pct":0.05,"automatable":False,"augmentable":True,"automation_confidence":0.20,"ai_tool_available":True, "notes":"AI transcribes; human interviews"},
]


# ══════════════════════════════════════════════════════════════════════════════
# BUILD DATAFRAMES
# ══════════════════════════════════════════════════════════════════════════════

def build_roles_df() -> pd.DataFrame:
    df = pd.DataFrame(ROLE_DEFINITIONS)
    df["hours_per_week"] = config.HOURS_PER_WEEK
    return df


def build_employees_df(roles_df: pd.DataFrame) -> pd.DataFrame:
    df = roles_df[["role_id", "num_employees", "avg_annual_salary_usd"]].copy()
    df.rename(columns={"num_employees": "total_headcount"}, inplace=True)
    df["benefits_load_pct"]         = config.BENEFITS_LOAD
    df["total_annual_labor_cost_usd"] = (
        df["total_headcount"] * df["avg_annual_salary_usd"] * (1 + config.BENEFITS_LOAD)
    ).round(0)
    df["productive_hours_per_year"] = config.HOURS_PER_WEEK * config.WORKING_WEEKS
    df["cost_per_productive_hour"]  = (
        df["total_annual_labor_cost_usd"] / (df["total_headcount"] * df["productive_hours_per_year"])
    ).round(2)
    return df


def build_tasks_df() -> pd.DataFrame:
    df = pd.DataFrame(TASK_DEFINITIONS)
    # Add a unique task_id
    df.insert(0, "task_id", ["TSK-" + str(i+1).zfill(3) for i in range(len(df))])
    return df


def build_ai_assumptions_df(roles_df: pd.DataFrame) -> pd.DataFrame:
    records = [compute_ai_assumptions(r) for r in ROLE_DEFINITIONS]
    return pd.DataFrame(records)


# ══════════════════════════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════════════════════════

def validate_datasets(roles_df, employees_df, tasks_df, ai_df):
    errors = []

    # 1. All role_ids consistent across tables
    role_ids = set(roles_df["role_id"])
    for name, df in [("employees", employees_df), ("ai_assumptions", ai_df)]:
        missing = set(df["role_id"]) - role_ids
        if missing:
            errors.append(f"{name}: unknown role_ids {missing}")

    # 2. Task time_pct sums to 1.0 per role (±0.01 tolerance)
    sums = tasks_df.groupby("role_id")["time_pct"].sum()
    bad  = sums[abs(sums - 1.0) > 0.01]
    if not bad.empty:
        errors.append(f"Tasks time_pct does not sum to 1.0 for: {bad.to_dict()}")

    # 3. automation_potential + augmentation_potential <= 1.0
    combined = ai_df["automation_potential_pct"] + ai_df["augmentation_potential_pct"]
    if (combined > 1.0).any():
        errors.append("automation + augmentation > 1.0 for some roles")

    # 4. No negative labor costs
    if (employees_df["total_annual_labor_cost_usd"] <= 0).any():
        errors.append("Non-positive labor costs found")

    if errors:
        for e in errors:
            print(f"  [VALIDATION ERROR] {e}")
        raise ValueError("Dataset validation failed. See errors above.")
    else:
        print("  [VALIDATION OK] All dataset checks passed.")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    utils.section("01 — DATA GENERATION")

    utils.ensure_dirs()

    print("\nBuilding datasets...")
    roles_df    = build_roles_df()
    employees_df= build_employees_df(roles_df)
    tasks_df    = build_tasks_df()
    ai_df       = build_ai_assumptions_df(roles_df)

    print("\nRunning validation...")
    validate_datasets(roles_df, employees_df, tasks_df, ai_df)

    # Save CSVs
    roles_df.to_csv(os.path.join(config.DATA_RAW, "roles.csv"), index=False)
    employees_df.to_csv(os.path.join(config.DATA_RAW, "employees.csv"), index=False)
    tasks_df.to_csv(os.path.join(config.DATA_RAW, "tasks.csv"), index=False)
    ai_df.to_csv(os.path.join(config.DATA_RAW, "ai_assumptions.csv"), index=False)

    utils.subsection("Dataset Summary")
    print(f"  Roles:         {len(roles_df):>4} records across {roles_df['function'].nunique()} functions")
    print(f"  Employees:     {len(employees_df):>4} records")
    print(f"  Tasks:         {len(tasks_df):>4} records")
    print(f"  AI Assumptions:{len(ai_df):>4} records")
    print(f"\n  Total headcount: {roles_df['num_employees'].sum():,}")
    total_cost = employees_df["total_annual_labor_cost_usd"].sum()
    print(f"  Total annual labor cost: {utils.fmt_usd(total_cost)}")
    print(f"\n  Raw CSVs saved to: {config.DATA_RAW}")


if __name__ == "__main__":
    main()
