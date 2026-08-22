USE AI_Workforce_DB;
GO

-- -------------------------------------------------------------------------------------
-- Q7: Roles with Highest Automation Opportunity & Impact
-- Business Question: Which top 12 roles offer the largest automatable cost pool and productivity uplift?
-- SQL Features: TOP (T-SQL), View usage, Composite ordering
SELECT TOP 12
    role_name                                                   AS Role_Name,
    function_domain                                             AS Department,
    CAST(ROUND(automation_potential_pct * 100.0, 1) AS DECIMAL(5,1)) AS Auto_Pct,
    CAST(ROUND(automatable_labor_cost_usd / 1000000.0, 2) AS DECIMAL(10,2)) AS Auto_Cost_Pool_MUSD,
    CAST(ROUND(ai_productivity_uplift_pct * 100.0, 1) AS DECIMAL(5,1)) AS Productivity_Uplift_Pct,
    CAST(composite_risk_score AS DECIMAL(5,3))                 AS Risk_Score,
    ai_classification                                           AS AI_Category
FROM dbo.vw_ai_workforce_master
ORDER BY automatable_labor_cost_usd DESC, automation_potential_pct DESC;
GO
