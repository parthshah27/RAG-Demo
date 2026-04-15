import { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";
import "../styles/chat.css";

export default function Chat({ setToken, config }) {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const ask = async () => {
    const trimmedQuery = query.trim();
    if (!trimmedQuery) return;

    try {
      setLoading(true);
      setError("");
      const res = await API.post("/ask", { query: trimmedQuery });

      setMessages((currentMessages) => [
        ...currentMessages,
        { type: "user", text: trimmedQuery },
        { type: "bot", text: res.data.answer },
      ]);

      setQuery("");
    } catch (err) {
      console.error("Chat error:", err);
      setError(
        err.response?.data?.detail ||
          "Failed to get response. Please try again."
      );
      setMessages((currentMessages) => [
        ...currentMessages,
        { type: "user", text: trimmedQuery },
      ]);
      setQuery("");
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem("token");
    navigate("/login");
  };

  if (!config) return <div>Loading...</div>;

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>{config.title}</h2>
        <button className="logout-btn" onClick={logout}>
          Logout
        </button>
      </div>

      <div className="chat-box">
        {messages.map((msg, index) => (
          <div key={`${msg.type}-${index}`} className={msg.type}>
            {msg.text}
          </div>
        ))}
        {error && <div className="error-msg">Error: {error}</div>}
      </div>

      <div className="input-box">
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(event) => event.key === "Enter" && !loading && ask()}
          placeholder={config?.ui?.chat_placeholder || `Ask about ${config.domain}...`}
          disabled={loading}
        />
        <button onClick={ask} disabled={loading}>
          {loading ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
}
