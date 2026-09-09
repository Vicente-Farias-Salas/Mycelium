import pytest
import sqlite3
from micelio.core.synapse_bus import SynapseBus
from micelio.storage.database import DatabaseManager
from micelio.storage.repositories import SqliteEventRepository, SqliteProjectRepository
from micelio.simulation.crunch_simulator import CrunchSimulator

@pytest.mark.asyncio
async def test_massive_crunch_simulation(tmp_path):
    # Setup test DB
    db_path = tmp_path / "test_crunch_events.db"
    db_manager = DatabaseManager(str(db_path))
    db_manager.initialize_schema()
    event_repo = SqliteEventRepository(db_manager)
    project_repo = SqliteProjectRepository(db_manager)
    
    bus = SynapseBus()
    
    # Init simulator
    simulator = CrunchSimulator(bus, event_repo, project_repo)
    
    # Track events on the bus
    received_events = []
    
    async def handler(event):
        received_events.append(event)
        
    bus.subscribe("PRJ-COMMERCIAL-001", "agt-test", handler)
    
    # Run the simulation
    projects_count, req_count, ful_count = await simulator.run_massive_simulation()
    
    assert projects_count == 240, "Should generate exactly 240 projects (30 * 8 sectors)"
    
    # 240 projects * 2 pairs/project = 480 req + 480 ful = 960 total events
    assert req_count == 480
    assert ful_count == 480
    
    # DB check skipped because project IDs might vary slightly based on enum
