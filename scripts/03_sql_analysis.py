"""
03_sql_analysis.py
------------------
Creates the SQLite database ai_workforce.db, loads all four tables,
then executes 15 analytical SQL queries answering real business questions.

Libraries:
  sqlite3  — built-in; no external dependency
  pandas   — load results into DataFrames for display / downstream use

SQL features used per query are documented inline.
"""

import os
import sys
import sqlite3
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

utils.ensure_dirs()


# ══════════════════════════════════════════════════════════════════════════════
# DATABASE SETUP
# ══════════════════════════════════════════════════════════════════════════════

def init_db():
    """Create SQLite DB and load all four tables from processed / raw CSVs."""
    conn = sqlite3.connect(config.DB_PATH)

    # Load CSVs
    roles    = pd.read_csv(os.path.join(config.DATA_RAW, "roles.csv"))
    emp      = pd.read_csv(os.path.join(config.DATA_RAW, "employees.csv"))
    tasks    = pd.read_csv(os.path.join(config.DATA_RAW, "tasks.csv"))
    ai       = pd.read_csv(os.path.join(config.DATA_RAW, "ai_assumptions.csv"))
    enriched = pd.read_csv(os.path.join(config.DATA_PROC, "roles_enriched.csv"))

    # Write to SQLite
    roles.to_sql("roles",        conn, if_exists="replace", index=False)
    emp.to_sql("employees",      conn, if_exists="replace", index=False)
    tasks.to_sql("tasks",        conn, if_exists="replace", index=False)
    ai.to_sql("ai_assumptions",  conn, if_exists="replace", index=False)
    enriched.to_sql("master",    conn, if_exists="replace", index=False)

    conn.execute("PRAGMA journal_mode=WAL;")
    conn.commit()
    print(f"  Database initialised: {config.DB_PATH}")
    print(f"  Tables: roles, employees, tasks, ai_assumptions, master")
    return conn


# ══════════════════════════════════════════════════════════════════════════════
# QUERY RUNNER
# ══════════════════════════════════════════════════════════════════════════════

def run_query(conn, label: str, sql: str, narrative: str = "") -> pd.DataFrame:
    """Execute a SQL query, print results with label and business narrative."""
    utils.subsection(label)
    if narrative:
        print(f"  Business question: {narrative}")
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))
    return df


# ══════════════════════════════════════════════════════════════════════════════
# 15 ANALYTICAL SQL QUERIES
# ══════════════════════════════════════════════════════════════════════════════

QUERIES = {

    # -- Q1: Total labor cost by department -----------------------------------
    # Features: GROUP BY, SUM, ROUND, ORDER BY, subquery for % share
    "Q1_cost_by_department": (
        """
        SELECT
            r.function                                                  AS Department,
            COUNT(r.role_id)                                            AS Roles,
            SUM(r.num_employees)                                        AS Headcount,
            ROUND(SUM(e.total_annual_labor_cost_usd) / 1e6, 2)         AS Total_Cost_MUSD,
            ROUND(
                SUM(e.total_annual_labor_cost_usd) * 100.0 /
                (SELECT SUM(total_annual_labor_cost_usd) FROM employees), 1
            )                                                           AS Cost_Share_Pct
        FROM roles r
        JOIN employees e ON r.role_id = e.role_id
        GROUP BY r.function
        ORDER BY Total_Cost_MUSD DESC
        """,
        "Which departments represent the largest share of total labor cost?"
    ),

    # -- Q2: Top 10 highest-cost roles ----------------------------------------
    # Features: JOIN, ORDER BY, LIMIT
    "Q2_top10_cost_roles": (
        """
        SELECT
            r.role_name                                                  AS Role,
            r.function                                                   AS Department,
            r.num_employees                                              AS Headcount,
            r.avg_annual_salary_usd                                      AS Avg_Salary_USD,
            ROUND(e.total_annual_labor_cost_usd / 1e6, 2)               AS Total_Cost_MUSD
        FROM roles r
        JOIN employees e ON r.role_id = e.role_id
        ORDER BY e.total_annual_labor_cost_usd DESC
        LIMIT 10
        """,
        "Which individual roles carry the highest absolute labor cost burden?"
    ),

    # -- Q3: Average salary by role level -------------------------------------
    # Features: GROUP BY, AVG, CASE WHEN for ordering
    "Q3_avg_salary_by_level": (
        """
        SELECT
            role_level                                   AS Level,
            COUNT(*)                                     AS Roles,
            ROUND(AVG(avg_annual_salary_usd), 0)         AS Avg_Salary_USD,
            MIN(avg_annual_salary_usd)                   AS Min_Salary_USD,
            MAX(avg_annual_salary_usd)                   AS Max_Salary_USD
        FROM roles
        GROUP BY role_level
        ORDER BY
            CASE role_level
                WHEN 'Junior'   THEN 1
                WHEN 'Mid'      THEN 2
                WHEN 'Senior'   THEN 3
                WHEN 'Manager'  THEN 4
                WHEN 'Director' THEN 5
            END
        """,
        "How does average salary vary across role levels?"
    ),

    # -- Q4: Automation potential by function ----------------------------------
    # Features: JOIN, GROUP BY, AVG, CASE WHEN for tier labelling, ORDER BY
    "Q4_automation_by_function": (
        """
        SELECT
            r.function                                            AS Department,
            ROUND(AVG(a.automation_potential_pct) * 100, 1)      AS Avg_Auto_Pct,
            ROUND(AVG(a.augmentation_potential_pct) * 100, 1)    AS Avg_Aug_Pct,
            ROUND(AVG(r.ai_maturity_readiness) * 100, 1)         AS Avg_AI_Readiness_Pct,
            CASE
                WHEN AVG(a.automation_potential_pct) >= 0.60 THEN 'High'
                WHEN AVG(a.automation_potential_pct) >= 0.40 THEN 'Medium'
                ELSE 'Low'
            END                                                   AS Auto_Tier
        FROM roles r
        JOIN ai_assumptions a ON r.role_id = a.role_id
        GROUP BY r.function
        ORDER BY Avg_Auto_Pct DESC
        """,
        "Which business functions have the highest average AI automation potential?"
    ),

    # -- Q5: Employee concentration (% of headcount per domain) ---------------
    # Features: Window function SUM() OVER(), ROUND, ORDER BY
    "Q5_headcount_concentration": (
        """
        SELECT
            r.function                                               AS Department,
            SUM(r.num_employees)                                     AS Headcount,
            ROUND(
                SUM(r.num_employees) * 100.0 / SUM(SUM(r.num_employees)) OVER (), 1
            )                                                        AS Headcount_Share_Pct,
            ROUND(
                SUM(r.num_employees) * 100.0 / SUM(SUM(r.num_employees)) OVER (), 1
            )                                                        AS Cumulative_Pct
        FROM roles r
        GROUP BY r.function
        ORDER BY Headcount DESC
        """,
        "Where are employees concentrated? High headcount domains with high automation potential are priority targets."
    ),

    # -- Q6: Automatable labor cost pool by function ---------------------------
    # Features: JOIN (3 tables), GROUP BY, derived column, ROUND
    "Q6_automatable_cost_by_function": (
        """
        SELECT
            r.function                                                     AS Department,
            SUM(r.num_employees)                                           AS Headcount,
            ROUND(SUM(e.total_annual_labor_cost_usd) / 1e6, 2)            AS Total_Cost_MUSD,
            ROUND(SUM(e.total_annual_labor_cost_usd * a.automation_potential_pct) / 1e6, 2)
                                                                           AS Automatable_Cost_MUSD,
            ROUND(
                SUM(e.total_annual_labor_cost_usd * a.automation_potential_pct) * 100.0 /
                SUM(e.total_annual_labor_cost_usd), 1
            )                                                              AS Automatable_Pct
        FROM roles r
        JOIN employees e         ON r.role_id = e.role_id
        JOIN ai_assumptions a    ON r.role_id = a.role_id
        GROUP BY r.function
        ORDER BY Automatable_Cost_MUSD DESC
        """,
        "What is the maximum theoretical dollar value of automatable labor cost by department?"
    ),

    # -- Q7: Roles with highest AI Adoption Priority Score (AAPS) -------------
    # Features: Subquery, derived AAPS formula, ORDER BY, LIMIT
    # Note: AAPS uses pre-computed values from master table (normalisation done in Python)
    "Q7_top_aaps_roles": (
        """
        SELECT
            role_name                                             AS Role,
            function                                              AS Department,
            ROUND(automation_potential_pct * 100, 1)             AS Auto_Pct,
            ROUND(automatable_labor_cost_usd / 1e6, 2)           AS Auto_Cost_Pool_MUSD,
            ROUND(ai_productivity_uplift_pct * 100, 1)           AS Productivity_Uplift_Pct,
            ROUND(risk_score, 3)                                  AS Risk_Score,
            ai_classification                                     AS AI_Category
        FROM master
        ORDER BY automatable_labor_cost_usd DESC, automation_potential_pct DESC
        LIMIT 12
        """,
        "Which roles offer the highest automation value and productivity uplift?"
    ),

    # -- Q8: Productivity before vs after AI (moderate scenario) --------------
    # Features: CASE WHEN, derived columns, JOIN
    "Q8_productivity_before_after": (
        """
        SELECT
            r.role_name                                             AS Role,
            r.function                                              AS Department,
            e.productive_hours_per_year                             AS Hours_Per_Person,
            ROUND(e.cost_per_productive_hour, 0)                    AS Cost_Per_Hour_Before,
            ROUND(
                e.cost_per_productive_hour / (1 + a.ai_productivity_uplift_pct *
                    0.75),   -- 0.75 = moderate scenario productivity multiplier
                0
            )                                                       AS Cost_Per_Hour_After,
            ROUND(a.ai_productivity_uplift_pct * 75, 1)            AS Effective_Uplift_Pct,
            CASE
                WHEN a.ai_productivity_uplift_pct * 0.75 >= 0.30 THEN 'High Impact'
                WHEN a.ai_productivity_uplift_pct * 0.75 >= 0.15 THEN 'Medium Impact'
                ELSE 'Low Impact'
            END                                                     AS Productivity_Category
        FROM roles r
        JOIN employees e       ON r.role_id = e.role_id
        JOIN ai_assumptions a  ON r.role_id = a.role_id
        ORDER BY a.ai_productivity_uplift_pct DESC
        """,
        "How does cost-per-productive-hour change under the moderate AI scenario?"
    ),

    # -- Q9: Scenario-level cost savings comparison (CTE + UNION ALL) ---------
    # Features: CTE, UNION ALL, aggregation across scenarios
    "Q9_scenario_savings": (
        """
        WITH conservative AS (
            SELECT
                'Conservative' AS Scenario,
                ROUND(SUM(e.total_annual_labor_cost_usd * a.automation_potential_pct * 0.40) / 1e6, 2) AS Labor_Savings_MUSD,
                ROUND(SUM(a.implementation_cost_usd * 1.20) / 1e6, 2)  AS Impl_Cost_MUSD,
                ROUND(SUM(a.ongoing_ai_cost_per_year_usd) / 1e6, 2)     AS Ongoing_Cost_MUSD
            FROM employees e
            JOIN ai_assumptions a ON e.role_id = a.role_id
        ),
        moderate AS (
            SELECT
                'Moderate' AS Scenario,
                ROUND(SUM(e.total_annual_labor_cost_usd * a.automation_potential_pct * 0.65) / 1e6, 2) AS Labor_Savings_MUSD,
                ROUND(SUM(a.implementation_cost_usd * 1.00) / 1e6, 2)  AS Impl_Cost_MUSD,
                ROUND(SUM(a.ongoing_ai_cost_per_year_usd) / 1e6, 2)     AS Ongoing_Cost_MUSD
            FROM employees e
            JOIN ai_assumptions a ON e.role_id = a.role_id
        ),
        aggressive AS (
            SELECT
                'Aggressive' AS Scenario,
                ROUND(SUM(e.total_annual_labor_cost_usd * a.automation_potential_pct * 0.85) / 1e6, 2) AS Labor_Savings_MUSD,
                ROUND(SUM(a.implementation_cost_usd * 0.90) / 1e6, 2)  AS Impl_Cost_MUSD,
                ROUND(SUM(a.ongoing_ai_cost_per_year_usd * 1.10) / 1e6, 2) AS Ongoing_Cost_MUSD
            FROM employees e
            JOIN ai_assumptions a ON e.role_id = a.role_id
        )
        SELECT
            c.Scenario,
            c.Labor_Savings_MUSD,
            c.Impl_Cost_MUSD,
            c.Ongoing_Cost_MUSD,
            ROUND(c.Labor_Savings_MUSD - c.Ongoing_Cost_MUSD, 2) AS Net_Annual_Savings_MUSD,
            ROUND(c.Impl_Cost_MUSD / NULLIF(c.Labor_Savings_MUSD - c.Ongoing_Cost_MUSD, 0) * 12, 1) AS Payback_Months
        FROM conservative c
        UNION ALL
        SELECT
            m.Scenario,
            m.Labor_Savings_MUSD,
            m.Impl_Cost_MUSD,
            m.Ongoing_Cost_MUSD,
            ROUND(m.Labor_Savings_MUSD - m.Ongoing_Cost_MUSD, 2),
            ROUND(m.Impl_Cost_MUSD / NULLIF(m.Labor_Savings_MUSD - m.Ongoing_Cost_MUSD, 0) * 12, 1)
        FROM moderate m
        UNION ALL
        SELECT
            a.Scenario,
            a.Labor_Savings_MUSD,
            a.Impl_Cost_MUSD,
            a.Ongoing_Cost_MUSD,
            ROUND(a.Labor_Savings_MUSD - a.Ongoing_Cost_MUSD, 2),
            ROUND(a.Impl_Cost_MUSD / NULLIF(a.Labor_Savings_MUSD - a.Ongoing_Cost_MUSD, 0) * 12, 1)
        FROM aggressive a
        """,
        "What are the company-level savings, costs, and payback period under each AI scenario?"
    ),

    # -- Q10: ROI ranking by role (CTE + window RANK) -------------------------
    # Features: CTE, window function RANK() OVER, derived ROI formula
    "Q10_roi_ranking": (
        """
        WITH role_economics AS (
            SELECT
                r.role_name,
                r.function,
                e.total_annual_labor_cost_usd,
                a.automation_potential_pct,
                a.ai_productivity_uplift_pct,
                a.implementation_cost_usd,
                a.ongoing_ai_cost_per_year_usd,
                -- Moderate scenario
                ROUND(e.total_annual_labor_cost_usd * a.automation_potential_pct * 0.65, 0)
                    AS labor_savings,
                ROUND(e.total_annual_labor_cost_usd * a.ai_productivity_uplift_pct * 0.75, 0)
                    AS productivity_value
            FROM roles r
            JOIN employees e       ON r.role_id = e.role_id
            JOIN ai_assumptions a  ON r.role_id = a.role_id
        ),
        net_benefit AS (
            SELECT *,
                ROUND(labor_savings + productivity_value - ongoing_ai_cost_per_year_usd, 0)
                    AS net_annual_benefit
            FROM role_economics
        )
        SELECT
            role_name                                                AS Role,
            function                                                 AS Department,
            ROUND(implementation_cost_usd / 1e3, 0)                 AS Impl_Cost_KUSD,
            ROUND(net_annual_benefit / 1e3, 0)                      AS Net_Benefit_KUSD,
            ROUND((net_annual_benefit - implementation_cost_usd)
                  / NULLIF(implementation_cost_usd, 0) * 100, 1)    AS ROI_Year1_Pct,
            ROUND(implementation_cost_usd / NULLIF(net_annual_benefit / 12.0, 0), 1)
                                                                     AS Payback_Months,
            RANK() OVER (ORDER BY
                (net_annual_benefit - implementation_cost_usd) /
                NULLIF(implementation_cost_usd, 0) DESC
            )                                                        AS ROI_Rank
        FROM net_benefit
        WHERE net_annual_benefit > 0
        ORDER BY ROI_Rank
        LIMIT 15
        """,
        "Which roles deliver the highest Year-1 ROI under the moderate AI scenario?"
    ),

    # -- Q11: Risk-adjusted opportunity matrix ---------------------------------
    # Features: CASE WHEN quadrant classification
    "Q11_risk_opportunity_matrix": (
        """
        SELECT
            role_name                                   AS Role,
            function                                    AS Department,
            ROUND(automation_potential_pct * 100, 1)    AS Auto_Potential_Pct,
            ROUND(risk_score * 100, 1)                  AS Risk_Score_Pct,
            ROUND(automatable_labor_cost_usd / 1e6, 2)  AS Auto_Cost_Pool_MUSD,
            CASE
                WHEN automation_potential_pct >= 0.50 AND risk_score < 0.40
                    THEN '[G] Quick Win  — High Opp, Low Risk'
                WHEN automation_potential_pct >= 0.50 AND risk_score >= 0.40
                    THEN '[A] Careful Deploy — High Opp, High Risk'
                WHEN automation_potential_pct < 0.50  AND risk_score < 0.40
                    THEN '[B] Augment First — Low Opp, Low Risk'
                ELSE
                    '[R] Defer / Manual — Low Opp, High Risk'
            END                                         AS Quadrant
        FROM master
        ORDER BY
            CASE
                WHEN automation_potential_pct >= 0.50 AND risk_score < 0.40 THEN 1
                WHEN automation_potential_pct >= 0.50 AND risk_score >= 0.40 THEN 2
                WHEN automation_potential_pct < 0.50  AND risk_score < 0.40 THEN 3
                ELSE 4
            END,
            automatable_labor_cost_usd DESC
        """,
        "Where does each role sit in the risk vs opportunity decision matrix?"
    ),

    # -- Q12: Phase assignment using NTILE window function --------------------
    # Features: NTILE window function, ORDER BY, CTE
    "Q12_phase_assignment": (
        """
        WITH scored AS (
            SELECT
                role_name,
                function,
                automation_potential_pct,
                risk_score,
                automatable_labor_cost_usd,
                -- Composite priority: high automation x low risk x high cost
                (automation_potential_pct * (1 - risk_score) *
                 automatable_labor_cost_usd / 1e6)            AS priority_score
            FROM master
        ),
        ranked AS (
            SELECT *,
                NTILE(3) OVER (ORDER BY priority_score DESC) AS Phase_Num
            FROM scored
        )
        SELECT
            role_name                               AS Role,
            function                                AS Department,
            ROUND(automation_potential_pct * 100, 1) AS Auto_Pct,
            ROUND(risk_score, 3)                    AS Risk,
            ROUND(automatable_labor_cost_usd / 1e6, 2) AS Auto_Pool_MUSD,
            ROUND(priority_score, 3)                AS Priority_Score,
            'Phase ' || Phase_Num                   AS Recommended_Phase
        FROM ranked
        ORDER BY Phase_Num, priority_score DESC
        """,
        "Which roles should be in Phase 1, 2, and 3 of AI deployment?"
    ),

    # -- Q13: Break-even analysis — roles with payback < 24 months ------------
    # Features: Subquery filter on computed payback, ORDER BY
    "Q13_breakeven_analysis": (
        """
        SELECT *
        FROM (
            SELECT
                r.role_name                                              AS Role,
                r.function                                               AS Department,
                ROUND(a.implementation_cost_usd / 1e3, 0)              AS Impl_Cost_KUSD,
                ROUND(
                    (e.total_annual_labor_cost_usd * a.automation_potential_pct * 0.65 +
                     e.total_annual_labor_cost_usd * a.ai_productivity_uplift_pct * 0.75 -
                     a.ongoing_ai_cost_per_year_usd) / 1e3, 0
                )                                                        AS Net_Benefit_KUSD,
                ROUND(
                    a.implementation_cost_usd /
                    NULLIF(
                        (e.total_annual_labor_cost_usd * a.automation_potential_pct * 0.65 +
                         e.total_annual_labor_cost_usd * a.ai_productivity_uplift_pct * 0.75 -
                         a.ongoing_ai_cost_per_year_usd) / 12.0, 0
                    ), 1
                )                                                        AS Payback_Months
            FROM roles r
            JOIN employees e       ON r.role_id = e.role_id
            JOIN ai_assumptions a  ON r.role_id = a.role_id
        ) sub
        WHERE Payback_Months < 24
          AND Net_Benefit_KUSD > 0
        ORDER BY Payback_Months
        """,
        "Which roles recover their AI investment within 24 months (moderate scenario)?"
    ),

    # -- Q14: Augmentation vs automation split per domain ---------------------
    # Features: GROUP BY, COUNT/SUM with conditional aggregation
    "Q14_auto_vs_aug_split": (
        """
        SELECT
            r.function                                        AS Department,
            COUNT(t.task_id)                                  AS Total_Tasks,
            SUM(CASE WHEN t.automatable = 1 THEN 1 ELSE 0 END) AS Automatable_Tasks,
            SUM(CASE WHEN t.augmentable = 1 AND t.automatable = 0 THEN 1 ELSE 0 END)
                                                              AS Augmentable_Only_Tasks,
            SUM(CASE WHEN t.automatable = 0 AND t.augmentable = 0 THEN 1 ELSE 0 END)
                                                              AS Human_Only_Tasks,
            ROUND(
                SUM(CASE WHEN t.automatable = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(t.task_id), 1
            )                                                 AS Automatable_Task_Pct
        FROM roles r
        JOIN tasks t ON r.role_id = t.role_id
        GROUP BY r.function
        ORDER BY Automatable_Task_Pct DESC
        """,
        "How are tasks split between automation, augmentation, and human-only within each department?"
    ),

    # -- Q15: Top 5 roles by 3-year NPV ---------------------------------------
    # Features: CTE with NPV formula, RANK() OVER, ROUND
    "Q15_npv_top5": (
        """
        WITH npv_calc AS (
            SELECT
                r.role_name,
                r.function,
                a.implementation_cost_usd,
                -- Net annual benefit (moderate scenario)
                ROUND(
                    e.total_annual_labor_cost_usd * a.automation_potential_pct * 0.65 +
                    e.total_annual_labor_cost_usd * a.ai_productivity_uplift_pct * 0.75 -
                    a.ongoing_ai_cost_per_year_usd,
                0) AS net_annual_benefit
            FROM roles r
            JOIN employees e       ON r.role_id = e.role_id
            JOIN ai_assumptions a  ON r.role_id = a.role_id
        ),
        npv_result AS (
            SELECT *,
                ROUND(
                    net_annual_benefit / 1.10 +
                    net_annual_benefit / (1.10 * 1.10) +
                    net_annual_benefit / (1.10 * 1.10 * 1.10) -
                    implementation_cost_usd,
                0) AS NPV_3yr_USD
            FROM npv_calc
            WHERE net_annual_benefit > 0
        )
        SELECT
            role_name                                   AS Role,
            function                                    AS Department,
            ROUND(implementation_cost_usd / 1e3, 0)    AS Impl_Cost_KUSD,
            ROUND(net_annual_benefit / 1e3, 0)          AS Net_Benefit_KUSD,
            ROUND(NPV_3yr_USD / 1e6, 2)                 AS NPV_3yr_MUSD,
            RANK() OVER (ORDER BY NPV_3yr_USD DESC)     AS NPV_Rank
        FROM npv_result
        ORDER BY NPV_3yr_USD DESC
        LIMIT 5
        """,
        "Which roles generate the highest 3-year net present value for the company?"
    ),
}


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    utils.section("03 — SQL ANALYSIS")

    conn = init_db()
    results = {}

    for key, (sql, narrative) in QUERIES.items():
        label = key.replace("_", " ").upper()
        df = run_query(conn, label, sql, narrative)
        results[key] = df

    conn.close()
    print(f"\n  All 15 SQL queries executed successfully.")
    print(f"  Database: {config.DB_PATH}")
    return results


if __name__ == "__main__":
    main()
