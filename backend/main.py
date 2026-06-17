from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random
import os
import json
import boto3

app = FastAPI(title="Enterprise AIOps Backend with AWS Bedrock")

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


def create_incident(cpu, memory, latency):
    if cpu > 80:
        return {
            "type": "Performance Issue",
            "severity": "High",
            "root_cause": "High CPU Utilization",
            "recommendation": "Scale application pods or increase node capacity",
            "cpu": cpu,
            "memory": memory,
            "latency": latency,
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
            "timestamp": get_timestamp(),
        }

    return None


@app.get("/")
def home():
    return {
        "message": "Enterprise AIOps Backend Running with AWS Bedrock",
        "status": "Healthy",
    }


@app.get("/metrics-summary")
def metrics_summary():
    cpu = random.randint(10, 95)
    memory = random.randint(20, 95)
    latency = random.randint(50, 1000)

    status = "Healthy"
    incident = create_incident(cpu, memory, latency)

    if incident:
        status = "Incident Detected"
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

    region = os.getenv("AWS_REGION", "us-east-1")
    model_id = os.getenv(
        "BEDROCK_MODEL_ID",
        "anthropic.claude-3-haiku-20240307-v1:0"
    )

    prompt = f"""
You are an enterprise AIOps engineer.

Analyze the following production incident and provide:
1. Root Cause
2. Severity
3. Business Impact
4. Recommended Fix
5. Prevention Step

Incident:
{latest_incident}
"""

    try:
        bedrock = boto3.client("bedrock-runtime", region_name=region)

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(response["body"].read())
        ai_text = response_body["content"][0]["text"]

        return {
            "incident": latest_incident,
            "ai_provider": "AWS Bedrock",
            "model": model_id,
            "ai_analysis": ai_text
        }

    except Exception as error:
        return {
            "incident": latest_incident,
            "ai_provider": "AWS Bedrock",
            "model": model_id,
            "ai_analysis": {
                "root_cause": "Bedrock analysis failed",
                "severity": "Unknown",
                "business_impact": "AI root cause analysis unavailable",
                "recommended_fix": str(error),
                "prevention_step": "Check IAM permission, Bedrock model access, AWS region, and model ID"
            }
        }


@app.get("/health")
def health():
    return {
        "status": "UP",
    }