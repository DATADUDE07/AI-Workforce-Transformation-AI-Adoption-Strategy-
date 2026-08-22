USE AI_Workforce_DB;
GO

-- -------------------------------------------------------------------------------------
-- Q15: Top 5 Long-Term Value Drivers by 3-Year Net Present Value (NPV @ 10% Hurdle Rate)
-- Business Question: Which top 5 roles generate the highest multi-year discounted enterprise cash value?
-- SQL Features: Multi-period discounting formula CTE, Window function RANK() OVER ()
;WITH Role_Cashflows AS (
    SELECT
        r.role_name,
        r.function_domain,
        a.implementation_cost_usd,
        -- Net Annual Benefit under Moderate Scenario
        (e.total_annual_labor_cost_usd * a.automation_potential_pct * 0.65 +
         e.total_annual_labor_cost_usd * a.ai_productivity_uplift_pct * 0.75 -
         a.ongoing_ai_cost_per_year_usd) AS net_annual_benefit
    FROM dbo.roles r
    INNER JOIN dbo.employees e      ON r.role_id = e.role_id
    INNER JOIN dbo.ai_assumptions a ON r.role_id = a.role_id
),
NPV_Calculation AS (
    SELECT 
        *,
        -- 3-Year Discounting at 10% Hurdle Rate: PV = C1/(1.10)^1 + C2/(1.10)^2 + C3/(1.10)^3 - Initial_Cost
        ROUND(
            (net_annual_benefit / 1.10) +
            (net_annual_benefit / POWER(1.10, 2)) +
            (net_annual_benefit / POWER(1.10, 3)) -
            implementation_cost_usd, 0
        ) AS npv_3yr_usd
    FROM Role_Cashflows
    WHERE net_annual_benefit > 0
)
SELECT TOP 5
    role_name                                                   AS Role_Name,
    function_domain                                             AS Department,
    CAST(ROUND(implementation_cost_usd / 1000.0, 0) AS INT)     AS Impl_Cost_KUSD,
    CAST(ROUND(net_annual_benefit / 1000.0, 0) AS INT)          AS Net_Benefit_KUSD,
    CAST(ROUND(npv_3yr_usd / 1000000.0, 2) AS DECIMAL(10,2))   AS NPV_3Year_MUSD,
    RANK() OVER (ORDER BY npv_3yr_usd DESC)                     AS NPV_Rank
FROM NPV_Calculation
ORDER BY NPV_Rank ASC;
GO
