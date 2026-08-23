# AI Workforce Transformation Analytics

> **A Decision Analytics portfolio project** demonstrating end-to-end analytical thinking across AI automation strategy, workforce economics, and implementation planning for a simulated large technology company (~2,932 employees, ~$373M annual labor cost).

> **Disclaimer**: All data is synthetic and derived from publicly available benchmarks (BLS OES, Glassdoor, McKinsey, MIT/Stanford research). This project does not represent any real company's data or plans.

**Author:** Sahil Saurav &nbsp;|&nbsp; **GitHub:** [DATADUDE07](https://github.com/DATADUDE07)

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
1. AP / AR Clerk — AAPS: 0.702 (88% repetitive, OCR + AI tools mature)
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

All factors min-max normalised to [0, 1]. Weights justified in `config.py` with sensitivity analysis confirming robustness.

### Risk Score

```
Risk = 0.40 × Quality_Risk + 0.30 × Regulatory_Sensitivity
     + 0.20 × Customer_Impact + 0.10 × Change_Mgmt_Complexity
```

### RAG Thresholds

| Status | AAPS | Risk Score | Payback |
|--------|------|------------|---------|
| 🟢 Green | > 0.70 | < 0.40 | < 12 months |
| 🟡 Amber | 0.40–0.70 | 0.40–0.65 | 12–24 months |
| 🔴 Red | < 0.40 | > 0.65 | > 24 months |

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
├── dataset/                  # Additional dataset exports and references
├── scripts/
│   ├── 01_data_generation.py         # 29 roles × 145 tasks, logic-derived not random
│   ├── 02_data_cleaning_eda.py       # QA checks, correlation analysis, anomaly detection
│   ├── 03_sql_analysis.py            # 15 business SQL queries (CTEs, window fns, CASE WHEN)
│   ├── 04_scoring_framework.py       # AAPS scoring, RAG flags, phase assignment
│   ├── 05_scenario_analysis.py       # 3-scenario financial modelling with validation
│   ├── 06_sensitivity_analysis.py    # 12 weight perturbations, Spearman rank correlation
│   ├── 07_visualizations.py          # 15 business-focused matplotlib charts
│   ├── 08_excel_export.py            # 8-sheet Excel workbook with RAG formatting
│   ├── 09_ai_cost_viability_analysis.py  # AI vs human cost parity & efficiency analysis
│   └── 10_add_cost_viability_sheet.py    # Appends cost viability sheet to Excel workbook
├── SQL Queries/              # Standalone SQL query files for reference
├── outputs/
│   ├── charts/               # 15 PNG charts (see Visualizations section)
│   ├── AI_Workforce_Strategy.xlsx              # 8-sheet Excel executive workbook
│   ├── AI_Workforce_Report_Formatted.pdf       # Full formatted PDF report
│   └── AI_Workforce_Transformation_Presentation.pptx  # 14-slide PowerPoint deck
├── config.py                 # All weights, assumptions, scenario parameters
├── utils.py                  # Shared helpers (normalisation, ROI, NPV, RAG)
├── main.py                   # Full pipeline orchestrator
├── generate_pptx.py          # PowerPoint presentation generator (python-pptx)
├── generate_pdf_report.py    # PDF report generator
├── add_cost_viability_sheet.py
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

## Visualizations (15 Charts)

| # | Chart | Type |
|---|-------|------|
| 00 | EDA Correlation Heatmap | Heatmap |
| 01 | Labor Cost by Department | Horizontal bar |
| 02 | AI Automation Potential by Function | Grouped bar |
| 03 | Cost Savings vs Implementation Cost | Bubble chart |
| 04 | Productivity Improvement by Role | Horizontal bar |
| 05 | AAPS Ranking — All 29 Roles | RAG-coloured bar |
| 06 | Automation Potential vs Human Judgment | Scatter quadrant |
| 06b | Sensitivity Tornado Chart | Tornado / horizontal bar |
| 07 | Scenario Savings by Department | Grouped bar |
| 08 | ROI vs Implementation Complexity | Scatter quadrant |
| 09 | Risk vs AI Opportunity (2×2 matrix) | Scatter quadrant |
| 10 | AI Cost Efficiency Ratio | Bar chart |
| 11 | Cost Parity Threshold by Role | Bar chart |
| 12 | AI Cost Sensitivity Analysis | Line chart |
| 13 | Human vs AI Cost per Hour | Comparative bar |

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
| 9. AI Cost Viability | Human vs AI cost comparison, parity thresholds, efficiency ratios |

---

## PowerPoint Presentation (14 Slides)

Generated via `generate_pptx.py` using `python-pptx`. Each slide uses the project brand palette and embeds actual chart images.

| Slide | Title |
|-------|-------|
| 1 | Title — Sahil Saurav · GitHub: DATADUDE07 |
| 2 | Agenda |
| 3 | Project Overview & Business Problem |
| 4 | Dataset Architecture & Schema Design |
| 5 | AI Classification Framework |
| 6 | AI Adoption Priority Score (AAPS) |
| 7 | Workforce & Cost Analysis |
| 8 | SQL Analysis — 15 Business Queries |
| 9 | Scenario Analysis (Conservative / Moderate / Aggressive) |
| 10 | Sensitivity Analysis & Robustness |
| 11 | Key Visualisations |
| 12 | Recommendations & Implementation Roadmap |
| 13 | Limitations, Risks & Next Steps |
| 14 | Closing / Thank You |

---

## AI Cost Viability Analysis (Scripts 09 & 10)

An additional analytical layer examining the economic breakeven between human labour and AI tooling costs.

**Key outputs:**
- **AI Cost Efficiency Ratio** — net benefit per dollar of AI investment by role
- **Cost Parity Threshold** — the automation adoption rate at which AI breaks even vs human cost
- **Human vs AI Cost per Hour** — side-by-side cost comparison across all roles
- **AI Cost Sensitivity** — how net savings change as ongoing AI costs scale up

These findings are appended as a dedicated sheet in the Excel workbook via `10_add_cost_viability_sheet.py`.

---

## Technology Stack

| Technology | Purpose |
|------------|---------|
| Python 3.x | Core language |
| pandas | Data loading, cleaning, merging, analysis |
| NumPy | Normalisation, array operations, seeded random |
| SQLite / sqlite3 | Portable relational database, 15 SQL queries |
| matplotlib | 15 business-focused charts |
| scipy.stats | Spearman rank correlation for sensitivity analysis |
| openpyxl | 8-sheet Excel workbook with RAG formatting and embedded images |
| python-pptx | 14-slide PowerPoint presentation generator |

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
6. AI tooling cost assumptions may understate vendor price escalation over time

---

## Running the Project

```bash
# Install dependencies
pip install pandas numpy matplotlib scipy openpyxl python-pptx

# Run full pipeline (generates all data, SQL, charts, and Excel)
python main.py

# Generate PowerPoint presentation
python generate_pptx.py

# Generate PDF report
python generate_pdf_report.py

# Add AI Cost Viability sheet to Excel (run after main.py)
python add_cost_viability_sheet.py
```

**Output files**:
- `data/raw/` — 4 synthetic CSVs
- `data/processed/` — enriched data, scoring, scenarios, sensitivity results
- `data/ai_workforce.db` — SQLite database
- `outputs/charts/` — 15 PNG charts
- `outputs/AI_Workforce_Strategy.xlsx` — 8-sheet RAG-formatted Excel workbook
- `outputs/AI_Workforce_Report_Formatted.pdf` — full formatted PDF report
- `outputs/AI_Workforce_Transformation_Presentation.pptx` — 14-slide PowerPoint deck
