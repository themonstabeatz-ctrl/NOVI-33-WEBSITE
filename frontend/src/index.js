import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";
import { API_BASE } from "./config/api";

// ✅ RUNTIME GUARD: Verify API_BASE is correct
const EXPECTED_API_BASE = "https://spa-system-fixes.preview.emergentagent.com";

if (!API_BASE.includes("spa-system-fixes")) {
  console.warn("⚠️ API_BASE may be misconfigured. Expected spa-system-fixes but got:", API_BASE);
}

console.log("🔐 LOCKED FRONTEND =", window.location.origin);
console.log("🔐 LOCKED API_BASE =", API_BASE);

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
