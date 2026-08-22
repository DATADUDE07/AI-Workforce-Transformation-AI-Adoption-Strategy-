# AI Workforce Transformation Analytics

> **A Decision Analytics portfolio project** demonstrating end-to-end analytical thinking across AI automation strategy, workforce economics, and implementation planning for a simulated large technology company (~2,900 employees, ~$373M annual labor cost).

> **Disclaimer**: All data is synthetic and derived from publicly available benchmarks (BLS OES, Glassdoor, McKinsey, MIT/Stanford research). This project does not represent any real company's data or plans.

---

## Project Overview

This project answers a high-stakes business question:

> *"Which roles/tasks should be automated by AI first, which should be augmented, and what is the estimated financial impact — with quantified risk?"*

The analysis produces a full decision recommendation — including phased rollout, ROI, sensitivity analysis, and governance flags — across 29 workforce roles and 145 tasks.

---

## Key Findings

| Metric | Value |
|--------|-------|
| Total workforce analysed | 2,932 FTE |
| Total annual labour cost | \$373M |
| Automatable cost pool (moderate scenario) | \$98M (26% of labour cost) |
| Estimated net annual savings (moderate) | \$61M |
| Portfolio Year-1 ROI (moderate) | ~94% |
| Payback period (moderate) | ~13 months |
| 3-year NPV (moderate, 10% discount) | ~\$146M |
| AAPS minimum Spearman ρ (sensitivity) | 0.969 — rankings robust |

**Top Phase 1 roles (by AAPS)**:
1. Software Engineer — AAPS: 0.705 (largest cost pool × high AI readiness)
2. Customer Support Agent Tier 1 — AAPS: 0.688 (72% repetitive, chatbot-ready)
3. QA / Test Engineer — AAPS: 0.650 (62% repetitive, mature AI tooling)

---

## Analytical Framework

### AI Adoption Priority Score (AAPS)

```
AAPS = 0.25 × Automation_Potential
     + 0.25 × Cost_Saving_Potential
     + 0.15 × Productivity_Improvement
     + 0.15 × Implementation_Feasibility
     + 0.10 × (1 − Quality_Risk)
     + 0.10 × (1 − Human_Judgment_Requirement)
```

All factors min-max normalised. Weights justified in `config.py` with sensitivity analysis confirming robustness.

### Risk Score

```
Risk = 0.40 × Quality_Risk + 0.30 × Regulatory_Sensitivity
     + 0.20 × Customer_Impact + 0.10 × Change_Mgmt_Complexity
```

### Scenario Analysis

| Scenario | Adoption Rate | Net Annual Benefit | Payback |
|----------|--------------|-------------------|---------|
| Conservative | 40% | ~\$36M | ~24 mo |
| Moderate ★ | 65% | ~\$61M | ~13 mo |
| Aggressive | 85% | ~\$79M | ~10 mo |

★ Recommended — best risk-adjusted efficiency ratio.

---

## Project Structure

```
ai_workforce_analytics/
├── data/
│   ├── raw/                  # 4 synthetic CSVs (roles, employees, tasks, ai_assumptions)
│   ├── processed/            # Enriched master, scoring output, scenario results
│   └── ai_workforce.db       # SQLite database
├── notebooks/
│   ├── 01_data_generation.py     # 29 roles × 145 tasks, logic-derived not random
│   ├── 02_data_cleaning_eda.py   # QA checks, correlation analysis, anomaly detection
│   ├── 03_sql_analysis.py        # 15 business SQL queries (CTEs, window fns, CASE WHEN)
│   ├── 04_scoring_framework.py   # AAPS scoring, RAG flags, phase assignment
│   ├── 05_scenario_analysis.py   # 3-scenario financial modelling with validation
│   ├── 06_sensitivity_analysis.py# 12 weight perturbations, Spearman rank correlation
│   ├── 07_visualizations.py      # 9 business-focused matplotlib charts
│   └── 08_excel_export.py        # 8-sheet Excel workbook with RAG formatting
├── outputs/
│   ├── charts/               # 9 PNG charts (+ EDA correlation heatmap)
│   └── AI_Workforce_Strategy.xlsx  # Final business deliverable
├── config.py                 # All weights, assumptions, scenario parameters
├── utils.py                  # Shared helpers (normalisation, ROI, NPV, RAG)
├── main.py                   # Full pipeline orchestrator
└── README.md
```

---

## SQL Analysis (15 Queries)

SQL features demonstrated: `JOIN`, `GROUP BY`, `CASE WHEN`, CTEs, subqueries, `UNION ALL`, window functions (`SUM() OVER`, `RANK() OVER`, `NTILE() OVER`).

| # | Business Question | SQL Features |
|---|------------------|-------------|
| Q1 | Labor cost by department | GROUP BY, SUM, subquery for % share |
| Q2 | Top 10 highest-cost roles | ORDER BY, LIMIT |
| Q3 | Salary by role level | CASE WHEN ordering |
| Q4 | Automation potential by function | AVG, CASE WHEN tier labels |
| Q5 | Headcount concentration | Window: SUM() OVER() |
| Q6 | Automatable cost pool by dept | 3-table JOIN, derived column |
| Q7 | Highest AI opportunity roles | Subquery, composite sort |
| Q8 | Productivity before/after AI | CASE WHEN, computed columns |
| Q9 | Scenario savings comparison | CTE + UNION ALL |
| Q10 | ROI ranking | CTE + RANK() OVER |
| Q11 | Risk-opportunity matrix | CASE WHEN quadrant classification |
| Q12 | Phase assignment | NTILE(3) OVER |
| Q13 | Break-even analysis | Subquery filter on payback |
| Q14 | Auto vs augment split per domain | Conditional aggregation |
| Q15 | Top 5 by 3-year NPV | CTE NPV formula + RANK() OVER |

---

## Visualizations

1. Labor cost by department (horizontal bar)
2. AI automation potential by function (grouped bar)
3. Cost savings vs implementation cost (bubble chart)
4. Productivity improvement by role (horizontal bar)
5. AAPS ranking — all 29 roles (RAG-coloured bar)
6. Automation potential vs human judgment (scatter quadrant)
7. Scenario savings by department (grouped bar)
8. ROI vs implementation complexity (scatter quadrant)
9. Risk vs AI opportunity (2×2 matrix)
10. EDA: Correlation heatmap (bonus)
11. Sensitivity: Tornado chart (worst-case Spearman ρ)

---

## Excel Deliverable (8 Sheets)

| Sheet | Contents |
|-------|----------|
| 1. Executive Summary | KPI tiles, scenario comparison, key findings, embedded matrix chart |
| 2. Workforce & Cost | Full role/cost table, department subtotals, embedded chart |
| 3. AI Automation Analysis | Automation/augmentation/readiness by role, classification colour-coding |
| 4. Role & Task Scoring | Full AAPS table, factor breakdown, RAG flags |
| 5. Scenario Analysis | Parameter table, company-level summary, per-role moderate results |
| 6. ROI & Savings | ROI ranking, payback period (RAG coloured), NPV, embedded charts |
| 7. AI Priority Matrix | Quadrant classification, phase plan, sensitivity tornado |
| 8. Recommendations | Structured action table with phase/owner/timeline/savings |

---

## Technology Stack

| Technology | Purpose |
|------------|---------|
| Python 3.x | Core language |
| pandas | Data loading, cleaning, merging, analysis |
| NumPy | Normalisation, array operations, seeded random |
| SQLite / sqlite3 | Portable relational database, 15 SQL queries |
| matplotlib | 9 + 2 business-focused charts |
| scipy.stats | Spearman rank correlation for sensitivity analysis |
| openpyxl | 8-sheet Excel workbook with RAG formatting and embedded images |

---

## Data Provenance

| Source | Used For |
|--------|---------|
| BLS Occupational Employment Statistics (2023) | Salary range anchoring |
| Glassdoor / LinkedIn Salary Insights (2023–24) | Salary validation |
| McKinsey Global Institute "A Future That Works" (2023) | Automation potential benchmarks |
| MIT/Stanford GitHub Copilot studies (2022–24) | Productivity uplift for engineering roles |
| Oxford Martin School Frey & Osborne (2013, updated) | Task-level automability framework |
| All headcounts, exact salaries, potentials | **Synthetic** — illustrative only |

---

## Limitations

1. All quantitative outputs are synthetic illustrations, not real-company forecasts
2. Automation potentials are modelled at a point in time; AI capability evolves rapidly
3. Productivity uplift estimates vary significantly by implementation quality
4. NPV uses a fixed 10% discount rate; adjust for your organisation's WACC
5. No change management cost is modelled beyond a complexity factor

---

## Resume Output

### Project Title
**AI Workforce Transformation Analytics: Decision Framework for Enterprise AI Adoption Strategy**

### Resume Bullets (3–4)
- Built an end-to-end Decision Analytics pipeline in Python (pandas, NumPy, SQLite, matplotlib, openpyxl) modelling AI automation strategy across 29 workforce roles, 145 tasks, and \$373M in annual labour cost for a simulated ~3,000-person technology company
- Designed a transparent AI Adoption Priority Score (AAPS) from six weighted factors (automation potential, cost savings, productivity, feasibility, quality risk, human judgment) with min-max normalisation; validated robustness via 12-perturbation sensitivity analysis achieving Spearman ρ ≥ 0.969 across all weight variations
- Quantified \$61M in estimated net annual savings under the recommended moderate AI scenario (65% adoption, 24-month rollout), with a 13-month payback period and \$146M 3-year NPV at 10% discount rate; delivered findings in a 15-query SQLite analytical layer and an 8-sheet RAG-formatted Excel executive workbook
- Developed phased implementation recommendations (Phase 1: Customer Support + Finance Ops; Phase 2: Engineering QA + BI + SDR; Phase 3: Software Engineering + Data & Analytics) with per-role ROI, risk scores, and governance flags distinguishing Full Automation, AI Augmentation, and Low AI Suitability categories

### Interview Explanation (30 seconds)
> "I built a complete Decision Analytics project to simulate how a large tech company should prioritise AI adoption across its workforce. I modelled 29 roles and 145 tasks with a transparent scoring system — the AI Adoption Priority Score — that weighs automation potential, cost savings, productivity uplift, feasibility, quality risk, and human judgment requirements. I ran three adoption scenarios, validated the rankings with a sensitivity analysis confirming they're robust to weight changes, and packaged everything into a business-facing Excel workbook. The key finding is that the moderate scenario — 65% adoption over 24 months — delivers \$61M in annual savings with a 13-month payback, while avoiding high-risk automation in customer-facing and regulatory roles."

### Likely Interviewer Questions & Answers

**Q: How did you choose the AAPS weights?**
> The weights are not arbitrary — they reflect a deliberate logic. Automation potential and cost-saving potential each get 25% because they represent feasibility and value: no automation strategy works without both. Productivity improvement and implementation feasibility each get 15% as secondary amplifiers. Quality risk and human judgment each get 10% as downside modifiers. I then validated that the ranking is robust to ±10 percentage point changes in each weight using Spearman rank correlation, getting a minimum ρ of 0.969 — meaning the conclusions hold regardless of reasonable weight disagreements.

**Q: Why not just automate the highest-salary roles first?**
> That's a common mistake. High salary doesn't automatically mean high automation potential. Corporate Counsel earns \$210K but has 0.92 decision intensity, 0.95 regulatory sensitivity, and 0.13 automation potential — automating that role creates legal liability. The AP/AR Clerk earns \$58K but has 0.88 task repetitiveness and 0.92 automation confidence with mature OCR and AI tools. The AAPS framework captures this interaction between salary, volume, repetitiveness, risk, and AI readiness.

**Q: How did you validate your savings figures?**
> I built in an explicit constraint check: labor savings cannot exceed the total labor cost. The scenario model is formulated so that savings = total_cost × automation_potential × adoption_rate — where adoption_rate is always ≤ 1.0. I also distinguish between labor savings (cost reduction) and productivity gain value (output increase), so the two don't overlap. Every formula is documented inline in the code.

**Q: What would you need to make this a real business recommendation?**
> Real HR headcount data and salary bands, time-motion studies or activity logs per role, historical error rates, vendor quotes for specific AI tools, a change management readiness assessment, and regulatory compliance review per function — especially in Finance and Legal.

**Q: What is the difference between automation and augmentation in your model?**
> Automation means AI replaces the human for that task — high repetitiveness, high AI tool maturity, low judgment requirement. Augmentation means AI assists but the human decides and owns the outcome — applicable to roles with high decision intensity, high regulatory sensitivity, or high customer relationship value. The distinction matters for headcount planning: automation may reduce FTE requirements, while augmentation increases output per FTE without changing headcount.

---

## Running the Project

```bash
# Install dependencies
pip install pandas numpy matplotlib scipy openpyxl

# Run full pipeline (generates all data, SQL, charts, and Excel)
python main.py
```

**Output files**:
- `data/raw/` — 4 synthetic CSVs
- `data/processed/` — enriched data, scoring, scenarios, sensitivity results
- `data/ai_workforce.db` — SQLite database
- `outputs/charts/` — 11 PNG charts
- `outputs/AI_Workforce_Strategy.xlsx` — final 8-sheet Excel deliverable
