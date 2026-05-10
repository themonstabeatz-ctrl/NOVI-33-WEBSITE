/**
 * 🔒 HARD LOCK - DO NOT CHANGE
 * Backend URL: https://spa-cors-sync.preview.emergentagent.com
 * 
 * 🚫 DISCOUNT UPDATES ARE RECEPCIJA-ONLY!
 * Client frontend ONLY READS discount data from backend.
 * Client NEVER calls PATCH discount endpoints.
 */

// ✅ SINGLE SOURCE OF TRUTH
export const API_BASE = process.env.REACT_APP_API_BASE_URL || "https://spa-cors-sync.preview.emergentagent.com";

// Freeze to prevent accidental overwrite
Object.freeze?.(API_BASE);

// Debug log on import
console.log("🔐 LOCKED FRONTEND =", window.location.origin);
console.log("🔐 LOCKED API_BASE =", API_BASE);

export const API = {
  health: `${API_BASE}/api/health`,

  // SERVICES
  services: `${API_BASE}/api/services`,
  spaServices: `${API_BASE}/api/spa/services`,
  spaCards: `${API_BASE}/api/spa/cards`,
  spaQuote: `${API_BASE}/api/spa/quote`,

  // APPOINTMENTS
  appointments: `${API_BASE}/api/appointments`,
  appointmentsList: `${API_BASE}/api/appointments/list`,
  coupleAppointments: `${API_BASE}/api/appointments/couple`,
  spaAppointments: `${API_BASE}/api/spa/appointments`,

  // CEO / NOTIF
  unviewedCount: `${API_BASE}/api/appointments/unviewed/count`,
};

/**
 * 🚫 GUARD: Discount updates are RECEPCIJA-ONLY
 * This function exists to prevent ANY discount update from client UI.
 * If any code tries to call this, it will be blocked with a warning.
 */
export function updateDiscount() {
  console.warn("🚫 Discount updates are RECEPCIJA-only. Client cannot modify discounts.");
  return Promise.resolve({ ok: false, error: "FORBIDDEN" });
}

/**
 * 🚫 GUARD: Block any PATCH to discount endpoints
 * This is a safety net - client code should NEVER reach here.
 */
export function patchDiscount() {
  console.warn("🚫 PATCH /discount is BLOCKED. Use recepcija to update discounts.");
  return Promise.resolve({ ok: false, error: "FORBIDDEN" });
}
