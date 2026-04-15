import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import API from "./api";

function App() {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      localStorage.setItem("token", token);
    } else {
      localStorage.removeItem("token");
    }
  }, [token]);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const res = await API.get("/config");
        setConfig(res.data);
      } catch (err) {
        console.error("Failed to fetch config:", err);
        // Use default config if fetch fails
        setConfig({
          domain: "general",
          title: "AI Assistant",
          description: "Analyze data with AI-powered insights",
          ui: {
            chat_placeholder: "Ask about your dataset...",
            upload_prompt: "Analyze this file",
            sample_queries: ["What are the key trends in this dataset?"],
            allowed_file_types: [".csv", ".txt", ".pdf", ".md"],
            empty_state_title: "Welcome to AI Assistant!",
            empty_state_description: "Ask questions and explore the currently loaded domain data.",
            dashboard: {
              metrics: [
                { label: "Dataset Status", value: "Ready", change: "Live" },
                { label: "Mode", value: "Generic", change: "Adaptive" },
              ],
              insights: [
                {
                  title: "Config Driven",
                  description: "Swap the active domain by updating backend config and data paths.",
                },
              ],
            },
          },
        });
      } finally {
        setLoading(false);
      }
    };

    fetchConfig();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={token ? <Landing config={config} setToken={setToken} /> : <Navigate to="/login" />} />
        <Route path="/login" element={token ? <Navigate to="/" /> : <Login setToken={setToken} />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
