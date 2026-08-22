USE AI_Workforce_DB;
GO

-- -------------------------------------------------------------------------------------
-- Q9: Three-Scenario Macro Financial Comparison (Conservative vs Moderate vs Aggressive)
-- Business Question: What are the company-level savings, costs, and payback periods across adoption scenarios?
-- SQL Features: Common Table Expressions (CTEs), UNION ALL, NULLIF division safety
;WITH Scenario_Conservative AS (
    SELECT
        '1. Conservative (40% Adoption)' AS Scenario_Name,
        ROUND(SUM(e.total_annual_labor_cost_usd * a.automation_potential_pct * 0.40) / 1000000.0, 2) AS Labor_Savings_MUSD,
        ROUND(SUM(a.implementation_cost_usd * 1.20) / 1000000.0, 2)  AS Impl_Cost_MUSD,
        ROUND(SUM(a.ongoing_ai_cost_per_year_usd * 1.00) / 1000000.0, 2) AS Ongoing_Cost_MUSD
    FROM dbo.employees e
    INNER JOIN dbo.ai_assumptions a ON e.role_id = a.role_id
),
Scenario_Moderate AS (
    SELECT
        '2. Moderate (65% Adoption - Recommended)' AS Scenario_Name,
        ROUND(SUM(e.total_annual_labor_cost_usd * a.automation_potential_pct * 0.65) / 1000000.0, 2) AS Labor_Savings_MUSD,
        ROUND(SUM(a.implementation_cost_usd * 1.00) / 1000000.0, 2)  AS Impl_Cost_MUSD,
        ROUND(SUM(a.ongoing_ai_cost_per_year_usd * 1.00) / 1000000.0, 2) AS Ongoing_Cost_MUSD
    FROM dbo.employees e
    INNER JOIN dbo.ai_assumptions a ON e.role_id = a.role_id
),
Scenario_Aggressive AS (
    SELECT
        '3. Aggressive (85% Adoption)' AS Scenario_Name,
        ROUND(SUM(e.total_annual_labor_cost_usd * a.automation_potential_pct * 0.85) / 1000000.0, 2) AS Labor_Savings_MUSD,
        ROUND(SUM(a.implementation_cost_usd * 0.90) / 1000000.0, 2)  AS Impl_Cost_MUSD,
        ROUND(SUM(a.ongoing_ai_cost_per_year_usd * 1.10) / 1000000.0, 2) AS Ongoing_Cost_MUSD
    FROM dbo.employees e
    INNER JOIN dbo.ai_assumptions a ON e.role_id = a.role_id
),
Combined_Scenarios AS (
    SELECT * FROM Scenario_Conservative
    UNION ALL
    SELECT * FROM Scenario_Moderate
    UNION ALL
    SELECT * FROM Scenario_Aggressive
)
SELECT
    Scenario_Name,
    CAST(Labor_Savings_MUSD AS DECIMAL(10,2))                   AS Gross_Labor_Savings_MUSD,
    CAST(Impl_Cost_MUSD AS DECIMAL(10,2))                        AS Implementation_Cost_MUSD,
    CAST(Ongoing_Cost_MUSD AS DECIMAL(10,2))                     AS Annual_Tooling_Cost_MUSD,
    CAST(ROUND(Labor_Savings_MUSD - Ongoing_Cost_MUSD, 2) AS DECIMAL(10,2)) AS Net_Annual_Savings_MUSD,
    CAST(ROUND(Impl_Cost_MUSD / NULLIF(Labor_Savings_MUSD - Ongoing_Cost_MUSD, 0) * 12.0, 1) AS DECIMAL(5,1)) 
                                                                 AS Payback_Period_Months
FROM Combined_Scenarios;
GO
