from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random
import requests

from kubernetes import client, config

app = FastAPI(title="Enterprise AIOps Backend with Auto Scaling Self-Healing")

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
    "node_cpu": 0,
    "status": "Healthy",
    "self_heal_required": False,
    "auto_scaled": False,
}


def get_timestamp():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


def load_k8s_config():
    try:
        config.load_incluster_config()
    except Exception:
        config.load_kube_config()


def get_backend_replicas():
    load_k8s_config()
    apps_v1 = client.AppsV1Api()

    scale = apps_v1.read_namespaced_deployment_scale(
        name="aiops-backend",
        namespace="default",
    )

    return scale.spec.replicas


def scale_backend(replicas):
    load_k8s_config()
    apps_v1 = client.AppsV1Api()

    scale = apps_v1.read_namespaced_deployment_scale(
        name="aiops-backend",
        namespace="default",
    )

    old_replicas = scale.spec.replicas
    scale.spec.replicas = replicas

    apps_v1.patch_namespaced_deployment_scale(
        name="aiops-backend",
        namespace="default",
        body=scale,
    )

    return old_replicas, replicas


def get_node_cpu_from_metrics_api():
    try:
        load_k8s_config()

        api_client = client.ApiClient()
        custom_api = client.CustomObjectsApi(api_client)

        metrics = custom_api.list_cluster_custom_object(
            group="metrics.k8s.io",
            version="v1beta1",
            plural="nodes",
        )

        total_cpu_millicores = 0
        total_node_count = 0

        for item in metrics.get("items", []):
            cpu_value = item["usage"]["cpu"]

            if cpu_value.endswith("n"):
                cpu_millicores = int(cpu_value.replace("n", "")) / 1000000
            elif cpu_value.endswith("u"):
                cpu_millicores = int(cpu_value.replace("u", "")) / 1000
            elif cpu_value.endswith("m"):
                cpu_millicores = int(cpu_value.replace("m", ""))
            else:
                cpu_millicores = int(cpu_value) * 1000

            total_cpu_millicores += cpu_millicores
            total_node_count += 1

        if total_node_count == 0:
            return 0

        # Demo calculation. This converts usage into a readable percentage-like value.
        average_millicores = total_cpu_millicores / total_node_count
        node_cpu_percent = min(round((average_millicores / 1000) * 100), 100)

        return node_cpu_percent

    except Exception:
        # fallback for demo if metrics API fails
        return random.randint(40, 95)


def create_incident(cpu, memory, latency, node_cpu):
    if node_cpu > 90:
        return {
            "type": "Node CPU Auto Scale Up",
            "severity": "Critical",
            "root_cause": "Node CPU exceeded 90%",
            "recommendation": "Automatically scale backend deployment up",
            "cpu": cpu,
            "memory": memory,
            "latency": latency,
            "node_cpu": node_cpu,
            "timestamp": get_timestamp(),
        }

    if node_cpu < 70:
        return {
            "type": "Node CPU Auto Scale Down",
            "severity": "Low",
            "root_cause": "Node CPU dropped below 70%",
            "recommendation": "Automatically scale backend deployment down",
            "cpu": cpu,
            "memory": memory,
            "latency": latency,
            "node_cpu": node_cpu,
            "timestamp": get_timestamp(),
        }

    if cpu > 80:
        return {
            "type": "Application Performance Issue",
            "severity": "High",
            "root_cause": "Application CPU utilization is high",
            "recommendation": "Monitor application workload",
            "cpu": cpu,
            "memory": memory,
            "latency": latency,
            "node_cpu": node_cpu,
            "timestamp": get_timestamp(),
        }

    return None


@app.get("/")
def home():
    return {
        "message": "Enterprise AIOps Backend Running with Node CPU Auto Scaling",
        "status": "Healthy",
    }


@app.get("/metrics-summary")
def metrics_summary():
    global last_metrics

    cpu = random.randint(10, 98)
    memory = random.randint(20, 95)
    latency = random.randint(50, 1000)
    node_cpu = get_node_cpu_from_metrics_api()

    status = "Healthy"
    auto_scaled = False

    current_replicas = get_backend_replicas()

    if node_cpu > 90 and current_replicas < 4:
        old, new = scale_backend(4)
        auto_scaled = True
        status = "Auto Scaled Up"

        incidents.append({
            "type": "Auto Scale Up Executed",
            "severity": "Critical",
            "root_cause": "Node CPU exceeded 90%",
            "recommendation": "Backend replicas increased automatically",
            "node_cpu": node_cpu,
            "old_replicas": old,
            "new_replicas": new,
            "timestamp": get_timestamp(),
        })

    elif node_cpu < 70 and current_replicas > 2:
        old, new = scale_backend(2)
        auto_scaled = True
        status = "Auto Scaled Down"

        incidents.append({
            "type": "Auto Scale Down Executed",
            "severity": "Resolved",
            "root_cause": "Node CPU dropped below 70%",
            "recommendation": "Backend replicas reduced automatically",
            "node_cpu": node_cpu,
            "old_replicas": old,
            "new_replicas": new,
            "timestamp": get_timestamp(),
        })

    else:
        incident = create_incident(cpu, memory, latency, node_cpu)

        if incident:
            status = "Incident Detected"
            incidents.append(incident)

    last_metrics = {
        "cpu": cpu,
        "memory": memory,
        "latency": latency,
        "node_cpu": node_cpu,
        "status": status,
        "self_heal_required": False,
        "auto_scaled": auto_scaled,
        "current_replicas": get_backend_replicas(),
    }

    return last_metrics


@app.get("/incidents")
def get_incidents():
    return incidents[-20:]


@app.get("/simulate-high-node-cpu")
def simulate_high_node_cpu():
    old, new = scale_backend(4)

    incident = {
        "type": "Simulated Auto Scale Up",
        "severity": "Critical",
        "root_cause": "Simulated node CPU above 90%",
        "recommendation": "Backend scaled up automatically",
        "node_cpu": 95,
        "old_replicas": old,
        "new_replicas": new,
        "timestamp": get_timestamp(),
    }

    incidents.append(incident)

    return incident


@app.get("/simulate-low-node-cpu")
def simulate_low_node_cpu():
    old, new = scale_backend(2)

    incident = {
        "type": "Simulated Auto Scale Down",
        "severity": "Resolved",
        "root_cause": "Simulated node CPU below 70%",
        "recommendation": "Backend scaled down automatically",
        "node_cpu": 60,
        "old_replicas": old,
        "new_replicas": new,
        "timestamp": get_timestamp(),
    }

    incidents.append(incident)

    return incident


@app.get("/simulate-error")
def simulate_error():
    incident = {
        "type": "Application Failure",
        "severity": "Critical",
        "root_cause": "HTTP 500 Internal Server Error",
        "recommendation": "Check application logs and restart affected service",
        "timestamp": get_timestamp(),
    }

    incidents.append(incident)

    return {
        "status": "error simulated",
        "incident": incident,
    }


@app.get("/health")
def health():
    return {
        "status": "UP",
    }