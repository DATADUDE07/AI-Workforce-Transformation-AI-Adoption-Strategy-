USE AI_Workforce_DB;
GO

-- -------------------------------------------------------------------------------------
-- Q1: Total Labor Cost & Exposure by Department
-- Business Question: Which departments represent the largest share of total labor cost?
-- SQL Features: GROUP BY, SUM, Subquery for percentage share, ORDER BY
SELECT
    r.function_domain                                           AS Department,
    COUNT(r.role_id)                                            AS Role_Count,
    SUM(r.num_employees)                                        AS Total_Headcount,
    CAST(ROUND(SUM(e.total_annual_labor_cost_usd) / 1000000.0, 2) AS DECIMAL(10,2)) AS Total_Cost_MUSD,
    CAST(ROUND(
        SUM(e.total_annual_labor_cost_usd) * 100.0 /
        (SELECT SUM(total_annual_labor_cost_usd) FROM dbo.employees), 1
    ) AS DECIMAL(5,1))                                          AS Cost_Share_Pct
FROM dbo.roles r
INNER JOIN dbo.employees e ON r.role_id = e.role_id
GROUP BY r.function_domain
ORDER BY Total_Cost_MUSD DESC;
GO
