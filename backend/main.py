```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random

app = FastAPI(title="Enterprise AIOps Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

incidents = []


def create_incident(cpu, memory, latency):
    incident_type = "Healthy"
    severity = "Low"
    root_cause = "No issues detected"
    recommendation = "System operating normally"

    if cpu > 80:
        incident_type = "Performance Issue"
        severity = "High"
        root_cause = "High CPU Utilization"
        recommendation = "Scale application pods or increase node capacity"

    elif memory > 85:
        incident_type = "Resource Issue"
        severity = "High"
        root_cause = "High Memory Utilization"
        recommendation = "Increase memory limits or scale workload"

    elif latency > 700:
        incident_type = "Latency Issue"
        severity = "Medium"
        root_cause = "High Response Time"
        recommendation = "Investigate network latency and application performance"

    return {
        "type": incident_type,
        "severity": severity,
        "root_cause": root_cause,
        "recommendation": recommendation,
        "cpu": cpu,
        "memory": memory,
        "latency": latency,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }


@app.get("/")
def home():
    return {
        "message": "Enterprise AIOps Backend Running",
        "status": "Healthy"
    }


@app.get("/metrics-summary")
def metrics_summary():

    cpu = random.randint(10, 95)
    memory = random.randint(20, 95)
    latency = random.randint(50, 1000)

    status = "Healthy"

    if cpu > 80 or memory > 85 or latency > 700:
        status = "Incident Detected"

        incident = create_incident(cpu, memory, latency)

        if incident["type"] != "Healthy":
            incidents.append(incident)

    return {
        "cpu": cpu,
        "memory": memory,
        "latency": latency,
        "status": status
    }


@app.get("/incidents")
def get_incidents():
    return incidents[-20:]


@app.get("/simulate-error")
def simulate_error():

    incident = {
        "type": "Application Failure",
        "severity": "Critical",
        "root_cause": "HTTP 500 Internal Server Error",
        "recommendation": "Check application logs and restart affected service",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

    incidents.append(incident)

    return {
        "status": "error simulated",
        "incident": incident
    }


@app.get("/health")
def health():
    return {
        "status": "UP"
    }
```
