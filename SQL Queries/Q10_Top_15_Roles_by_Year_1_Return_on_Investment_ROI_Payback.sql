USE AI_Workforce_DB;
GO

-- -------------------------------------------------------------------------------------
-- Q10: Top 15 Roles by Year-1 Return on Investment (ROI) & Payback
-- Business Question: Which specific roles deliver the fastest capital recovery and highest ROI?
-- SQL Features: Multiple CTEs, Window function RANK() OVER (), Filter on net benefit
;WITH Role_Economics AS (
    SELECT
        r.role_name,
        r.function_domain,
        e.total_annual_labor_cost_usd,
        a.automation_potential_pct,
        a.ai_productivity_uplift_pct,
        a.implementation_cost_usd,
        a.ongoing_ai_cost_per_year_usd,
        -- Moderate scenario assumptions: 65% auto capture, 75% productivity capture
        ROUND(e.total_annual_labor_cost_usd * a.automation_potential_pct * 0.65, 0) AS labor_savings,
        ROUND(e.total_annual_labor_cost_usd * a.ai_productivity_uplift_pct * 0.75, 0) AS productivity_value
    FROM dbo.roles r
    INNER JOIN dbo.employees e      ON r.role_id = e.role_id
    INNER JOIN dbo.ai_assumptions a ON r.role_id = a.role_id
),
Role_Net_Benefit AS (
    SELECT 
        *,
        (labor_savings + productivity_value - ongoing_ai_cost_per_year_usd) AS net_annual_benefit
    FROM Role_Economics
)
SELECT TOP 15
    role_name                                                   AS Role_Name,
    function_domain                                             AS Department,
    CAST(ROUND(implementation_cost_usd / 1000.0, 0) AS INT)     AS Impl_Cost_KUSD,
    CAST(ROUND(net_annual_benefit / 1000.0, 0) AS INT)          AS Net_Annual_Benefit_KUSD,
    CAST(ROUND(
        (net_annual_benefit - implementation_cost_usd) * 100.0 / NULLIF(implementation_cost_usd, 0), 1
    ) AS DECIMAL(8,1))                                          AS Year1_ROI_Pct,
    CAST(ROUND(
        implementation_cost_usd / NULLIF(net_annual_benefit / 12.0, 0), 1
    ) AS DECIMAL(5,1))                                          AS Payback_Months,
    RANK() OVER (ORDER BY (net_annual_benefit - implementation_cost_usd) / NULLIF(implementation_cost_usd, 0) DESC) 
                                                                AS ROI_Rank
FROM Role_Net_Benefit
WHERE net_annual_benefit > 0
ORDER BY ROI_Rank;
GO
