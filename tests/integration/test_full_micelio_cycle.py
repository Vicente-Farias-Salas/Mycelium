"""Full end-to-end integration test simulating the complete Proyecto Micelio cycle."""

from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from micelio.api.app import create_app
from micelio.domain.models import ProjectStatus, SynapseEventType


@pytest.fixture
def e2e_env(tmp_path: Path):
    """Fixture with test client and dedicated workspace directory."""
    workspace_dir = tmp_path / "e2e_workspaces"
    app = create_app(workspace_base_dir=workspace_dir)
    client = TestClient(app)
    return client, workspace_dir


def test_complete_micelio_ecosystem_cycle(e2e_env):
    """Simulate complete lifecycle: creation, AI optimization, invite, bootstrap, A2A office work."""
    client, workspace_dir = e2e_env

    # -------------------------------------------------------------
    # 1. EL JEFE Y SU AGENTE CREAN EL PROYECTO
    # -------------------------------------------------------------
    create_payload = {
        "title": "Motor Cuantitativo de Arbitraje",
        "vision": "Procesar libros de órdenes L2 y ejecutar señales con sub-milisegundo",
        "creator_id": "mem-jefe-operaciones",
        "distilled_specs": "Ingesta WebSockets L2, cálculo de desbalance de libro y gateway FIX.",
        "interfaces": {
            "OrderBook": {"bids": "list[tuple[float, float]]", "asks": "list[tuple[float, float]]"}
        },
        "constraints": ("latencia < 500us", "cero copias en memoria", "inmutabilidad"),
        "shared_contracts": {"feed": "binance_l2", "engine": "order_book_v1"},
        "required_skills": ["python", "fastapi", "data_pipelines", "iot"],
        "target_department": "DATA",
    }
    proj_resp = client.post("/api/projects", json=create_payload)
    assert proj_resp.status_code == 201
    project_data = proj_resp.json()
    project_id = project_data["id"]
    assert project_data["status"] == ProjectStatus.DRAFT.value

    # -------------------------------------------------------------
    # 2. EL AGENTE DEL JEFE PREGUNTA: "¿A QUIÉN ENVIAMOS O BUSCO LOS MÁS ÓPTIMOS?"
    # El Jefe pide evaluar el equipo óptimo:
    # -------------------------------------------------------------
    rec_resp = client.get(f"/api/projects/{project_id}/recommend-team")
    assert rec_resp.status_code == 200
    recommendations = rec_resp.json()
    assert len(recommendations) >= 2

    top_candidate = recommendations[0]
    # Carlos Data should be the #1 recommendation because of DATA department & skills
    assert top_candidate["member"]["department"] == "DATA"
    assert top_candidate["score"] > 0.7
    assert "carlos" in top_candidate["rationale"].lower()

    # -------------------------------------------------------------
    # 3. EL JEFE APRUEBA Y SE DESPACHA LA INVITACIÓN INTERDEPARTAMENTAL
    # -------------------------------------------------------------
    invite_carlos_resp = client.post(
        f"/api/projects/{project_id}/dispatch",
        json={"member_id": top_candidate["member"]["id"], "role": "Lead Quantitative Data Engineer"},
    )
    assert invite_carlos_resp.status_code == 200
    carlos_invite = invite_carlos_resp.json()
    assert carlos_invite["status"] == "INVITED"

    # También invitamos a Vicente Architect para la arquitectura
    invite_arch_resp = client.post(
        f"/api/projects/{project_id}/dispatch",
        json={"member_id": "mem-dev", "role": "Systems Architect"},
    )
    assert invite_arch_resp.status_code == 200
    arch_invite = invite_arch_resp.json()

    # -------------------------------------------------------------
    # 4. LOS TRABAJADORES Y SUS AGENTES ACEPTAN LA UNIÓN Y AUTO-CREAN WORKSPACES
    # -------------------------------------------------------------
    # Carlos acepta:
    accept_carlos = client.post(
        f"/api/invites/{carlos_invite['id']}/respond",
        json={"action": "accept", "project_slug": "quant_data_carlos"},
    )
    assert accept_carlos.status_code == 200
    carlos_membership = accept_carlos.json()
    assert carlos_membership["status"] == "JOINED"

    # Verificar que el agente de Carlos creó físicamente la carpeta y el briefing
    carlos_dir = Path(carlos_membership["local_workspace_path"])
    assert carlos_dir.exists()
    assert (carlos_dir / "README.md").exists()
    assert (carlos_dir / "briefing.md").exists()

    briefing_text = (carlos_dir / "briefing.md").read_text(encoding="utf-8")
    assert "### 📥 1. ¿Qué llegó?" in briefing_text
    assert "### 🛠️ 2. ¿Qué se ha hecho?" in briefing_text
    assert "### 🚀 3. ¿Qué podemos hacer?" in briefing_text
    assert "Lead Quantitative Data Engineer" in briefing_text

    # Vicente Architect acepta:
    accept_arch = client.post(
        f"/api/invites/{arch_invite['id']}/respond",
        json={"action": "accept", "project_slug": "quant_arch_vicente"},
    )
    assert accept_arch.status_code == 200

    # -------------------------------------------------------------
    # 5. CO-TRABAJO EN LA "OFICINA VIRTUAL DE AGENTES" (SUSTRATO VIVO A2A)
    # -------------------------------------------------------------
    # Agente de Carlos propone un cambio de contrato para el OrderBook L2:
    mutation_resp = client.post(
        f"/api/projects/{project_id}/events",
        json={
            "event_type": SynapseEventType.STATE_MUTATION.value,
            "source_agent_id": "agt-carlos",
            "target_agent_id": "BROADCAST",
            "payload": {
                "contract_update": "order_book_v1",
                "changes": {"timestamp_unit": "nanoseconds", "depth": 50},
            },
        },
    )
    assert mutation_resp.status_code == 201

    # Agente de Vicente consulta y otorga consenso:
    consensus_resp = client.post(
        f"/api/projects/{project_id}/events",
        json={
            "event_type": SynapseEventType.AGENT_CONSENSUS.value,
            "source_agent_id": "agt-dev",
            "target_agent_id": "agt-carlos",
            "payload": {
                "decision": "APPROVED",
                "note": "Nanosegundos es óptimo para evitar saltos temporales en HFT.",
            },
        },
    )
    assert consensus_resp.status_code == 201

    # -------------------------------------------------------------
    # 6. ESTADO FINAL DEL PROYECTO Y HISTORIAL CONSOLIDADO
    # -------------------------------------------------------------
    status_resp = client.get(f"/api/projects/{project_id}/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["project"]["status"] == ProjectStatus.ACTIVE_OFFICE.value
    assert status_data["active_in_office"] == 2

    events_resp = client.get(f"/api/projects/{project_id}/events")
    assert events_resp.status_code == 200
    events = events_resp.json()
    assert len(events) == 2
    assert events[0]["event_type"] == SynapseEventType.STATE_MUTATION.value
    assert events[1]["event_type"] == SynapseEventType.AGENT_CONSENSUS.value
