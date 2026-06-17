import React, { useEffect, useState } from "react";

function App() {
  const [metrics, setMetrics] = useState({
    cpu: 0,
    memory: 0,
    latency: 0,
    status: "Loading...",
    self_heal_required: false
  });

  const [incidents, setIncidents] = useState([]);
  const [healMessage, setHealMessage] = useState("");

  const backendUrl = "http://a70ddf5e3581947ebac9f2d87793af7d-1117394785.ap-south-1.elb.amazonaws.com";

  const loadData = async () => {
    try {
      const metricsResponse = await fetch(`${backendUrl}/metrics-summary`);
      const metricsData = await metricsResponse.json();
      setMetrics(metricsData);

      const incidentsResponse = await fetch(`${backendUrl}/incidents`);
      const incidentsData = await incidentsResponse.json();
      setIncidents(incidentsData);
    } catch (error) {
      console.error("Backend connection failed:", error);
    }
  };

  const simulateError = async () => {
    await fetch(`${backendUrl}/simulate-error`);
    loadData();
  };

  const approveSelfHeal = async () => {
    setHealMessage("Self-healing is in progress...");

    try {
      const response = await fetch(`${backendUrl}/approve-self-heal`, {
        method: "POST"
      });

      const data = await response.json();

      setHealMessage(
        `Self-healing completed. Backend scaled from ${data.old_replicas} to ${data.new_replicas} replicas.`
      );

      loadData();
    } catch (error) {
      setHealMessage("Self-healing failed. Please check backend logs.");
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const severityColor = (severity) => {
    if (severity === "Critical") return "#dc2626";
    if (severity === "High") return "#f97316";
    if (severity === "Medium") return "#eab308";
    if (severity === "Resolved") return "#16a34a";
    return "#16a34a";
  };

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>Enterprise AIOps Platform</h1>
          <p style={styles.subtitle}>
            Monitoring, incident detection, approval-based self-healing, and Kubernetes remediation
          </p>
        </div>
        <div style={styles.badge}>AWS EKS • Prometheus • Loki • Grafana</div>
      </div>

      <div style={styles.grid}>
        <div style={styles.card}>
          <h3>CPU Usage</h3>
          <h2 style={{ color: metrics.cpu > 90 ? "#dc2626" : "#111827" }}>
            {metrics.cpu}%
          </h2>
        </div>

        <div style={styles.card}>
          <h3>Memory Usage</h3>
          <h2>{metrics.memory}%</h2>
        </div>

        <div style={styles.card}>
          <h3>Latency</h3>
          <h2>{metrics.latency} ms</h2>
        </div>

        <div style={styles.card}>
          <h3>System Status</h3>
          <h2 style={{ color: metrics.status === "Healthy" ? "#16a34a" : "#dc2626" }}>
            {metrics.status}
          </h2>
        </div>
      </div>

      {metrics.self_heal_required && (
        <div style={styles.healCard}>
          <div>
            <h2>Critical CPU Threshold Breached</h2>
            <p>
              CPU usage is above 90%. Approval is required before automatic Kubernetes remediation.
            </p>
          </div>
          <button style={styles.healButton} onClick={approveSelfHeal}>
            Approve Self-Heal
          </button>
        </div>
      )}

      {healMessage && (
        <div style={styles.messageBox}>
          {healMessage}
        </div>
      )}

      <div style={styles.actionCard}>
        <div>
          <h2>AIOps Incident Simulation</h2>
          <p>
            Simulate an application failure and verify detection in dashboard, Loki logs,
            Prometheus metrics, and Alertmanager.
          </p>
        </div>
        <button style={styles.button} onClick={simulateError}>
          Simulate Application Error
        </button>
      </div>

      <div style={styles.section}>
        <h2>Detected Incidents</h2>

        {incidents.length === 0 ? (
          <div style={styles.empty}>No active incidents detected.</div>
        ) : (
          <div style={styles.incidentGrid}>
            {incidents.map((incident, index) => (
              <div key={index} style={styles.incidentCard}>
                <div style={styles.incidentHeader}>
                  <h3>{incident.type}</h3>
                  <span
                    style={{
                      ...styles.severity,
                      backgroundColor: severityColor(incident.severity)
                    }}
                  >
                    {incident.severity}
                  </span>
                </div>

                <p><strong>Root Cause:</strong> {incident.root_cause}</p>
                <p><strong>Recommendation:</strong> {incident.recommendation}</p>
                <p><strong>Timestamp:</strong> {incident.timestamp}</p>

                {incident.cpu !== undefined && (
                  <p>
                    <strong>Metrics:</strong> CPU {incident.cpu}% | Memory {incident.memory}% | Latency {incident.latency} ms
                  </p>
                )}

                {incident.self_heal_required && (
                  <p style={{ color: "#dc2626", fontWeight: "bold" }}>
                    Approval required for self-healing.
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #0f172a, #1e293b)",
    color: "#e5e7eb",
    fontFamily: "Segoe UI, Arial, sans-serif",
    padding: "35px"
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "30px"
  },
  title: {
    fontSize: "42px",
    margin: "0",
    color: "#ffffff"
  },
  subtitle: {
    fontSize: "16px",
    color: "#cbd5e1"
  },
  badge: {
    background: "#2563eb",
    padding: "12px 18px",
    borderRadius: "30px",
    fontWeight: "bold"
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: "20px",
    marginBottom: "25px"
  },
  card: {
    background: "#ffffff",
    color: "#111827",
    padding: "25px",
    borderRadius: "18px",
    boxShadow: "0 10px 25px rgba(0,0,0,0.25)"
  },
  healCard: {
    background: "#7f1d1d",
    border: "1px solid #ef4444",
    padding: "25px",
    borderRadius: "18px",
    marginBottom: "25px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center"
  },
  healButton: {
    background: "#22c55e",
    color: "#ffffff",
    padding: "14px 22px",
    border: "none",
    borderRadius: "10px",
    fontWeight: "bold",
    cursor: "pointer"
  },
  messageBox: {
    background: "#ecfdf5",
    color: "#065f46",
    padding: "18px",
    borderRadius: "12px",
    marginBottom: "25px",
    fontWeight: "bold"
  },
  actionCard: {
    background: "#1d4ed8",
    padding: "25px",
    borderRadius: "18px",
    marginBottom: "25px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center"
  },
  button: {
    background: "#facc15",
    color: "#111827",
    padding: "14px 22px",
    border: "none",
    borderRadius: "10px",
    fontWeight: "bold",
    cursor: "pointer"
  },
  section: {
    background: "#ffffff",
    color: "#111827",
    padding: "25px",
    borderRadius: "18px"
  },
  empty: {
    padding: "20px",
    background: "#f1f5f9",
    borderRadius: "12px"
  },
  incidentGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
    gap: "18px"
  },
  incidentCard: {
    border: "1px solid #e5e7eb",
    borderRadius: "14px",
    padding: "18px",
    background: "#f8fafc"
  },
  incidentHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center"
  },
  severity: {
    color: "#ffffff",
    padding: "6px 12px",
    borderRadius: "20px",
    fontWeight: "bold"
  }
};

export default App;