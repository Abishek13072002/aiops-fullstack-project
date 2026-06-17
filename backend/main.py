from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random
import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


app = FastAPI(title="Enterprise AIOps Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

incidents = []


def get_timestamp():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None

    if OpenAI is None:
        return None

    return OpenAI(api_key=api_key)


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
        "timestamp": get_timestamp(),
    }


@app.get("/")
def home():
    return {
        "message": "Enterprise AIOps Backend Running",
        "status": "Healthy",
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
        incidents.append(incident)

    return {
        "cpu": cpu,
        "memory": memory,
        "latency": latency,
        "status": status,
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
        "timestamp": get_timestamp(),
    }

    incidents.append(incident)

    return {
        "status": "error simulated",
        "incident": incident,
    }


@app.get("/ai-root-cause")
def ai_root_cause():
    latest_incident = incidents[-1] if incidents else {
        "message": "No incidents available"
    }

    client = get_openai_client()

    if client is None:
        return {
            "incident": latest_incident,
            "ai_analysis": {
                "root_cause": "OpenAI API key is not configured or OpenAI package is missing.",
                "severity": "Unknown",
                "business_impact": "AI analysis is currently unavailable.",
                "recommended_fix": "Verify OPENAI_API_KEY Kubernetes secret and requirements.txt.",
                "prevention_step": "Ensure CI/CD pipeline installs the openai package and injects the secret."
            }
        }

    prompt = f"""
You are an enterprise AIOps engineer.

Analyze the following incident and provide:
1. Root cause
2. Severity
3. Business impact
4. Recommended fix
5. Prevention step

Incident:
{latest_incident}
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        return {
            "incident": latest_incident,
            "ai_analysis": response.output_text
        }

    except Exception as error:
        return {
            "incident": latest_incident,
            "ai_analysis": {
                "root_cause": "AI analysis request failed.",
                "severity": "Unknown",
                "business_impact": "AI-based root cause analysis could not be completed.",
                "recommended_fix": str(error),
                "prevention_step": "Check OpenAI API key, network access, model name, and package version."
            }
        }


@app.get("/health")
def health():
    return {
        "status": "UP",
    }