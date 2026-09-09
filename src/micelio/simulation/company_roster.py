"""Enterprise Company Roster: 40 employees across 8 strategic departments."""

from micelio.domain.models import AgentProfile, DepartmentEnum, Member


def _build_commercial_team() -> tuple[tuple[Member, AgentProfile], ...]:
    """5 employees in Commercial & Executive Leadership."""
    data = [
        ("emp-001", "Valeria CEO - Estrategia", "valeria.ceo@empresa.com", True, ("b2b_saas", "enterprise_sales", "fundraising"), 30.0),
        ("emp-002", "Rodrigo CRO - Ventas", "rodrigo.cro@empresa.com", True, ("deal_closing", "sales_pipeline", "pricing"), 45.0),
        ("emp-003", "Camila Enterprise AE", "camila.ae@empresa.com", False, ("contract_negotiation", "b2b_enterprise", "crm"), 40.0),
        ("emp-004", "Lucas Sales Lead", "lucas.sales@empresa.com", False, ("outbound", "lead_scoring", "cold_outreach"), 35.0),
        ("emp-005", "Daniela Partnerships", "daniela.part@empresa.com", False, ("partner_ecosystem", "alliances", "channel_sales"), 25.0),
    ]
    return _map_tuples(DepartmentEnum.COMMERCIAL, data)


def _build_product_team() -> tuple[tuple[Member, AgentProfile], ...]:
    """5 employees in Product Management & Strategy."""
    data = [
        ("emp-006", "Sofia CPO - Producto", "sofia.cpo@empresa.com", True, ("product_vision", "roadmap", "okrs"), 35.0),
        ("emp-007", "Martin PM Enterprise", "martin.pm@empresa.com", False, ("prds", "feature_scoping", "b2b_requirements"), 40.0),
        ("emp-008", "Elena PM Integraciones", "elena.pm@empresa.com", False, ("api_integrations", "slack_jira_connectors", "sdk_specs"), 30.0),
        ("emp-009", "Javier Lead Product Analyst", "javier.pa@empresa.com", False, ("mixpanel", "funnel_analytics", "product_metrics"), 20.0),
        ("emp-010", "Paula Technical Writer", "paula.docs@empresa.com", False, ("openapi_docs", "developer_guides", "release_notes"), 25.0),
    ]
    return _map_tuples(DepartmentEnum.PRODUCT, data)


def _build_engineering_team() -> tuple[tuple[Member, AgentProfile], ...]:
    """5 employees in Core Engineering & Architecture."""
    data = [
        ("emp-011", "Vicente CTO - Arquitectura", "vicente.cto@empresa.com", True, ("distributed_systems", "fastapi", "c++", "tdd", "clean_arch"), 20.0),
        ("emp-012", "Gabriel Principal Architect", "gabriel.arch@empresa.com", False, ("system_design", "concurrency", "event_mesh", "python"), 35.0),
        ("emp-013", "Esteban Sr Backend Engineer", "esteban.backend@empresa.com", False, ("fastapi", "websockets", "sqlite_wal", "postgresql"), 40.0),
        ("emp-014", "Carolina Sr Fullstack", "carolina.fs@empresa.com", False, ("react", "typescript", "nextjs", "fastapi"), 45.0),
        ("emp-015", "Ignacio API Specialist", "ignacio.api@empresa.com", False, ("rest", "json_rpc", "openapi", "rate_limiting"), 30.0),
    ]
    return _map_tuples(DepartmentEnum.ENGINEERING, data)


def _build_data_ai_team() -> tuple[tuple[Member, AgentProfile], ...]:
    """5 employees in Data Science & Applied AI."""
    data = [
        ("emp-016", "Marcela Head of AI/Data", "marcela.ai@empresa.com", True, ("llm_orchestration", "multi_agent_swarms", "data_strategy"), 35.0),
        ("emp-017", "Carlos Lead Data Scientist", "carlos.ds@empresa.com", False, ("python", "data_pipelines", "ranking_algorithms", "nlp"), 25.0),
        ("emp-018", "Tomas Data Engineer", "tomas.de@empresa.com", False, ("etl", "clickhouse", "duckdb", "parquet", "streaming"), 40.0),
        ("emp-019", "Natalia MLOps Engineer", "natalia.mlops@empresa.com", False, ("model_deployment", "cuda", "vllm", "embedding_cache"), 30.0),
        ("emp-020", "Andres Agentic Researcher", "andres.agent@empresa.com", False, ("prompt_engineering", "semantic_compression", "a2a_protocols"), 20.0),
    ]
    return _map_tuples(DepartmentEnum.DATA, data)


def _build_operations_team() -> tuple[tuple[Member, AgentProfile], ...]:
    """5 employees in Platform, SRE & Operations."""
    data = [
        ("emp-021", "Hernan VP Platform & Ops", "hernan.ops@empresa.com", True, ("cloud_governance", "soc2", "disaster_recovery"), 30.0),
        ("emp-022", "Mauricio DevSecOps Lead", "mauricio.sec@empresa.com", False, ("zero_trust", "path_traversal_defense", "secrets_vault"), 25.0),
        ("emp-023", "Felipe SRE Lead", "felipe.sre@empresa.com", False, ("kubernetes", "high_availability", "prometheus", "grafana"), 40.0),
        ("emp-024", "Loreto DBA Specialist", "loreto.dba@empresa.com", False, ("sqlite_wal", "query_optimization", "indexes", "backup_restore"), 20.0),
        ("emp-025", "Patricio Cloud Architect", "patricio.cloud@empresa.com", False, ("aws", "docker", "redis_clusters", "networking"), 35.0),
    ]
    return _map_tuples(DepartmentEnum.OPERATIONS, data)


def _build_qa_team() -> tuple[tuple[Member, AgentProfile], ...]:
    """5 employees in Quality Assurance & Reliability."""
    data = [
        ("emp-026", "Claudia QA Director", "claudia.qa@empresa.com", True, ("qa_strategy", "tdd_enforcement", "test_pyramids"), 30.0),
        ("emp-027", "Alonso Automation Lead", "alonso.auto@empresa.com", False, ("pytest", "playwright", "integration_testing", "coverage"), 35.0),
        ("emp-028", "Francisca Load Tester", "francisca.load@empresa.com", False, ("locust", "stress_testing", "websocket_concurrency"), 25.0),
        ("emp-029", "Guillermo Chaos Engineer", "guillermo.chaos@empresa.com", False, ("failure_injection", "recovery_testing", "resilience"), 20.0),
        ("emp-030", "Veronica Security Tester", "veronica.pentest@empresa.com", False, ("owasp", "input_fuzzing", "path_traversal_audit"), 30.0),
    ]
    return _map_tuples(DepartmentEnum.QA, data)


def _build_design_team() -> tuple[tuple[Member, AgentProfile], ...]:
    """5 employees in Design & Frontend UX."""
    data = [
        ("emp-031", "Beatriz Head of UX/UI", "beatriz.ux@empresa.com", True, ("design_systems", "tasteful_ui", "information_architecture"), 25.0),
        ("emp-032", "Andrea Sr Product Designer", "andrea.ui@empresa.com", False, ("figma", "tailwind", "ui_craft", "interaction_design"), 35.0),
        ("emp-033", "Cristobal Frontend Dev", "cristobal.fe@empresa.com", False, ("react", "nextjs", "css_grid", "responsive_layouts"), 40.0),
        ("emp-034", "Macarena Visual Designer", "macarena.design@empresa.com", False, ("branding", "data_viz", "threejs", "dark_mode"), 30.0),
        ("emp-035", "Sebastian UX Researcher", "sebastian.uxr@empresa.com", False, ("user_interviews", "cognitive_load_analysis", "heuristics"), 20.0),
    ]
    return _map_tuples(DepartmentEnum.DESIGN, data)


def _build_cs_team() -> tuple[tuple[Member, AgentProfile], ...]:
    """5 employees in Customer Success & Support."""
    data = [
        ("emp-036", "Lorena VP Customer Success", "lorena.cs@empresa.com", True, ("customer_retention", "nps", "enterprise_accounts"), 35.0),
        ("emp-037", "Fabiola Enterprise CSM", "fabiola.csm@empresa.com", False, ("onboarding", "sla_monitoring", "qbrs"), 40.0),
        ("emp-038", "Gonzalo Solutions Consultant", "gonzalo.sol@empresa.com", False, ("client_workshops", "pilot_deployments", "custom_flows"), 30.0),
        ("emp-039", "Rocio L3 Support Engineer", "rocio.support@empresa.com", False, ("incident_triage", "log_analysis", "bug_reporting"), 25.0),
        ("emp-040", "Diego DevRel & Community", "diego.devrel@empresa.com", False, ("developer_advocacy", "tutorials", "github_issues"), 20.0),
    ]
    return _map_tuples(DepartmentEnum.CUSTOMER_SUCCESS, data)


def _map_tuples(
    dept: DepartmentEnum,
    data: list[tuple[str, str, str, bool, tuple[str, ...], float]],
) -> tuple[tuple[Member, AgentProfile], ...]:
    """Helper to assemble Member and AgentProfile pairs."""
    pairs = []
    for emp_id, name, email, is_mgr, capabilities, workload in data:
        member = Member(
            id=emp_id,
            name=name,
            email=email,
            department=dept,
            is_manager=is_mgr,
        )
        profile = AgentProfile(
            agent_id=f"agt-{emp_id.replace('emp-', '')}",
            member_id=emp_id,
            capabilities=capabilities,
            workload_pct=workload,
        )
        pairs.append((member, profile))
    return tuple(pairs)


def get_40_employee_roster() -> tuple[tuple[Member, AgentProfile], ...]:
    """Return the complete 40-employee enterprise company roster."""
    return (
        *_build_commercial_team(),
        *_build_product_team(),
        *_build_engineering_team(),
        *_build_data_ai_team(),
        *_build_operations_team(),
        *_build_qa_team(),
        *_build_design_team(),
        *_build_cs_team(),
    )


def get_department_members(department: DepartmentEnum) -> tuple[tuple[Member, AgentProfile], ...]:
    """Return all members belonging to a specific department."""
    roster = get_40_employee_roster()
    return tuple(pair for pair in roster if pair[0].department == department)


def get_enterprise_member_by_id(member_id: str) -> tuple[Member, AgentProfile] | None:
    """Find a member and profile by employee ID."""
    for pair in get_40_employee_roster():
        if pair[0].id == member_id:
            return pair
    return None
