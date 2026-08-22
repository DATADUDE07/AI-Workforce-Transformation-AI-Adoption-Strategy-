USE AI_Workforce_DB;
GO

-- -------------------------------------------------------------------------------------
-- Q14: Task-Level Decomposition: Automatable vs Augmentable vs Human-Only by Department
-- Business Question: How are granular tasks distributed across automation, augmentation, and human-only?
-- SQL Features: Task-level JOIN, Conditional aggregation (SUM CASE), Granular ratio analytics
SELECT
    r.function_domain                                           AS Department,
    COUNT(t.task_id)                                            AS Total_Tasks,
    SUM(CASE WHEN t.automatable = 1 THEN 1 ELSE 0 END)          AS Automatable_Tasks,
    SUM(CASE WHEN t.augmentable = 1 AND t.automatable = 0 THEN 1 ELSE 0 END) 
                                                                AS Augmentable_Only_Tasks,
    SUM(CASE WHEN t.automatable = 0 AND t.augmentable = 0 THEN 1 ELSE 0 END) 
                                                                AS Human_Only_Tasks,
    CAST(ROUND(
        SUM(CASE WHEN t.automatable = 1 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(t.task_id), 0), 1
    ) AS DECIMAL(5,1))                                          AS Automatable_Task_Ratio_Pct
FROM dbo.roles r
INNER JOIN dbo.tasks t ON r.role_id = t.role_id
GROUP BY r.function_domain
ORDER BY Automatable_Task_Ratio_Pct DESC;
GO
