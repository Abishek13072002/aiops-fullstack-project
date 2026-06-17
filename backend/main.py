from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random

from kubernetes import client, config

app = FastAPI(title="Enterprise AIOps Backend with Approval Based Self Healing")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

incidents = []
last_metrics = {
    "cpu": 0,
    "memory": 0,
    "latency": 0,
    "status": "Healthy",
    "self_heal_required": False
}


def get_timestamp():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


def create_incident(cpu, memory, latency):
    if cpu > 90:
        return {
            "type": "High CPU Auto-Heal Required",
            "severity": "Critical",
            "root_cause": "CPU utilization exceeded 90%",
            "recommendation": "Approve self-healing to scale backend pods to 3 replicas",
            "cpu": cpu,
            "memory": memory,
            "latency": latency,
            "self_heal_required": True,
            "timestamp": get_timestamp(),
        }

    if cpu > 80:
        return {
            "type": "Performance Issue",
            "severity": "High",
            "root_cause": "High CPU Utilization",
            "recommendation": "Monitor CPU usage and prepare for scaling",
            "cpu": cpu,
            "memory": memory,
            "latency": latency,
            "self_heal_required": False,
            "timestamp": get_timestamp(),
        }

    if memory > 85:
        return {
            "type": "Resource Issue",
            "severity": "High",
            "root_cause": "High Memory Utilization",
            "recommendation": "Increase memory limits or scale workload",
            "cpu": cpu,
            "memory": memory,
            "latency": latency,
            "self_heal_required": False,
            "timestamp": get_timestamp(),
        }

    if latency > 700:
        return {
            "type": "Latency Issue",
            "severity": "Medium",
            "root_cause": "High Response Time",
            "recommendation": "Investigate network latency and application performance",
            "cpu": cpu,
            "memory": memory,
            "latency": latency,
            "self_heal_required": False,
            "timestamp": get_timestamp(),
        }

    return None


@app.get("/")
def home():
    return {
        "message": "Enterprise AIOps Backend Running with Approval Based Self Healing",
        "status": "Healthy"
    }


@app.get("/metrics-summary")
def metrics_summary():
    global last_metrics

    cpu = random.randint(10, 98)
    memory = random.randint(20, 95)
    latency = random.randint(50, 1000)

    status = "Healthy"
    self_heal_required = False

    incident = create_incident(cpu, memory, latency)

    if incident:
        status = "Incident Detected"
        self_heal_required = incident["self_heal_required"]
        incidents.append(incident)

    last_metrics = {
        "cpu": cpu,
        "memory": memory,
        "latency": latency,
        "status": status,
        "self_heal_required": self_heal_required
    }

    return last_metrics


@app.get("/incidents")
def get_incidents():
    return incidents[-20:]


@app.post("/approve-self-heal")
@app.get("/approve-self-heal")
def approve_self_heal():
    try:
        config.load_incluster_config()

        apps_v1 = client.AppsV1Api()

        deployment_name = "aiops-backend"
        namespace = "default"

        scale = apps_v1.read_namespaced_deployment_scale(
            name=deployment_name,
            namespace=namespace
        )

        old_replicas = scale.spec.replicas
        scale.spec.replicas = 3

        apps_v1.patch_namespaced_deployment_scale(
            name=deployment_name,
            namespace=namespace,
            body=scale
        )

        remediation_incident = {
            "type": "Self Healing Approved",
            "severity": "Resolved",
            "root_cause": "High CPU utilization exceeded 90%",
            "recommendation": "Backend deployment scaled successfully",
            "old_replicas": old_replicas,
            "new_replicas": 3,
            "timestamp": get_timestamp()
        }

        incidents.append(remediation_incident)

        return {
            "status": "Self healing executed successfully",
            "deployment": deployment_name,
            "old_replicas": old_replicas,
            "new_replicas": 3
        }

    except Exception as error:
        return {
            "status": "Self healing failed",
            "error": str(error)
        }


@app.get("/simulate-error")
def simulate_error():
    incident = {
        "type": "Application Failure",
        "severity": "Critical",
        "root_cause": "HTTP 500 Internal Server Error",
        "recommendation": "Check application logs and restart affected service",
        "self_heal_required": False,
        "timestamp": get_timestamp(),
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