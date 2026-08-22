USE AI_Workforce_DB;
GO

-- -------------------------------------------------------------------------------------
-- Q6: Addressable Automatable Labor Cost Pool by Function
-- Business Question: What is the maximum theoretical dollar pool of automatable labor cost by department?
-- SQL Features: Multi-table INNER JOIN, GROUP BY, Weighted opportunity calculation
SELECT
    r.function_domain                                                    AS Department,
    SUM(r.num_employees)                                                 AS Headcount,
    CAST(ROUND(SUM(e.total_annual_labor_cost_usd) / 1000000.0, 2) AS DECIMAL(10,2)) AS Total_Cost_MUSD,
    CAST(ROUND(SUM(e.total_annual_labor_cost_usd * a.automation_potential_pct) / 1000000.0, 2) AS DECIMAL(10,2)) 
                                                                         AS Automatable_Cost_MUSD,
    CAST(ROUND(
        SUM(e.total_annual_labor_cost_usd * a.automation_potential_pct) * 100.0 /
        NULLIF(SUM(e.total_annual_labor_cost_usd), 0), 1
    ) AS DECIMAL(5,1))                                                   AS Automatable_Pct
FROM dbo.roles r
INNER JOIN dbo.employees e      ON r.role_id = e.role_id
INNER JOIN dbo.ai_assumptions a ON r.role_id = a.role_id
GROUP BY r.function_domain
ORDER BY Automatable_Cost_MUSD DESC;
GO
