USE AI_Workforce_DB;
GO

-- -------------------------------------------------------------------------------------
-- Q4: AI Automation & Augmentation Potential by Function
-- Business Question: Which business functions have the highest average AI automation potential?
-- SQL Features: INNER JOIN, GROUP BY, AVG, CASE WHEN for tier classification
SELECT
    r.function_domain                                            AS Department,
    CAST(ROUND(AVG(a.automation_potential_pct) * 100.0, 1) AS DECIMAL(5,1))   AS Avg_Auto_Pct,
    CAST(ROUND(AVG(a.augmentation_potential_pct) * 100.0, 1) AS DECIMAL(5,1)) AS Avg_Aug_Pct,
    CAST(ROUND(AVG(r.ai_maturity_readiness) * 100.0, 1) AS DECIMAL(5,1))      AS Avg_AI_Readiness_Pct,
    CASE
        WHEN AVG(a.automation_potential_pct) >= 0.60 THEN 'High Automation'
        WHEN AVG(a.automation_potential_pct) >= 0.40 THEN 'Medium Automation'
        ELSE 'Low Automation'
    END                                                          AS Auto_Tier
FROM dbo.roles r
INNER JOIN dbo.ai_assumptions a ON r.role_id = a.role_id
GROUP BY r.function_domain
ORDER BY Avg_Auto_Pct DESC;
GO
