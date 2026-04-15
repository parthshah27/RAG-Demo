import { useState } from "react";
import { useNavigate } from "react-router-dom";
import ChatModal from "../components/ChatModal";
import "../styles/landing.css";

export default function Landing({ config, setToken }) {
  const [showChat, setShowChat] = useState(false);
  const navigate = useNavigate();

  if (!config) return <div>Loading...</div>;

  const logout = () => {
    setToken(null);
    localStorage.removeItem("token");
    navigate("/login");
  };

  const dashboardData = config.ui?.dashboard?.metrics || [];
  const insights = config.ui?.dashboard?.insights || [];

  return (
    <div className="landing">
      <header className="dashboard-header">
        <div className="header-content">
          <div>
            <h1>{config.title}</h1>
            <p>{config.description}</p>
          </div>
          <button className="logout-btn" onClick={logout}>
            Logout
          </button>
        </div>
      </header>

      <div className="dashboard-grid">
        {dashboardData.map((item) => (
          <div key={item.label} className="metric-card">
            <h3>{item.label}</h3>
            <div className="metric-value">{item.value}</div>
            <div
              className={`metric-change ${
                item.change.startsWith("+")
                  ? "positive"
                  : item.change.startsWith("-")
                    ? "negative"
                    : "neutral"
              }`}
            >
              {item.change}
            </div>
          </div>
        ))}
      </div>

      <div className="dashboard-content">
        <div className="data-section">
          <h2>Key Insights</h2>
          <div className="insights-grid">
            {insights.map((item) => (
              <div key={item.title} className="insight-card">
                <h4>{item.title}</h4>
                <p>{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <button
        type="button"
        className="chat-icon"
        onClick={() => setShowChat(true)}
        aria-label="Open AI assistant"
      >
        💬
      </button>

      {showChat && <ChatModal config={config} onClose={() => setShowChat(false)} />}
    </div>
  );
}
