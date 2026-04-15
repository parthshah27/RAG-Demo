import { useState } from "react";
import { useNavigate } from "react-router-dom";
import ChatModal from "../components/ChatModal";
import "../styles/landing.css";

const SAMPLE_DATA = {
  finance: [
    { label: "Total Revenue", value: "INR 2.5L Cr", change: "+12%" },
    { label: "Fiscal Deficit", value: "5.2%", change: "-0.8%" },
    { label: "Tax Collection", value: "INR 18.5L Cr", change: "+8%" },
    { label: "GDP Growth", value: "7.2%", change: "+1.2%" },
  ],
  healthcare: [
    { label: "Total Patients", value: "45,200", change: "+15%" },
    { label: "Recovery Rate", value: "94.5%", change: "+2.1%" },
    { label: "Bed Occupancy", value: "78%", change: "-3%" },
    { label: "Avg. Stay", value: "5.2 days", change: "-0.5 days" },
  ],
  ecommerce: [
    { label: "Total Sales", value: "$2.5M", change: "+23%" },
    { label: "Active Users", value: "15,200", change: "+18%" },
    { label: "Conversion Rate", value: "3.8%", change: "+0.5%" },
    { label: "Avg. Order", value: "$145", change: "+12%" },
  ],
  agriculture: [
    { label: "Crop Yield", value: "15.6 t/ha", change: "+8%" },
    { label: "Farmers", value: "42,000", change: "+5%" },
    { label: "Irrigation Eff.", value: "78%", change: "+3%" },
    { label: "Soil Health", value: "6.8 pH", change: "Stable" },
  ],
};

export default function Landing({ config, setToken }) {
  const [showChat, setShowChat] = useState(false);
  const navigate = useNavigate();

  if (!config) return <div>Loading...</div>;

  const logout = () => {
    setToken(null);
    localStorage.removeItem("token");
    navigate("/login");
  };

  const dashboardData = SAMPLE_DATA[config.domain] || SAMPLE_DATA.finance;

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
            <div className="insight-card">
              <h4>Trend Analysis</h4>
              <p>
                Showing positive growth across all major metrics with consistent
                improvement patterns.
              </p>
            </div>
            <div className="insight-card">
              <h4>Performance Overview</h4>
              <p>
                Overall system performance is optimal with efficient resource
                utilization.
              </p>
            </div>
            <div className="insight-card">
              <h4>Future Projections</h4>
              <p>
                Based on current trends, we project continued growth and
                improved outcomes.
              </p>
            </div>
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
