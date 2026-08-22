USE AI_Workforce_DB;
GO

-- -------------------------------------------------------------------------------------
-- Q13: Break-Even Analysis (Capital Recovery < 24 Months)
-- Business Question: Which roles achieve full break-even within the 24-month moderate transformation window?
-- SQL Features: Derived table subquery, Strict payback filtering, Ordering
SELECT
    sub.Role_Name,
    sub.Department,
    sub.Impl_Cost_KUSD,
    sub.Net_Annual_Benefit_KUSD,
    sub.Payback_Months
FROM (
    SELECT
        r.role_name                                             AS Role_Name,
        r.function_domain                                       AS Department,
        CAST(ROUND(a.implementation_cost_usd / 1000.0, 0) AS INT) AS Impl_Cost_KUSD,
        CAST(ROUND(
            (e.total_annual_labor_cost_usd * a.automation_potential_pct * 0.65 +
             e.total_annual_labor_cost_usd * a.ai_productivity_uplift_pct * 0.75 -
             a.ongoing_ai_cost_per_year_usd) / 1000.0, 0
        ) AS INT)                                               AS Net_Annual_Benefit_KUSD,
        CAST(ROUND(
            a.implementation_cost_usd /
            NULLIF(
                (e.total_annual_labor_cost_usd * a.automation_potential_pct * 0.65 +
                 e.total_annual_labor_cost_usd * a.ai_productivity_uplift_pct * 0.75 -
                 a.ongoing_ai_cost_per_year_usd) / 12.0, 0
            ), 1
        ) AS DECIMAL(5,1))                                      AS Payback_Months
    FROM dbo.roles r
    INNER JOIN dbo.employees e      ON r.role_id = e.role_id
    INNER JOIN dbo.ai_assumptions a ON r.role_id = a.role_id
) sub
WHERE sub.Payback_Months <= 24.0
  AND sub.Net_Annual_Benefit_KUSD > 0
ORDER BY sub.Payback_Months ASC;
GO
