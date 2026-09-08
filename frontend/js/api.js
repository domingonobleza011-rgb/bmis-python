// Central API client. Set window.API_BASE before this loads if the backend
// isn't on the same origin (e.g. frontend on Netlify, backend on Render).
const API_BASE = window.API_BASE || "http://localhost:8000";

function getToken() { return localStorage.getItem("bmis_token"); }
function getSession() {
  const raw = localStorage.getItem("bmis_session");
  return raw ? JSON.parse(raw) : null;
}
function setSession(tokenResponse) {
  localStorage.setItem("bmis_token", tokenResponse.access_token);
  localStorage.setItem("bmis_session", JSON.stringify({
    role: tokenResponse.role, name: tokenResponse.name, user_id: tokenResponse.user_id,
  }));
}
function clearSession() {
  localStorage.removeItem("bmis_token");
  localStorage.removeItem("bmis_session");
}
function requireLogin(allowedRoles) {
  const session = getSession();
  if (!session || !getToken()) { window.location.href = "/index.html"; return null; }
  if (allowedRoles && !allowedRoles.includes(session.role)) {
    window.location.href = "/index.html";
    return null;
  }
  return session;
}

async function api(path, { method = "GET", body, isForm = false, auth = true } = {}) {
  const headers = {};
  if (!isForm) headers["Content-Type"] = "application/json";
  if (auth && getToken()) headers["Authorization"] = `Bearer ${getToken()}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? (isForm ? body : JSON.stringify(body)) : undefined,
  });

  if (res.status === 401) { clearSession(); window.location.href = "/index.html"; return; }

  let data = null;
  try { data = await res.json(); } catch (_) { /* no body */ }

  if (!res.ok) {
    const message = (data && (data.detail || data.message)) || `Request failed (${res.status})`;
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }
  return data;
}

function toast(message, type = "success") {
  const el = document.createElement("div");
  el.className = `toast ${type === "error" ? "error" : ""}`;
  el.textContent = message;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3200);
}

function badge(status) {
  return `<span class="badge ${status}">${status}</span>`;
}

function fmtDate(d) {
  if (!d) return "—";
  return new Date(d).toLocaleDateString("en-PH", { year: "numeric", month: "short", day: "numeric" });
}
