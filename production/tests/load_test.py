from locust import HttpUser, task, between
import random

class WebFormUser(HttpUser):
    wait_time = between(2, 10)
    weight = 3

    @task(3)
    def submit_support_form(self):
        categories = ['general', 'technical', 'billing', 'feedback', 'bug_report']
        self.client.post("/support/submit", json={
            "name": f"Load Test User {random.randint(1, 10000)}",
            "email": f"loadtest{random.randint(1, 10000)}@example.com",
            "subject": f"Load Test Query {random.randint(1, 100)}",
            "category": random.choice(categories),
            "message": "This is a load test message to verify system performance under stress conditions."
        })

    @task(1)
    def check_health(self):
        self.client.get("/health")

    @task(1)
    def check_metrics(self):
        self.client.get("/metrics/channels")

class HealthCheckUser(HttpUser):
    wait_time = between(5, 15)
    weight = 1

    @task
    def check_health(self):
        self.client.get("/health")
