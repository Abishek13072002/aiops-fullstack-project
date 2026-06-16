from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI(title="AIOps Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

incidents = []

@app.get("/")
def home():
    return {"message": "AIOps Backend is running"}

@app.get("/metrics-summary")
def metrics_summary():
    cpu = random.randint(10, 95)
    memory = random.randint(20, 90)
    latency = random.randint(50, 1000)

    status = "Healthy"
    if cpu > 80 or memory > 80 or latency > 700:
        status = "Incident Detected"
        incidents.append({
            "type": "Performance Issue",
            "cpu": cpu,
            "memory": memory,
            "latency": latency
        })

    return {
        "cpu": cpu,
        "memory": memory,
        "latency": latency,
        "status": status
    }

@app.get("/incidents")
def get_incidents():
    return incidents

@app.get("/simulate-error")
def simulate_error():
    incidents.append({"type": "Application Error", "message": "500 error simulated"})
    return {"status": "error simulated"}