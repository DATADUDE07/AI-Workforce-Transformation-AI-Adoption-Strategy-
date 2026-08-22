USE AI_Workforce_DB;
GO

-- -------------------------------------------------------------------------------------
-- Q8: Hourly Productivity Economics: Pre-AI vs Post-AI (Moderate Adoption Scenario)
-- Business Question: How does effective cost-per-productive-hour change under moderate AI adoption?
-- SQL Features: Mathematical derived columns, CASE WHEN, Ordering by uplift
SELECT
    r.role_name                                                 AS Role_Name,
    r.function_domain                                           AS Department,
    e.productive_hours_per_year                                 AS Hours_Per_Person,
    CAST(ROUND(e.cost_per_productive_hour, 0) AS INT)           AS Cost_Per_Hour_Before,
    CAST(ROUND(
        e.cost_per_productive_hour / (1.0 + (a.ai_productivity_uplift_pct * 0.75)), 0
    ) AS INT)                                                   AS Cost_Per_Hour_After_AI,
    CAST(ROUND(a.ai_productivity_uplift_pct * 75.0, 1) AS DECIMAL(5,1)) AS Effective_Output_Gain_Pct,
    CASE
        WHEN a.ai_productivity_uplift_pct * 0.75 >= 0.35 THEN 'Transformational Impact'
        WHEN a.ai_productivity_uplift_pct * 0.75 >= 0.25 THEN 'High Impact'
        ELSE 'Moderate Impact'
    END                                                         AS Impact_Classification
FROM dbo.roles r
INNER JOIN dbo.employees e      ON r.role_id = e.role_id
INNER JOIN dbo.ai_assumptions a ON r.role_id = a.role_id
ORDER BY a.ai_productivity_uplift_pct DESC;
GO
