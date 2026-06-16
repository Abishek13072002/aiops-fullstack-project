import React, { useEffect, useState } from "react";

function App() {
  const [metrics, setMetrics] = useState({
    cpu: 0,
    memory: 0,
    latency: 0,
    status: "Loading..."
  });

  const [incidents, setIncidents] = useState([]);

  const backendUrl = "http://a94ed1c0ff1794fedbd10f3ef7a56df4-455779412.ap-south-1.elb.amazonaws.com";

  const loadData = async () => {
    try {
      const metricsResponse = await fetch(
        `${backendUrl}/metrics-summary`
      );

      const metricsData = await metricsResponse.json();

      setMetrics(metricsData);

      const incidentsResponse = await fetch(
        `${backendUrl}/incidents`
      );

      const incidentsData = await incidentsResponse.json();

      setIncidents(incidentsData);

    } catch (error) {
      console.error("Error loading data:", error);
    }
  };

  const simulateError = async () => {
    try {
      await fetch(`${backendUrl}/simulate-error`);
      loadData();
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    loadData();

    const interval = setInterval(() => {
      loadData();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div
      style={{
        padding: "30px",
        fontFamily: "Arial",
        backgroundColor: "#f5f5f5",
        minHeight: "100vh"
      }}
    >
      <h1>AIOps Incident Detection Dashboard</h1>

      <div
        style={{
          backgroundColor: "white",
          padding: "20px",
          borderRadius: "10px",
          marginBottom: "20px"
        }}
      >
        <h2>System Metrics</h2>

        <p>
          <strong>CPU Usage:</strong> {metrics.cpu}%
        </p>

        <p>
          <strong>Memory Usage:</strong> {metrics.memory}%
        </p>

        <p>
          <strong>Latency:</strong> {metrics.latency} ms
        </p>

        <p>
          <strong>Status:</strong> {metrics.status}
        </p>

        <button
          onClick={simulateError}
          style={{
            padding: "10px",
            cursor: "pointer"
          }}
        >
          Simulate Application Error
        </button>
      </div>

      <div
        style={{
          backgroundColor: "white",
          padding: "20px",
          borderRadius: "10px"
        }}
      >
        <h2>Detected Incidents</h2>

        {incidents.length === 0 ? (
          <p>No incidents detected.</p>
        ) : (
          <ul>
            {incidents.map((incident, index) => (
              <li key={index}>
                {JSON.stringify(incident)}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default App;