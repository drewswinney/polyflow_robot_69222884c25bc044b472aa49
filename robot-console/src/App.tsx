import { useEffect, useMemo, useState } from "react";
import {
  Button,
  TextField,
  Card,
  Variant,
} from "@polyflowrobotics/ui-components";
import Logo from "./components/Logo";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faTerminal,
  faWifi,
  faBars,
  faRightFromBracket,
} from "@fortawesome/free-solid-svg-icons";

type StatusState = "idle" | "saving" | "success" | "error";

interface WifiBody {
  ssid: string;
  psk?: string;
}

interface WifiStatusResponse {
  configured: boolean;
  ssid: string | null;
  pskSet: boolean;
}

export default function App() {
  const [robotId, setRobotId] = useState("robot-001");
  const [ssid, setSsid] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState<StatusState>("idle");
  const [statusMessage, setStatusMessage] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // API is reverse-proxied by Caddy under the same origin at /api
  const apiBase = useMemo(() => `/api`, []);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch(`${apiBase}/wifi`);
        if (!res.ok) return;
        const data: WifiStatusResponse = await res.json();
        if (data.configured) {
          setSsid(data.ssid || "");
          setPassword(data.pskSet ? "********" : "");
        }
      } catch (err) {
        // ignore initial load errors
        console.error(err);
      }
    };
    fetchStatus();
  }, [apiBase]);

  const handleSave = async () => {
    if (!ssid) {
      setStatus("error");
      setStatusMessage("SSID is required");
      return;
    }
    setStatus("saving");
    setStatusMessage("");
    try {
      const body: WifiBody = { ssid, psk: password || undefined };
      const res = await fetch(`${apiBase}/wifi`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const msg = await res.text();
        throw new Error(msg || "Failed to save");
      }
      setStatus("success");
      setStatusMessage("Saved. Switching modes...");
    } catch (err: any) {
      setStatus("error");
      setStatusMessage(err?.message || "Failed to save");
    }
  };

  return (
    <div className="app-shell theme-light">
      <main className="content">
        {sidebarOpen && (
          <div
            className="sidebar-overlay"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close sidebar overlay"
          />
        )}
        <aside className={`sidebar ${sidebarOpen ? "is-open" : ""}`}>
          <div className="branding">
            <Logo />
            <span className="title">Polyflow Robot Console</span>
          </div>
          <div className="header">Pages</div>
          <nav className="nav">
            <Button className="nav-item" variant={Variant.Transparent}>
              <FontAwesomeIcon icon={faWifi} />
              <span>Connection</span>
            </Button>
            <Button className="nav-item" variant={Variant.Transparent}>
              <FontAwesomeIcon icon={faTerminal} />
              <span>Logs</span>
            </Button>
          </nav>
        </aside>
        <Card className="page">
          <div className="page-header">
            <Button
              className="sidebar-toggle"
              variant={Variant.Transparent}
              onClick={() => setSidebarOpen(true)}
              aria-label="Open navigation"
            >
              <FontAwesomeIcon icon={faRightFromBracket} />
            </Button>
            <div className="title">
              <h5>Connection Settings</h5>
              <span>Connect to Wifi and Bluetooth devices</span>
            </div>
          </div>
          <div className="section">
            <div className="section-header">
              <div className="actions"></div>
            </div>
            <div className="form">
              <div className="group">
                <div className="group-header">Wifi Settings</div>
                <TextField
                  label="SSID"
                  value={ssid}
                  onChange={(value) => setSsid(value)}
                />
                <TextField
                  label="Password"
                  type="password"
                  value={password}
                  onChange={(value) => setPassword(value)}
                />
              </div>
              <div className="group">
                <div className="group-header">Bluetooth Settings</div>
                <Card className="coming-soon">Coming Soon</Card>
              </div>
            </div>
          </div>
          <div className="footer">
            <div className="status-message">
              {statusMessage && (
                <Card
                  variant={status === "error" ? Variant.Error : Variant.Success}
                >
                  {statusMessage}
                </Card>
              )}
            </div>
            <Button
              variant={Variant.Primary}
              onClick={handleSave}
              disabled={status === "saving"}
            >
              {status === "saving" ? "Saving..." : "Save configuration"}
            </Button>
          </div>
        </Card>
      </main>
    </div>
  );
}
