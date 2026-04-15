import { useEffect, useRef, useState } from "react";
import API from "../api";
import "../styles/chat.css";

const DEFAULT_UPLOAD_PROMPT = "Analyze this file";

const ALLOWED_FILE_TYPES = {
  manufacturing: [".csv", ".xlsx"],
  retail: [".csv", ".xlsx"],
  healthcare: [".pdf", ".txt", ".docx"],
};

const SAMPLE_QUERIES = {
  manufacturing: [
    "Why are there more defects on Line A?",
    "What factors contribute to critical defects?",
    "How can we reduce surface scratches?",
  ],
  retail: [
    "Why did sales deviate from forecast in December?",
    "What caused negative deviation in North region?",
    "How do promotions affect forecast accuracy?",
  ],
  healthcare: [
    "What are the steps for patient admission?",
    "How should medications be administered?",
    "What are infection control requirements?",
  ],
};

export default function ChatModal({ config, onClose }) {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [uploadedFile, setUploadedFile] = useState(null);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const domain = config?.domain || "general";
  const allowedTypes = ALLOWED_FILE_TYPES[domain] || [".csv", ".txt", ".pdf"];
  const acceptValue = allowedTypes.join(",");
  const sampleQueries =
    SAMPLE_QUERIES[domain] || ["Ask me anything about the data..."];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  const ask = async () => {
    const trimmedQuery = query.trim();
    if (!trimmedQuery && !uploadedFile) return;

    const userMessage = {
      type: "user",
      text: trimmedQuery || DEFAULT_UPLOAD_PROMPT,
      file: uploadedFile?.name,
    };

    const requestData = {
      query: uploadedFile
        ? `${trimmedQuery || DEFAULT_UPLOAD_PROMPT}: ${uploadedFile.name}`
        : trimmedQuery,
    };

    try {
      setLoading(true);
      setError("");

      const res = await API.post("/ask", requestData);

      setMessages((currentMessages) => [
        ...currentMessages,
        userMessage,
        { type: "bot", text: res.data.answer },
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
              <h4>Welcome to {config?.title || "AI Assistant"}!</h4>
              <p>Try asking:</p>
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
              placeholder="Ask a question..."
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
