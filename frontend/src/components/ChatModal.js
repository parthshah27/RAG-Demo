import { useEffect, useRef, useState } from "react";
import API from "../api";
import "../styles/chat.css";

export default function ChatModal({ config, onClose }) {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [uploadedFile, setUploadedFile] = useState(null);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const domain = config?.domain || "general";
  const uploadPrompt = config?.ui?.upload_prompt || "Analyze this file";
  const allowedTypes =
    config?.ui?.allowed_file_types || [".csv", ".txt", ".pdf", ".md"];
  const acceptValue = allowedTypes.join(",");
  const sampleQueries =
    config?.ui?.sample_queries || ["Ask me anything about the data..."];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  const uploadSelectedFile = async (file) => {
    const formData = new FormData();
    formData.append("upload", file);
    const response = await API.post("/upload/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  };

  const ask = async () => {
    const trimmedQuery = query.trim();
    if (!trimmedQuery && !uploadedFile) return;

    const userMessage = {
      type: "user",
      text: trimmedQuery || uploadPrompt,
      file: uploadedFile?.name,
    };

    try {
      setLoading(true);
      setError("");

      let uploadedSummary = null;
      if (uploadedFile) {
        uploadedSummary = await uploadSelectedFile(uploadedFile);
      }

      const requestData = {
        query: uploadedFile
          ? `${trimmedQuery || uploadPrompt}: ${uploadedFile.name}. Indexed ${uploadedSummary?.indexed || 0} records for the ${domain} domain.`
          : trimmedQuery,
      };

      const res = await API.post("/ask", requestData);

      const botText = uploadedSummary
        ? `Indexed ${uploadedSummary.indexed} records from ${uploadedSummary.filename}.\n\n${res.data.answer}`
        : res.data.answer;

      setMessages((currentMessages) => [
        ...currentMessages,
        userMessage,
        { type: "bot", text: botText },
      ]);

      setQuery("");
      setUploadedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (err) {
      console.error("Chat error:", err);
      setError(
        err.response?.data?.detail ||
          "Failed to get response. Please try again."
      );
      setMessages((currentMessages) => [...currentMessages, userMessage]);
      setQuery("");
      setUploadedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey && !loading) {
      event.preventDefault();
      ask();
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const fileExt = `.${file.name.split(".").pop().toLowerCase()}`;
    if (!allowedTypes.includes(fileExt)) {
      setError(`Invalid file type. Allowed: ${allowedTypes.join(", ")}`);
      event.target.value = "";
      return;
    }

    setUploadedFile(file);
    setError("");
  };

  const removeFile = () => {
    setUploadedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div
      className="chat-modal-overlay"
      onClick={onClose}
      onKeyDown={(event) => event.key === "Escape" && onClose()}
      role="presentation"
    >
      <div
        className="chat-modal"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="chat-modal-title"
      >
        <div className="chat-modal-header">
          <h3 id="chat-modal-title">{config?.title || "AI Assistant"}</h3>
          <button className="close-btn" onClick={onClose} aria-label="Close chat">
            x
          </button>
        </div>

        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h4>{config?.ui?.empty_state_title || `Welcome to ${config?.title || "AI Assistant"}!`}</h4>
              <p>{config?.ui?.empty_state_description || "Try asking:"}</p>
              <div className="sample-queries">
                {sampleQueries.map((sampleQuery) => (
                  <button
                    key={sampleQuery}
                    className="sample-query-btn"
                    onClick={() => setQuery(sampleQuery)}
                  >
                    {sampleQuery}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, index) => (
            <div key={`${msg.type}-${index}`} className={`message ${msg.type}`}>
              <div className="message-content">
                {msg.file && <div className="file-attachment">Attached file: {msg.file}</div>}
                {msg.text}
              </div>
            </div>
          ))}

          {loading && (
            <div className="message bot loading">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="chat-input-area">
          {uploadedFile && (
            <div className="file-preview">
              <span>Attached: {uploadedFile.name}</span>
              <button onClick={removeFile} aria-label="Remove attached file">
                x
              </button>
            </div>
          )}

          <div className="input-controls">
            <input
              type="text"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={config?.ui?.chat_placeholder || `Ask about ${domain}...`}
              disabled={loading}
            />

            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileSelect}
              accept={acceptValue}
              style={{ display: "none" }}
            />

            <button
              className="file-btn"
              onClick={() => fileInputRef.current?.click()}
              disabled={loading}
              title="Upload file"
              aria-label="Upload file"
            >
              Attach
            </button>

            <button
              className="send-btn"
              onClick={ask}
              disabled={loading || (!query.trim() && !uploadedFile)}
            >
              {loading ? "..." : "Send"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
