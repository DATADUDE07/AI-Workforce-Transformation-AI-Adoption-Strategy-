USE AI_Workforce_DB;
GO

-- -------------------------------------------------------------------------------------
-- Q12: Phased Implementation Roadmap Allocation (Phase 1, 2, 3)
-- Business Question: How should roles be prioritized across a 24-month roadmap using NTILE distribution?
-- SQL Features: Window function NTILE(3) OVER (), CTE, T-SQL string CONCAT
;WITH Scored_Priorities AS (
    SELECT
        role_name,
        function_domain,
        automation_potential_pct,
        composite_risk_score,
        automatable_labor_cost_usd,
        -- Composite scoring: High Automation x Low Risk x High Addressable Cost Pool
        (automation_potential_pct * (1.0 - composite_risk_score) * (automatable_labor_cost_usd / 1000000.0)) 
            AS composite_priority_index
    FROM dbo.vw_ai_workforce_master
),
Ranked_Phases AS (
    SELECT 
        *,
        NTILE(3) OVER (ORDER BY composite_priority_index DESC) AS Phase_Number
    FROM Scored_Priorities
)
SELECT
    role_name                                                   AS Role_Name,
    function_domain                                             AS Department,
    CAST(ROUND(automation_potential_pct * 100.0, 1) AS DECIMAL(5,1)) AS Auto_Pct,
    CAST(ROUND(composite_risk_score, 3) AS DECIMAL(5,3))        AS Risk_Score,
    CAST(ROUND(automatable_labor_cost_usd / 1000000.0, 2) AS DECIMAL(10,2)) AS Auto_Pool_MUSD,
    CAST(ROUND(composite_priority_index, 3) AS DECIMAL(8,3))    AS Priority_Index,
    CONCAT('Phase ', Phase_Number)                              AS Recommended_Deployment_Phase
FROM Ranked_Phases
ORDER BY Phase_Number ASC, composite_priority_index DESC;
GO
