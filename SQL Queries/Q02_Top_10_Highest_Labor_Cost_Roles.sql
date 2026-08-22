USE AI_Workforce_DB;
GO

-- -------------------------------------------------------------------------------------
-- Q2: Top 10 Highest Labor-Cost Roles
-- Business Question: Which individual roles carry the highest absolute labor cost burden?
-- SQL Features: TOP (T-SQL syntax), INNER JOIN, ORDER BY
SELECT TOP 10
    r.role_name                                                 AS Role_Name,
    r.function_domain                                           AS Department,
    r.num_employees                                             AS Headcount,
    CAST(r.avg_annual_salary_usd AS INT)                        AS Avg_Salary_USD,
    CAST(ROUND(e.total_annual_labor_cost_usd / 1000000.0, 2) AS DECIMAL(10,2)) AS Total_Cost_MUSD
FROM dbo.roles r
INNER JOIN dbo.employees e ON r.role_id = e.role_id
ORDER BY e.total_annual_labor_cost_usd DESC;
GO
