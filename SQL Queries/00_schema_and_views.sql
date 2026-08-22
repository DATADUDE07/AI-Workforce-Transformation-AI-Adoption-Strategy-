-- =====================================================================================
-- DATABASE: AI_Workforce_DB (Microsoft SQL Server / SSMS)
-- PROJECT : AI Workforce Transformation Analytics & Prioritization Framework
-- AUTHOR  : Senior Decision Analytics Consultant
-- PURPOSE : Production-ready T-SQL script containing schema DDL, constraints,
--           indexed analytical views, and all 15 Business Decision Queries.
-- =====================================================================================

USE master;
GO

IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'AI_Workforce_DB')
BEGIN
    CREATE DATABASE AI_Workforce_DB;
END;
GO

USE AI_Workforce_DB;
GO

-- =====================================================================================
-- SECTION 1: SCHEMA DDL (TABLE CREATION)
-- =====================================================================================

IF OBJECT_ID('dbo.tasks', 'U') IS NOT NULL DROP TABLE dbo.tasks;
IF OBJECT_ID('dbo.ai_assumptions', 'U') IS NOT NULL DROP TABLE dbo.ai_assumptions;
IF OBJECT_ID('dbo.employees', 'U') IS NOT NULL DROP TABLE dbo.employees;
IF OBJECT_ID('dbo.roles', 'U') IS NOT NULL DROP TABLE dbo.roles;
GO

-- 1. Roles Master Table
CREATE TABLE dbo.roles (
    role_id                   VARCHAR(20)     NOT NULL PRIMARY KEY,
    role_name                 VARCHAR(100)    NOT NULL,
    function_domain           VARCHAR(50)     NOT NULL, -- 'function' is a reserved word in T-SQL
    role_level                VARCHAR(20)     NOT NULL,
    avg_annual_salary_usd     DECIMAL(18, 2)  NOT NULL,
    num_employees             INT             NOT NULL,
    hours_per_week            DECIMAL(5, 2)   NOT NULL DEFAULT 40.0,
    task_repetitiveness_pct   DECIMAL(5, 4)   NOT NULL,
    decision_intensity        DECIMAL(5, 4)   NOT NULL,
    customer_impact           DECIMAL(5, 4)   NOT NULL,
    regulatory_sensitivity    DECIMAL(5, 4)   NOT NULL,
    skill_complexity          DECIMAL(5, 4)   NOT NULL,
    current_error_rate_pct    DECIMAL(5, 4)   NOT NULL,
    ai_maturity_readiness     DECIMAL(5, 4)   NOT NULL
);
GO

-- 2. Employees & Cost Table
CREATE TABLE dbo.employees (
    role_id                      VARCHAR(20)     NOT NULL PRIMARY KEY,
    total_headcount              INT             NOT NULL,
    benefits_load_pct            DECIMAL(5, 4)   NOT NULL DEFAULT 0.30,
    total_annual_labor_cost_usd  DECIMAL(18, 2)  NOT NULL,
    productive_hours_per_year    INT             NOT NULL DEFAULT 1920,
    cost_per_productive_hour     DECIMAL(10, 2)  NOT NULL,
    CONSTRAINT FK_employees_roles FOREIGN KEY (role_id) REFERENCES dbo.roles(role_id)
);
GO

-- 3. AI Adoption Assumptions Table
CREATE TABLE dbo.ai_assumptions (
    role_id                         VARCHAR(20)     NOT NULL PRIMARY KEY,
    automation_potential_pct        DECIMAL(5, 4)   NOT NULL,
    augmentation_potential_pct      DECIMAL(5, 4)   NOT NULL,
    human_oversight_required_pct    DECIMAL(5, 4)   NOT NULL,
    ai_productivity_uplift_pct      DECIMAL(5, 4)   NOT NULL,
    implementation_cost_usd         DECIMAL(18, 2)  NOT NULL,
    ongoing_ai_cost_per_year_usd    DECIMAL(18, 2)  NOT NULL,
    time_to_value_months            INT             NOT NULL,
    quality_risk_score              DECIMAL(5, 4)   NOT NULL,
    change_mgmt_complexity          DECIMAL(5, 4)   NOT NULL,
    scenario_conservative_auto_pct  DECIMAL(5, 4)   NOT NULL,
    scenario_moderate_auto_pct      DECIMAL(5, 4)   NOT NULL,
    scenario_aggressive_auto_pct    DECIMAL(5, 4)   NOT NULL,
    CONSTRAINT FK_ai_assumptions_roles FOREIGN KEY (role_id) REFERENCES dbo.roles(role_id)
);
GO

-- 4. Task-Level Breakdown Table
CREATE TABLE dbo.tasks (
    task_id               VARCHAR(20)     NOT NULL PRIMARY KEY,
    role_id               VARCHAR(20)     NOT NULL,
    task_name             VARCHAR(150)    NOT NULL,
    task_category         VARCHAR(50)     NOT NULL,
    time_pct              DECIMAL(5, 4)   NOT NULL,
    automatable           BIT             NOT NULL,
    augmentable           BIT             NOT NULL,
    automation_confidence DECIMAL(5, 4)   NOT NULL,
    ai_tool_available     BIT             NOT NULL,
    notes                 NVARCHAR(500)   NULL,
    CONSTRAINT FK_tasks_roles FOREIGN KEY (role_id) REFERENCES dbo.roles(role_id)
);
GO

-- Create analytical indexes
CREATE NONCLUSTERED INDEX IX_roles_function ON dbo.roles(function_domain);
CREATE NONCLUSTERED INDEX IX_tasks_role ON dbo.tasks(role_id);
CREATE NONCLUSTERED INDEX IX_tasks_automatable ON dbo.tasks(automatable, augmentable);
GO


-- =====================================================================================
-- SECTION 2: ENRICHED ANALYTICAL VIEW (Consolidated Master Frame)
-- =====================================================================================

IF OBJECT_ID('dbo.vw_ai_workforce_master', 'V') IS NOT NULL 
    DROP VIEW dbo.vw_ai_workforce_master;
GO

CREATE VIEW dbo.vw_ai_workforce_master
AS
SELECT 
    r.role_id,
    r.role_name,
    r.function_domain,
    r.role_level,
    r.avg_annual_salary_usd,
    r.num_employees AS total_headcount,
    r.hours_per_week,
    r.task_repetitiveness_pct,
    r.decision_intensity,
    r.customer_impact,
    r.regulatory_sensitivity,
    r.skill_complexity,
    r.current_error_rate_pct,
    r.ai_maturity_readiness,
    e.benefits_load_pct,
    e.total_annual_labor_cost_usd,
    e.productive_hours_per_year,
    e.cost_per_productive_hour,
    a.automation_potential_pct,
    a.augmentation_potential_pct,
    a.human_oversight_required_pct,
    a.ai_productivity_uplift_pct,
    a.implementation_cost_usd,
    a.ongoing_ai_cost_per_year_usd,
    a.time_to_value_months,
    a.quality_risk_score,
    a.change_mgmt_complexity,
    -- Derived Metrics
    ROUND(e.total_annual_labor_cost_usd * a.automation_potential_pct, 2) AS automatable_labor_cost_usd,
    ROUND(e.total_annual_labor_cost_usd * a.augmentation_potential_pct, 2) AS augmentable_labor_cost_usd,
    ROUND(
        (0.40 * a.quality_risk_score) + 
        (0.30 * r.regulatory_sensitivity) + 
        (0.20 * r.customer_impact) + 
        (0.10 * a.change_mgmt_complexity), 4
    ) AS composite_risk_score,
    CASE 
        WHEN a.automation_potential_pct >= 0.60 THEN 'Full Automation'
        WHEN a.augmentation_potential_pct >= 0.40 THEN 'AI Augmentation'
        ELSE 'Low AI Suitability'
    END AS ai_classification
FROM dbo.roles r
INNER JOIN dbo.employees e ON r.role_id = e.role_id
INNER JOIN dbo.ai_assumptions a ON r.role_id = a.role_id;
GO


-- =====================================================================================
-- SECTION 3: 15 BUSINESS DECISION ANALYTICAL QUERIES (T-SQL / SSMS)
-- =====================================================================================
