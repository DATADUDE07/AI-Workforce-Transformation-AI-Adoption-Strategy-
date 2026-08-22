USE AI_Workforce_DB;
GO

-- -------------------------------------------------------------------------------------
-- Q11: 2x2 Risk-Opportunity Strategy Classification
-- Business Question: Where does each role sit in the risk vs opportunity strategic matrix?
-- SQL Features: CASE WHEN nested logic, Quadrant tagging, Conditional ordering
SELECT
    role_name                                                   AS Role_Name,
    function_domain                                             AS Department,
    CAST(ROUND(automation_potential_pct * 100.0, 1) AS DECIMAL(5,1)) AS Auto_Potential_Pct,
    CAST(ROUND(composite_risk_score * 100.0, 1) AS DECIMAL(5,1))     AS Risk_Score_Pct,
    CAST(ROUND(automatable_labor_cost_usd / 1000000.0, 2) AS DECIMAL(10,2)) AS Auto_Cost_Pool_MUSD,
    CASE
        WHEN automation_potential_pct >= 0.50 AND composite_risk_score < 0.40
            THEN '🟢 Quick Win: High Opp, Low Risk (Deploy First)'
        WHEN automation_potential_pct >= 0.50 AND composite_risk_score >= 0.40
            THEN '🟡 Careful Deploy: High Opp, High Risk (Governance Guardrails)'
        WHEN automation_potential_pct < 0.50  AND composite_risk_score < 0.40
            THEN '🔵 Augment First: Moderate Opp, Low Risk (Copilot Tooling)'
        ELSE
            '🔴 Defer / Manual: High Judgment, High Risk (Human-Led)'
    END                                                         AS Strategic_Quadrant
FROM dbo.vw_ai_workforce_master
ORDER BY
    CASE
        WHEN automation_potential_pct >= 0.50 AND composite_risk_score < 0.40 THEN 1
        WHEN automation_potential_pct >= 0.50 AND composite_risk_score >= 0.40 THEN 2
        WHEN automation_potential_pct < 0.50  AND composite_risk_score < 0.40 THEN 3
        ELSE 4
    END,
    automatable_labor_cost_usd DESC;
GO
