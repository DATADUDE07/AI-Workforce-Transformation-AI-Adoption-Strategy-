USE AI_Workforce_DB;
GO

-- -------------------------------------------------------------------------------------
-- Q5: Headcount Concentration & Cumulative Distribution
-- Business Question: Where is company headcount concentrated? (Targets for volume scale)
-- SQL Features: Window function SUM() OVER (), Percentage calculations
SELECT
    r.function_domain                                           AS Department,
    SUM(r.num_employees)                                         AS Headcount,
    CAST(ROUND(
        SUM(r.num_employees) * 100.0 / SUM(SUM(r.num_employees)) OVER (), 1
    ) AS DECIMAL(5,1))                                          AS Headcount_Share_Pct,
    CAST(ROUND(
        SUM(SUM(r.num_employees)) OVER (ORDER BY SUM(r.num_employees) DESC ROWS UNBOUNDED PRECEDING) * 100.0 / 
        SUM(SUM(r.num_employees)) OVER (), 1
    ) AS DECIMAL(5,1))                                          AS Cumulative_Headcount_Pct
FROM dbo.roles r
GROUP BY r.function_domain
ORDER BY Headcount DESC;
GO
