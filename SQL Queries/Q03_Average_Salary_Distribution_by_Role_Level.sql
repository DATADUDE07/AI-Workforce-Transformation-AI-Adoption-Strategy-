USE AI_Workforce_DB;
GO

-- -------------------------------------------------------------------------------------
-- Q3: Average Salary & Distribution by Role Level
-- Business Question: How does average salary and role compensation spread across seniority tiers?
-- SQL Features: GROUP BY, CASE WHEN in ORDER BY, Aggregate functions
SELECT
    role_level                                   AS Level,
    COUNT(*)                                     AS Role_Count,
    CAST(ROUND(AVG(avg_annual_salary_usd), 0) AS INT) AS Avg_Salary_USD,
    CAST(MIN(avg_annual_salary_usd) AS INT)      AS Min_Salary_USD,
    CAST(MAX(avg_annual_salary_usd) AS INT)      AS Max_Salary_USD
FROM dbo.roles
GROUP BY role_level
ORDER BY
    CASE role_level
        WHEN 'Junior'   THEN 1
        WHEN 'Mid'      THEN 2
        WHEN 'Senior'   THEN 3
        WHEN 'Manager'  THEN 4
        WHEN 'Director' THEN 5
    END;
GO
