/**
 * Chat Component - Main conversational interface
 * 
 * Features:
 * - Real-time message streaming
 * - JWT token-based authentication
 * - Loading states and error handling
 * - Domain-specific configuration support
 * - Logout functionality
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";
import "../styles/chat.css";

/**
 * Chat functional component
 * 
 * @param {Function} setToken - Function to update app-level auth token (for logout)
 * @param {Object} config - Domain configuration object from /config endpoint
 * @param {string} config.domain - Current domain (e.g., 'healthcare', 'retail')
 * @param {string} config.title - Page title
 * @param {Object} config.ui - UI configuration
 * @param {string} config.ui.chat_placeholder - Input placeholder text
 * @returns {JSX.Element} Chat interface
 */
export default function Chat({ setToken, config }) {
  // State management
  const [query, setQuery] = useState(""); // Current user input
  const [messages, setMessages] = useState([]); // Chat message history
  const [loading, setLoading] = useState(false); // API call in progress
  const [error, setError] = useState(""); // Error message display
  const navigate = useNavigate(); // Navigation hook for logout redirect

  /**
   * Send query to RAG backend and receive answer
   * 
   * Process:
   * 1. Validate query is not empty
   * 2. Add user message to chat
   * 3. Call /ask endpoint
   * 4. Add bot response to chat
   * 5. Handle errors gracefully
   * 
   * @async
   */
  const ask = async () => {
    const trimmedQuery = query.trim();
    if (!trimmedQuery) return;

    try {
      setLoading(true);
      setError("");
      
      // Call RAG API endpoint
      const res = await API.post("/ask", { query: trimmedQuery });

      // Update chat with user message and bot response
      setMessages((currentMessages) => [
        ...currentMessages,
        { type: "user", text: trimmedQuery },
        { type: "bot", text: res.data.answer },
      ]);

      // Clear input for next query
      setQuery("");
    } catch (err) {
      // Handle API errors
      console.error("Chat error:", err);
      setError(
        err.response?.data?.detail ||
          "Failed to get response. Please try again."
      );
      
      // Still add user message even on error
      setMessages((currentMessages) => [
        ...currentMessages,
        { type: "user", text: trimmedQuery },
      ]);
      setQuery("");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Logout user - clear token and redirect to login
   */
  const logout = () => {
    setToken(null);
    localStorage.removeItem("token");
    navigate("/login");
  };

  if (!config) return <div>Loading...</div>;

  return (
    <div className="chat-container">
      {/* Header with title and logout button */}
      <div className="chat-header">
        <h2>{config.title}</h2>
        <button className="logout-btn" onClick={logout}>
          Logout
        </button>
      </div>

      {/* Chat message display area */}
      <div className="chat-box">
        {messages.map((msg, index) => (
          <div key={`${msg.type}-${index}`} className={msg.type}>
            {msg.text}
          </div>
        ))}
        {error && <div className="error-msg">Error: {error}</div>}
      </div>

      {/* Input area with send button */}
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
