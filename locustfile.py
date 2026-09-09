import time
import uuid
import json
from locust import HttpUser, task, between, events
from locust.user.task import TaskSet

# Use an admin token for tests or mock a tenant
JWT_TOKEN = None

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    global JWT_TOKEN
    # In a real scenario, this would authenticate to `/api/token`
    # Here we simulate fetching the master token.
    # Note: Locust needs to make a standard HTTP request.
    pass

class SwarmBehavior(TaskSet):
    
    def on_start(self):
        """Executed when a simulated agent starts up."""
        self.tenant_id = f"tenant-{uuid.uuid4().hex[:8]}"
        self.agent_id = f"agent-{uuid.uuid4().hex[:6]}"
        self.headers = {"X-Mycelium-API-Key": "test-secret-key"} # Using master key for bypass
        
    @task(3)
    def check_health(self):
        self.client.get("/health", headers=self.headers)
        
    @task(1)
    def create_project(self):
        payload = {
            "title": f"LoadTest-{uuid.uuid4().hex[:4]}",
            "vision": "A load testing simulation project.",
            "creator_id": self.agent_id,
            "distilled_specs": "Should withstand 1000 requests per second."
        }
        self.client.post("/api/projects", json=payload, headers=self.headers)
        
    @task(5)
    def overview_analytics(self):
        self.client.get("/api/analytics/overview", headers=self.headers)

class MyceliumAgent(HttpUser):
    tasks = [SwarmBehavior]
    wait_time = between(1, 5) # Agents wait 1-5 seconds between actions

    # Note: For WebSocket load testing, you'd typically write a custom WebSocketUser.
    # We focus on HTTP endpoints for standard load testing in this iteration.
