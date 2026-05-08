import React, { useState, useEffect, useCallback } from "react";
import { API_BASE } from "../config/api";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Calendar, Clock, User, Phone, Sparkles, Leaf, Pencil, X } from "lucide-react";

/**
 * ✅ Termini (Appointments) Screen
 * Displays calendar events including SPA bookings from backend
 * LOCKED TO: https://spa-system-fixes.preview.emergentagent.com
 */

// Format date helper
const formatDate = (dateStr) => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return date.toLocaleDateString("sr-RS", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric"
  });
};

// Format time helper
const formatTime = (dateStr) => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return date.toLocaleTimeString("sr-RS", {
    hour: "2-digit",
    minute: "2-digit"
  });
};

// Format price helper
const formatPrice = (price) => {
  const num = Number(price || 0);
  return num.toLocaleString("sr-RS") + " RSD";
};

// Get badge based on event type
const getBadge = (event) => {
  // Check for SPA
  if (event.type === "spa" || event.spa_category || event.category?.toLowerCase().includes("spa")) {
    return { label: "SPA", color: "#d4af37", bg: "rgba(212, 175, 55, 0.2)" };
  }
  // Check for couples massage
  if (event.is_couples_booking || event.type === "couple" || event.category?.toLowerCase().includes("couple")) {
    return { label: "PAROVI", color: "#e91e63", bg: "rgba(233, 30, 99, 0.2)" };
  }
  return { label: "MASAŽA", color: "#4ade80", bg: "rgba(74, 222, 128, 0.2)" };
};

// ✅ A) FINAL HELPER FUNKCIJE
// Backend polja su izvor istine; notes parsing je samo fallback
const s = (v) => (typeof v === "string" ? v.trim() : v);

// Get event type
function getType(row) {
  // ✅ FIX: Properly detect SPA appointments
  if (row.type === "spa" || row.spa_category || row.category?.toLowerCase?.()?.includes("spa")) {
    return "spa";
  }
  if (row.is_couples_booking || row.type === "couple" || row.category?.toLowerCase?.()?.includes("couple")) {
    return "couple";
  }
  return row.type || row.appointment_type || row.source || "massage";
}

// ✅ Parse notes - SAMO kao fallback dok backend ne isporuči polja
function parseNotesSpa(notes = "") {
  const out = { title: "", variant: "", totalMin: null, spaZone: "" };
  if (!notes) return out;

  // Parse title: Multiple formats supported
  // Format 1: "SPA paket: Silky Body Ritual"
  // Format 2: "Paket: Romantični paket za parove"
  // Format 3: "🌹 Romantični SPA paket za parove" (first line)
  const mTitle1 = notes.match(/SPA paket:\s*([^\n]+?)(?:\s+Varijanta:|\s+SPA zona:|\s+Ukupno trajanje:|\s+Ukupna cena:|$)/);
  const mTitle2 = notes.match(/^Paket:\s*([^\n]+)/m);
  const mTitle3 = notes.match(/^[🌹🧖‍♀️💆‍♂️✨🌿🍃💎]?\s*(.+?SPA.+?)$/m);
  
  if (mTitle1) {
    out.title = mTitle1[1].trim();
  } else if (mTitle2) {
    out.title = mTitle2[1].trim();
  } else if (mTitle3) {
    out.title = mTitle3[1].trim();
  }

  // Parse variant: "Varijanta: Sa masažom lica (+3.000 RSD)"
  const mVar = notes.match(/Varijanta:\s*([^\n]+?)(?:\s+SPA zona:|\s+Ukupno trajanje:|\s+Ukupna cena:|$)/);
  if (mVar) out.variant = mVar[1].trim();

  // Parse duration: "Ukupno trajanje: 270 min"
  const mDur = notes.match(/Ukupno trajanje:\s*(\d+)\s*min/);
  if (mDur) out.totalMin = Number(mDur[1]);

  // Parse SPA zone (inline or multiline)
  const mZoneInline = notes.match(/SPA zona:\s*([^\n]+)/);
  if (mZoneInline) {
    out.spaZone = mZoneInline[1].trim();
  } else {
    // Try multiline format
    const mZoneMulti = notes.match(/SPA zona:\s*\n((?:\s+[•\-]\s*[^\n]+\n?)+)/);
    if (mZoneMulti) {
      out.spaZone = mZoneMulti[1]
        .split('\n')
        .map(line => line.replace(/^\s+[•\-]\s*/, '').trim())
        .filter(Boolean)
        .join(', ');
    }
  }

  return out;
}

// ✅ Get title - BACKEND FIRST, notes kao fallback
function getTitle(row) {
  const type = getType(row);
  
  // Non-SPA: backend fields only (MASAŽE I PAROVI - NE DIRATI)
  if (type !== "spa") {
    // Couples massage
    if (row.is_couples_booking && row.person1_services_snapshot?.length) {
      const p1 = row.person1_services_snapshot
        .map(svc => s(svc.name)?.replace('[PAROVI] ', '').replace(/ - \d+ min$/, ''))
        .filter(Boolean)
        .join(' + ');
      if (p1) return `Masaža za parove: ${p1}`;
    }
    return s(row.service_name) || s(row.service_title) || s(row.title) || "Usluga";
  }

  // SPA: notes parsed title FIRST (because backend returns generic "SPA Tretman")
  // then backend fields as fallback
  const notesParsed = parseNotesSpa(row.notes || "");
  
  // Check if backend service_name is not generic
  const backendName = s(row.service_name) || s(row.service_title) || s(row?.services_snapshot?.[0]?.name);
  const isGenericName = !backendName || backendName === "SPA Tretman" || backendName === "SPA";
  
  // Prefer notes parsed title if backend name is generic
  if (notesParsed.title && isGenericName) {
    return notesParsed.title;
  }
  
  return backendName || s(notesParsed.title) || "SPA Tretman";
}

// ✅ Get description - BACKEND FIRST
function getDesc(row) {
  const type = getType(row);
  
  // Non-SPA
  if (type !== "spa") {
    // Couples - show person2 services
    if (row.is_couples_booking && row.person2_services_snapshot?.length) {
      const p2 = row.person2_services_snapshot
        .map(svc => s(svc.name)?.replace('[PAROVI] ', '').replace(/ - \d+ min$/, ''))
        .filter(Boolean)
        .join(' + ');
      if (p2) return `Osoba 2: ${p2}`;
    }
    return s(row.service_description) || s(row.service_desc) || "";
  }

  // SPA: backend first, then notes fallback
  const notesParsed = parseNotesSpa(row.notes || "");
  return (
    s(row.service_description) ||
    s(row.service_desc) ||
    s(row?.services_snapshot?.[0]?.description) ||
    s(notesParsed.variant) ||
    ""
  );
}

// ✅ Get duration - BACKEND FIRST, nikad N/A
function getDurationMin(row) {
  const type = getType(row);

  // Backend first
  const raw = row.duration_min ?? row.duration ?? row?.services_snapshot?.[0]?.duration;
  if (Number.isFinite(Number(raw)) && Number(raw) > 0) return Number(raw);

  // Couples - person1 snapshot
  if (row.is_couples_booking && row.person1_services_snapshot?.[0]?.duration) {
    const dur = Number(row.person1_services_snapshot[0].duration);
    if (Number.isFinite(dur) && dur > 0) return dur;
  }

  // SPA: notes fallback
  if (type === "spa") {
    const notesParsed = parseNotesSpa(row.notes || "");
    if (Number.isFinite(Number(notesParsed.totalMin)) && notesParsed.totalMin > 0) {
      return Number(notesParsed.totalMin);
    }
  }

  // Compute from start/end
  if (row.start_time && row.end_time) {
    const diff = Math.round((new Date(row.end_time) - new Date(row.start_time)) / 60000);
    if (Number.isFinite(diff) && diff > 0) return diff;
  }

  return 120; // never N/A
}

// ✅ Get SPA zone - BACKEND FIRST
function getSpaZone(row) {
  const notesParsed = parseNotesSpa(row.notes || "");
  return s(row.spa_zone) || s(notesParsed.spaZone) || "";
}

// ✅ Get add-ons
function getAddonsText(row) {
  const addons = row.addons || row.spa_addons || [];
  if (!addons.length) return "";
  return "Doplate: " + addons.map(a => a.name || a).join(", ");
}

/**
 * ✅ Fetch calendar events from backend
 * Uses direct XMLHttpRequest to avoid rrweb-recorder clone() issue
 */
const fetchCalendarEvents = async () => {
  console.log("📅 Fetching all events from price-consistency...");
  
  // ✅ FIX: Use XMLHttpRequest to bypass rrweb-recorder interceptor
  const fetchWithXHR = (url) => new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.setRequestHeader("Accept", "application/json");
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(JSON.parse(xhr.responseText));
        } catch (e) {
          resolve([]);
        }
      } else {
        reject(new Error(`HTTP ${xhr.status}`));
      }
    };
    xhr.onerror = () => reject(new Error("Network error"));
    xhr.send();
  });
  
  try {
    // Fetch both massage and SPA appointments in parallel
    const [massageData, spaData] = await Promise.all([
      fetchWithXHR(`${API_BASE}/api/appointments?limit=100`).catch(() => []),
      fetchWithXHR(`${API_BASE}/api/spa/appointments`).catch(() => [])
    ]);
    
    // Mark SPA appointments with type
    const spaWithType = (Array.isArray(spaData) ? spaData : []).map(e => ({ ...e, type: "spa" }));
    
    // Combine and sort by start_time
    const combined = [...(Array.isArray(massageData) ? massageData : []), ...spaWithType];
    combined.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
    
    console.log(`📅 Loaded ${combined.length} events (${massageData?.length || 0} massage + ${spaData?.length || 0} SPA)`);
    
    // 🔍 DEBUG: Log sample SPA row (privremeno, brišemo posle)
    const sampleSpa = combined.find(r => getType(r) === "spa");
    if (sampleSpa) {
      console.log("🔍 TERMINI SPA ROW SAMPLE:", sampleSpa);
      console.log("🔍 PARSED:", {
        title: getTitle(sampleSpa),
        desc: getDesc(sampleSpa),
        duration: getDurationMin(sampleSpa),
        spaZone: getSpaZone(sampleSpa)
      });
    }
    
    return combined;
  } catch (err) {
    console.error("❌ Failed to fetch events:", err);
    throw err;
  }
};

const Termini = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [viewMode, setViewMode] = useState("week"); // "day", "week", "month"
  const [currentDate, setCurrentDate] = useState(new Date());
  
  // ✅ NEW: Edit mode state
  const [isEditing, setIsEditing] = useState(false);
  const [editFormData, setEditFormData] = useState({
    status: "scheduled", // scheduled, completed, cancelled
    service_id: null,    // ✅ NEW: For SPA service selection
    service_name: ""     // ✅ NEW: Display name
  });
  
  // ✅ NEW: SPA services list for dropdown
  const [spaServices, setSpaServices] = useState([]);
  const [savingEdit, setSavingEdit] = useState(false);
  
  // ✅ Load SPA services on mount
  useEffect(() => {
    const loadSpaServices = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/spa/services`);
        if (response.ok) {
          const data = await response.json();
          console.log("📦 Loaded SPA services:", data.length);
          setSpaServices(data);
        }
      } catch (err) {
        console.error("❌ Failed to load SPA services:", err);
      }
    };
    loadSpaServices();
  }, []);

  // Calculate date range based on view mode
  const getDateRange = useCallback(() => {
    const start = new Date(currentDate);
    const end = new Date(currentDate);
    
    if (viewMode === "day") {
      start.setHours(0, 0, 0, 0);
      end.setHours(23, 59, 59, 999);
    } else if (viewMode === "week") {
      const dayOfWeek = start.getDay();
      const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek; // Start from Monday
      start.setDate(start.getDate() + diff);
      start.setHours(0, 0, 0, 0);
      end.setDate(start.getDate() + 6);
      end.setHours(23, 59, 59, 999);
    } else if (viewMode === "month") {
      start.setDate(1);
      start.setHours(0, 0, 0, 0);
      end.setMonth(end.getMonth() + 1);
      end.setDate(0);
      end.setHours(23, 59, 59, 999);
    }
    
    return {
      startISO: start.toISOString(),
      endISO: end.toISOString()
    };
  }, [currentDate, viewMode]);

  // Load events
  const loadEvents = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // ✅ FIX: Fetch all events, then filter client-side by date range
      const allEvents = await fetchCalendarEvents();
      const { startISO, endISO } = getDateRange();
      const startDate = new Date(startISO);
      const endDate = new Date(endISO);
      
      // Filter events within the selected date range
      const filteredEvents = allEvents.filter(event => {
        const eventDate = new Date(event.start_time);
        return eventDate >= startDate && eventDate <= endDate;
      });
      
      console.log(`📅 Filtered ${filteredEvents.length}/${allEvents.length} events for date range`);
      setEvents(filteredEvents);
    } catch (err) {
      console.error("❌ Failed to load events:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [getDateRange]);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  // Navigation
  const goToPrevious = () => {
    const newDate = new Date(currentDate);
    if (viewMode === "day") newDate.setDate(newDate.getDate() - 1);
    else if (viewMode === "week") newDate.setDate(newDate.getDate() - 7);
    else newDate.setMonth(newDate.getMonth() - 1);
    setCurrentDate(newDate);
  };

  const goToNext = () => {
    const newDate = new Date(currentDate);
    if (viewMode === "day") newDate.setDate(newDate.getDate() + 1);
    else if (viewMode === "week") newDate.setDate(newDate.getDate() + 7);
    else newDate.setMonth(newDate.getMonth() + 1);
    setCurrentDate(newDate);
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  // Render event card
  const renderEventCard = (event) => {
    const badge = getBadge(event);
    // ✅ B) UI prikaz - BACKEND FIRST helper funkcije
    const type = getType(event);
    const title = getTitle(event);
    const desc = getDesc(event);
    const dur = getDurationMin(event);
    const zone = type === "spa" ? getSpaZone(event) : "";
    const addonsText = getAddonsText(event);
    
    const startTime = formatTime(event.start_time);
    const endTime = formatTime(event.end_time);
    const clientName = event.client 
      ? `${event.client.first_name || ""} ${event.client.last_name || ""}`.trim()
      : event.client_first_name 
        ? `${event.client_first_name} ${event.client_last_name || ""}`.trim()
        : "Nepoznat klijent";
    // ✅ Get price from backend fields
    const price = event.final_total 
      || event.snapshot_price 
      || event.pricing?.final_total 
      || event.final_price 
      || event.services_snapshot?.[0]?.price
      || event.price 
      || 0;

    return (
      <Card 
        key={event.id} 
        className="event-card"
        onClick={() => setSelectedEvent(event)}
        style={{
          cursor: "pointer",
          background: "rgba(26, 26, 26, 0.8)",
          border: `1px solid ${badge.color}40`,
          marginBottom: "0.75rem",
          transition: "all 0.3s ease"
        }}
      >
        <CardContent style={{ padding: "1rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div style={{ flex: 1 }}>
              {/* Badges: type + duration */}
              <div className="badges" style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.5rem" }}>
                {type === "spa" && (
                  <span className="badge-spa" style={{
                    display: "inline-block",
                    padding: "0.2rem 0.5rem",
                    borderRadius: "4px",
                    fontSize: "0.7rem",
                    fontWeight: "bold",
                    background: badge.bg,
                    color: badge.color
                  }}>
                    {badge.label}
                  </span>
                )}
                {type !== "spa" && (
                  <span style={{
                    display: "inline-block",
                    padding: "0.2rem 0.5rem",
                    borderRadius: "4px",
                    fontSize: "0.7rem",
                    fontWeight: "bold",
                    background: badge.bg,
                    color: badge.color
                  }}>
                    {badge.label}
                  </span>
                )}
                
                {/* Duration - uvek broj, nikad N/A */}
                <span className="badge-dur" style={{ 
                  color: "#888", 
                  fontSize: "0.75rem"
                }}>
                  ⏱ {dur} min
                </span>
              </div>
              
              {/* Title */}
              <div className="service-title" style={{ color: "#f5f2e8", fontSize: "1rem", margin: "0.25rem 0", fontWeight: "600" }}>
                {title}
              </div>
              
              {/* Description (italic) */}
              {desc && (
                <div className="service-desc" style={{ color: "#a0a0a0", fontSize: "0.8rem", marginBottom: "0.25rem" }}>
                  <em>{desc}</em>
                </div>
              )}
              
              {/* SPA Zone */}
              {zone && (
                <div className="spa-zone" style={{ color: "#d4af37", fontSize: "0.75rem", marginBottom: "0.25rem" }}>
                  🧖 {zone}
                </div>
              )}
              
              {/* Add-ons (if exists) */}
              {addonsText && (
                <div style={{ color: "#4ade80", fontSize: "0.75rem", marginBottom: "0.25rem" }}>
                  {addonsText}
                </div>
              )}
              
              {/* Client */}
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", color: "#c0baa8", fontSize: "0.85rem", marginTop: "0.5rem" }}>
                <User size={14} />
                <span>{clientName}</span>
              </div>
              
              {/* Time */}
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", color: "#c0baa8", fontSize: "0.85rem", marginTop: "0.25rem" }}>
                <Clock size={14} />
                <span>{startTime} - {endTime}</span>
              </div>
            </div>
            
            {/* Price - with discount display if applicable */}
            <div style={{ 
              textAlign: "right",
              minWidth: "120px"
            }}>
              {event.pricing?.has_discount ? (
                <>
                  <div style={{ 
                    color: "#888", 
                    fontSize: "0.75rem",
                    textDecoration: "line-through"
                  }}>
                    {formatPrice(event.pricing.original_total)}
                  </div>
                  <div style={{ 
                    color: "#4ade80", 
                    fontSize: "0.7rem",
                    fontWeight: "600"
                  }}>
                    -{event.pricing.discount_percent}%
                  </div>
                  <div style={{ 
                    color: "#d4af37", 
                    fontWeight: "bold",
                    fontSize: "1rem"
                  }}>
                    {formatPrice(event.pricing.final_total)}
                  </div>
                </>
              ) : (
                <div style={{ 
                  color: "#d4af37", 
                  fontWeight: "bold",
                  fontSize: "1rem"
                }}>
                  {formatPrice(price)}
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  // Render selected event details modal
  const renderEventModal = () => {
    if (!selectedEvent) return null;
    
    const badge = getBadge(selectedEvent);
    const title = getTitle(selectedEvent);
    const duration = getDurationMin(selectedEvent);
    const clientName = selectedEvent.client 
      ? `${selectedEvent.client.first_name || ""} ${selectedEvent.client.last_name || ""}`.trim()
      : selectedEvent.client_first_name 
        ? `${selectedEvent.client_first_name} ${selectedEvent.client_last_name || ""}`.trim()
        : "Nepoznat klijent";
    const phone = selectedEvent.client?.phone || selectedEvent.client_phone || "";
    const email = selectedEvent.client?.email || selectedEvent.client_email || "";
    const price = selectedEvent.pricing?.final_total || selectedEvent.final_price || selectedEvent.price || 0;
    const notes = selectedEvent.notes || "";
    
    // ✅ Build service display label: "Naziv usluge - XX min"
    const serviceDisplayLabel = duration > 0 ? `${title} - ${duration} min` : title;
    
    // ✅ Get current status from event
    const currentStatus = selectedEvent.status || "scheduled";

    // ✅ Handle opening edit mode
    const handleEditClick = () => {
      const type = getType(selectedEvent);
      const isSpa = type === "spa";
      
      // ✅ Extract service_id for SPA appointments
      let serviceId = null;
      let serviceName = title;
      
      if (isSpa) {
        // SPA: Try to get service_id from various fields
        serviceId = selectedEvent.service_id 
          || selectedEvent.card_id 
          || (selectedEvent.services_snapshot?.[0]?.id)
          || (selectedEvent.service_ids?.[0])
          || null;
        
        serviceName = selectedEvent.service_name 
          || selectedEvent.card_title 
          || selectedEvent.services_snapshot?.[0]?.name
          || title;
          
        console.log("📝 Opening SPA edit:", { serviceId, serviceName, type });
      }
      
      setEditFormData({ 
        status: currentStatus,
        service_id: serviceId,
        service_name: serviceName
      });
      setIsEditing(true);
    };

    // ✅ Handle closing edit mode
    const handleCancelEdit = () => {
      setIsEditing(false);
    };

    // ✅ Print appointment helper - works for SPA and MASAŽE
    const printAppointment = (appointmentData) => {
      const type = getType(appointmentData);
      const serviceName = appointmentData.service_name 
        || appointmentData.card_title 
        || appointmentData.services_snapshot?.[0]?.name
        || getTitle(appointmentData);
      const durationMin = getDurationMin(appointmentData);
      const clientName = appointmentData.client 
        ? `${appointmentData.client.first_name || ""} ${appointmentData.client.last_name || ""}`.trim()
        : `${appointmentData.client_first_name || ""} ${appointmentData.client_last_name || ""}`.trim();
      const phone = appointmentData.client?.phone || appointmentData.client_phone || "";
      const email = appointmentData.client?.email || appointmentData.client_email || "";
      const startTime = appointmentData.start_time ? new Date(appointmentData.start_time) : new Date();
      const pricing = appointmentData.pricing || {};
      
      // Build print content
      const printContent = `
<!DOCTYPE html>
<html>
<head>
  <title>Termin - ${serviceName}</title>
  <style>
    body { font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; max-width: 400px; margin: 0 auto; }
    .header { text-align: center; border-bottom: 2px solid #d4af37; padding-bottom: 15px; margin-bottom: 20px; }
    .logo { font-size: 24px; font-weight: bold; color: #d4af37; }
    .subtitle { color: #666; font-size: 12px; }
    .badge { display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; margin: 10px 0; }
    .badge-spa { background: rgba(212, 175, 55, 0.2); color: #d4af37; }
    .badge-massage { background: rgba(74, 222, 128, 0.2); color: #4ade80; }
    .section { margin: 15px 0; }
    .label { color: #888; font-size: 12px; margin-bottom: 4px; }
    .value { font-size: 16px; font-weight: 500; }
    .price-block { background: #f5f5f5; padding: 15px; border-radius: 8px; margin-top: 20px; }
    .price-row { display: flex; justify-content: space-between; margin: 5px 0; }
    .price-final { font-size: 20px; font-weight: bold; color: #d4af37; }
    .strikethrough { text-decoration: line-through; color: #999; }
    .discount { color: #4ade80; font-weight: bold; }
    .footer { text-align: center; margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; font-size: 11px; color: #888; }
    @media print { body { padding: 10px; } }
  </style>
</head>
<body>
  <div class="header">
    <div class="logo">🌸 Bua Luang Thai Spa</div>
    <div class="subtitle">Potvrda termina</div>
  </div>
  
  <div style="text-align: center;">
    <span class="badge ${type === 'spa' ? 'badge-spa' : 'badge-massage'}">
      ${type === 'spa' ? 'SPA' : 'MASAŽA'}
    </span>
  </div>
  
  <div class="section">
    <div class="label">Usluga</div>
    <div class="value">${serviceName}</div>
  </div>
  
  <div class="section">
    <div class="label">Trajanje</div>
    <div class="value">${durationMin} min</div>
  </div>
  
  <div class="section">
    <div class="label">Datum i vreme</div>
    <div class="value">${startTime.toLocaleDateString('sr-RS')} u ${startTime.toLocaleTimeString('sr-RS', { hour: '2-digit', minute: '2-digit' })}</div>
  </div>
  
  <div class="section">
    <div class="label">Klijent</div>
    <div class="value">${clientName || 'N/A'}</div>
  </div>
  
  ${phone ? `
  <div class="section">
    <div class="label">Telefon</div>
    <div class="value">${phone}</div>
  </div>
  ` : ''}
  
  ${email ? `
  <div class="section">
    <div class="label">Email</div>
    <div class="value">${email}</div>
  </div>
  ` : ''}
  
  <div class="price-block">
    ${pricing.has_discount ? `
    <div class="price-row">
      <span>Originalna cena:</span>
      <span class="strikethrough">${Number(pricing.original_total || 0).toLocaleString('sr-RS')} RSD</span>
    </div>
    <div class="price-row">
      <span>Popust:</span>
      <span class="discount">-${pricing.discount_percent || 0}%</span>
    </div>
    ` : ''}
    <div class="price-row">
      <span>${pricing.has_discount ? 'Za naplatu:' : 'Cena:'}</span>
      <span class="price-final">${Number(pricing.final_total || pricing.original_total || appointmentData.price || 0).toLocaleString('sr-RS')} RSD</span>
    </div>
  </div>
  
  <div class="footer">
    <div>Hvala vam na poverenju!</div>
    <div style="margin-top: 5px;">Bua Luang Thai Spa • Beograd</div>
  </div>
</body>
</html>
      `;
      
      // Open print window
      const printWindow = window.open('', '_blank', 'width=450,height=600');
      if (printWindow) {
        printWindow.document.write(printContent);
        printWindow.document.close();
        printWindow.focus();
        setTimeout(() => {
          printWindow.print();
        }, 500);
      } else {
        alert("Molimo omogućite pop-up prozore za štampanje.");
      }
    };

    // ✅ Handle save - sends data to backend
    const handleSaveEdit = async () => {
      const type = getType(selectedEvent);
      const isSpa = type === "spa";
      const appointmentId = selectedEvent.id;
      
      if (!appointmentId) {
        console.error("❌ No appointment ID found");
        alert("Greška: Nema ID termina");
        return;
      }
      
      setSavingEdit(true);
      
      try {
        // Build update payload - PUT requires full object
        const payload = {
          client_first_name: selectedEvent.client_first_name || selectedEvent.client?.first_name || "",
          client_last_name: selectedEvent.client_last_name || selectedEvent.client?.last_name || "",
          client_phone: selectedEvent.client_phone || selectedEvent.client?.phone || "",
          client_email: selectedEvent.client_email || selectedEvent.client?.email || "",
          service_id: editFormData.service_id || selectedEvent.service_id || selectedEvent.card_id,
          start_time: selectedEvent.start_time,
          status: editFormData.status,
          notes: selectedEvent.notes || ""
        };
        
        // ✅ For SPA, update service_name if changed
        if (isSpa && editFormData.service_id) {
          const selectedSvc = spaServices.find(s => s.id === editFormData.service_id);
          if (selectedSvc) {
            payload.service_name = selectedSvc.name;
          }
        }
        
        console.log("📝 Saving edit (PUT):", { appointmentId, payload, isSpa });
        
        // Use PUT method (backend requires full object)
        const endpoint = `${API_BASE}/api/appointments/${appointmentId}`;
        
        const response = await fetch(endpoint, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        
        const updatedAppointment = await response.json();
        console.log("✅ Appointment updated:", updatedAppointment);
        
        // Update local events list
        setEvents(prev => prev.map(evt => 
          evt.id === appointmentId ? { ...evt, ...updatedAppointment } : evt
        ));
        
        // Update selected event with merged data
        const mergedAppointment = { ...selectedEvent, ...updatedAppointment };
        setSelectedEvent(mergedAppointment);
        
        setIsEditing(false);
        
        // ✅ PRINT_TRIGGERED_AFTER_SAVE - works for both SPA and MASAŽE
        const appointmentType = getType(mergedAppointment);
        console.log("🖨️ PRINT_TRIGGERED_AFTER_SAVE", { type: appointmentType, id: appointmentId });
        printAppointment(mergedAppointment);
        
      } catch (err) {
        console.error("❌ Failed to save:", err);
        alert(`Greška pri čuvanju: ${err.message}`);
      } finally {
        setSavingEdit(false);
      }
    };

    // ✅ Close modal entirely
    const handleCloseModal = () => {
      setSelectedEvent(null);
      setIsEditing(false);
    };

    return (
      <div 
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: "rgba(0,0,0,0.8)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000
        }}
        onClick={handleCloseModal}
      >
        <Card 
          style={{
            maxWidth: "500px",
            width: "90%",
            background: "#1a1a1a",
            border: `2px solid ${badge.color}`
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <CardHeader>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{
                padding: "0.3rem 0.75rem",
                borderRadius: "4px",
                fontSize: "0.8rem",
                fontWeight: "bold",
                background: badge.bg,
                color: badge.color
              }}>
                {badge.label}
              </span>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                {/* ✅ Edit button (pencil icon) */}
                {!isEditing && (
                  <button 
                    onClick={handleEditClick}
                    title="Uredi termin"
                    style={{
                      background: "rgba(212, 175, 55, 0.2)",
                      border: "1px solid #d4af37",
                      borderRadius: "6px",
                      color: "#d4af37",
                      padding: "0.4rem",
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center"
                    }}
                  >
                    <Pencil size={16} />
                  </button>
                )}
                {/* Close button */}
                <button 
                  onClick={handleCloseModal}
                  style={{
                    background: "transparent",
                    border: "none",
                    color: "#888",
                    fontSize: "1.5rem",
                    cursor: "pointer"
                  }}
                >
                  ×
                </button>
              </div>
            </div>
            <CardTitle style={{ color: "#d4af37", marginTop: "0.5rem" }}>
              {isEditing ? "Uredi termin" : title}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isEditing ? (
              /* ✅ EDIT MODE */
              <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                {/* Usluga field - DROPDOWN for SPA, read-only for massage */}
                <div>
                  <label style={{ 
                    display: "block", 
                    color: "#d4af37", 
                    fontSize: "0.85rem", 
                    marginBottom: "0.5rem",
                    fontWeight: "600"
                  }}>
                    Usluga
                  </label>
                  {getType(selectedEvent) === "spa" ? (
                    /* ✅ SPA: Editable dropdown - ACTIVE STYLING (not gray!) */
                    <select
                      value={editFormData.service_id || ""}
                      onChange={(e) => {
                        const newServiceId = e.target.value;
                        const selectedSvc = spaServices.find(s => s.id === newServiceId);
                        setEditFormData(prev => ({
                          ...prev,
                          service_id: newServiceId,
                          service_name: selectedSvc?.name || prev.service_name
                        }));
                      }}
                      style={{
                        width: "100%",
                        padding: "0.75rem",
                        background: "#1a1a1a",
                        border: "2px solid #d4af37",
                        borderRadius: "8px",
                        color: "#d4af37",
                        fontSize: "0.95rem",
                        fontWeight: "600",
                        cursor: "pointer",
                        outline: "none",
                        opacity: 1,
                        boxShadow: "0 0 8px rgba(212, 175, 55, 0.3)"
                      }}
                    >
                      <option value="" style={{ background: "#1a1a1a", color: "#888" }}>-- Izaberite uslugu --</option>
                      {spaServices.map(svc => (
                        <option key={svc.id} value={svc.id} style={{ background: "#1a1a1a", color: "#f5f2e8" }}>
                          {svc.name} {svc.price ? `(${Number(svc.price).toLocaleString('sr-RS')} RSD)` : ''}
                        </option>
                      ))}
                    </select>
                  ) : (
                    /* ✅ MASAŽE/PAROVI: Read-only (NE DIRATI) */
                    <div style={{
                      padding: "0.75rem",
                      background: "rgba(255,255,255,0.05)",
                      border: "1px solid rgba(212, 175, 55, 0.3)",
                      borderRadius: "8px",
                      color: "#f5f2e8",
                      fontSize: "0.95rem"
                    }}>
                      {serviceDisplayLabel}
                    </div>
                  )}
                </div>

                {/* Klijent field - read-only */}
                <div>
                  <label style={{ 
                    display: "block", 
                    color: "#d4af37", 
                    fontSize: "0.85rem", 
                    marginBottom: "0.5rem",
                    fontWeight: "600"
                  }}>
                    Klijent
                  </label>
                  <div style={{
                    padding: "0.75rem",
                    background: "rgba(255,255,255,0.05)",
                    border: "1px solid rgba(212, 175, 55, 0.3)",
                    borderRadius: "8px",
                    color: "#f5f2e8",
                    fontSize: "0.95rem"
                  }}>
                    {clientName}
                  </div>
                </div>

                {/* Datum i vreme - read-only */}
                <div>
                  <label style={{ 
                    display: "block", 
                    color: "#d4af37", 
                    fontSize: "0.85rem", 
                    marginBottom: "0.5rem",
                    fontWeight: "600"
                  }}>
                    Datum i vreme
                  </label>
                  <div style={{
                    padding: "0.75rem",
                    background: "rgba(255,255,255,0.05)",
                    border: "1px solid rgba(212, 175, 55, 0.3)",
                    borderRadius: "8px",
                    color: "#f5f2e8",
                    fontSize: "0.95rem"
                  }}>
                    {formatDate(selectedEvent.start_time)} {formatTime(selectedEvent.start_time)} - {formatTime(selectedEvent.end_time)}
                  </div>
                </div>

                {/* ✅ Status field - FULL WIDTH to prevent cut-off */}
                <div style={{ width: "100%" }}>
                  <label style={{ 
                    display: "block", 
                    color: "#d4af37", 
                    fontSize: "0.85rem", 
                    marginBottom: "0.5rem",
                    fontWeight: "600"
                  }}>
                    Status
                  </label>
                  <select
                    value={editFormData.status}
                    onChange={(e) => setEditFormData({ ...editFormData, status: e.target.value })}
                    style={{
                      width: "100%",
                      padding: "0.75rem",
                      background: "#2a2a2a",
                      border: "1px solid #d4af37",
                      borderRadius: "8px",
                      color: "#f5f2e8",
                      fontSize: "0.95rem",
                      cursor: "pointer",
                      outline: "none"
                    }}
                  >
                    <option value="scheduled">Zakazan</option>
                    <option value="confirmed">Potvrđen</option>
                    <option value="completed">Završen</option>
                    <option value="cancelled">Otkazan</option>
                  </select>
                </div>

                {/* Action buttons */}
                <div style={{ 
                  display: "flex", 
                  gap: "0.75rem", 
                  marginTop: "0.5rem",
                  flexWrap: "wrap"
                }}>
                  <Button
                    onClick={handleSaveEdit}
                    disabled={savingEdit}
                    style={{
                      flex: 1,
                      minWidth: "120px",
                      background: savingEdit ? "#666" : "#d4af37",
                      color: "#1a1a1a",
                      border: "none",
                      fontWeight: "bold",
                      cursor: savingEdit ? "wait" : "pointer"
                    }}
                  >
                    {savingEdit ? "Čuvanje..." : "Sačuvaj"}
                  </Button>
                  <Button
                    onClick={handleCancelEdit}
                    disabled={savingEdit}
                    variant="outline"
                    style={{
                      flex: 1,
                      minWidth: "120px",
                      background: "transparent",
                      color: "#888",
                      border: "1px solid #555"
                    }}
                  >
                    Otkaži
                  </Button>
                </div>
              </div>
            ) : (
              /* ✅ VIEW MODE */
              <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                {/* ✅ Service/Usluga with duration */}
                <div style={{ 
                  display: "flex", 
                  alignItems: "center", 
                  gap: "0.75rem",
                  padding: "0.75rem",
                  background: "rgba(212, 175, 55, 0.05)",
                  borderRadius: "8px",
                  border: "1px solid rgba(212, 175, 55, 0.2)"
                }}>
                  <Sparkles size={18} style={{ color: "#d4af37" }} />
                  <div>
                    <div style={{ color: "#888", fontSize: "0.75rem" }}>Usluga</div>
                    <div style={{ color: "#f5f2e8", fontWeight: "600" }}>{serviceDisplayLabel}</div>
                  </div>
                </div>

                {/* Client */}
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", color: "#f5f2e8" }}>
                  <User size={18} style={{ color: "#d4af37" }} />
                  <span>{clientName}</span>
                </div>
                
                {/* Phone */}
                {phone && (
                  <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", color: "#c0baa8" }}>
                    <Phone size={18} style={{ color: "#d4af37" }} />
                    <span>{phone}</span>
                  </div>
                )}
                
                {/* Time */}
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", color: "#c0baa8" }}>
                  <Clock size={18} style={{ color: "#d4af37" }} />
                  <span>
                    {formatDate(selectedEvent.start_time)} {formatTime(selectedEvent.start_time)} - {formatTime(selectedEvent.end_time)}
                  </span>
                </div>
                
                {/* Price */}
                <div style={{ 
                  display: "flex", 
                  alignItems: "center", 
                  gap: "0.75rem",
                  padding: "0.75rem",
                  background: "rgba(212, 175, 55, 0.1)",
                  borderRadius: "8px"
                }}>
                  <span style={{ color: "#c0baa8" }}>Cena:</span>
                  <span style={{ color: "#d4af37", fontWeight: "bold", fontSize: "1.2rem" }}>
                    {formatPrice(price)}
                  </span>
                </div>
                
                {/* Pricing block with discount (if applicable) */}
                {selectedEvent.pricing?.has_discount && (
                  <div style={{ 
                    padding: "0.75rem",
                    background: "rgba(74, 222, 128, 0.1)",
                    borderRadius: "8px",
                    border: "1px solid rgba(74, 222, 128, 0.3)"
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                      <span style={{ color: "#c0baa8" }}>Cena (orig):</span>
                      <span style={{ color: "#888", textDecoration: "line-through" }}>
                        {formatPrice(selectedEvent.pricing.original_total)}
                      </span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                      <span style={{ color: "#c0baa8" }}>Popust:</span>
                      <span style={{ color: "#4ade80", fontWeight: "600" }}>
                        -{selectedEvent.pricing.discount_percent}%
                      </span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <span style={{ color: "#c0baa8" }}>Za naplatu:</span>
                      <span style={{ color: "#d4af37", fontWeight: "bold", fontSize: "1.1rem" }}>
                        {formatPrice(selectedEvent.pricing.final_total)}
                      </span>
                    </div>
                  </div>
                )}
                
                {/* Notes */}
                {notes && (
                  <div style={{ 
                    padding: "0.75rem",
                    background: "rgba(255,255,255,0.05)",
                    borderRadius: "8px",
                    color: "#c0baa8",
                    fontSize: "0.9rem"
                  }}>
                    <strong style={{ color: "#f5f2e8" }}>Napomena:</strong>
                    <p style={{ margin: "0.5rem 0 0 0", whiteSpace: "pre-wrap" }}>{notes}</p>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  };

  // Group events by date
  const groupEventsByDate = () => {
    const grouped = {};
    events.forEach(event => {
      const dateKey = formatDate(event.start_time);
      if (!grouped[dateKey]) {
        grouped[dateKey] = [];
      }
      grouped[dateKey].push(event);
    });
    return grouped;
  };

  const groupedEvents = groupEventsByDate();

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%)",
      padding: "80px 20px 40px"
    }}>
      {/* Header */}
      <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
        <h1 style={{
          fontSize: "2.5rem",
          color: "#d4af37",
          textAlign: "center",
          marginBottom: "0.5rem"
        }}>
          <Calendar style={{ display: "inline", marginRight: "0.5rem" }} />
          Termini
        </h1>
        <p style={{
          color: "#c0baa8",
          textAlign: "center",
          marginBottom: "2rem"
        }}>
          Pregled zakazanih termina
        </p>

        {/* Controls */}
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1.5rem",
          flexWrap: "wrap",
          gap: "1rem"
        }}>
          {/* View mode buttons */}
          <div style={{ display: "flex", gap: "0.5rem" }}>
            {["day", "week", "month"].map((mode) => (
              <Button
                key={mode}
                variant={viewMode === mode ? "default" : "outline"}
                onClick={() => setViewMode(mode)}
                style={{
                  background: viewMode === mode ? "#d4af37" : "transparent",
                  color: viewMode === mode ? "#1a1a1a" : "#d4af37",
                  border: "1px solid #d4af37"
                }}
              >
                {mode === "day" ? "Dan" : mode === "week" ? "Nedelja" : "Mesec"}
              </Button>
            ))}
          </div>

          {/* Navigation */}
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <Button variant="outline" onClick={goToPrevious} style={{ color: "#d4af37", border: "1px solid #d4af37" }}>
              ←
            </Button>
            <Button variant="outline" onClick={goToToday} style={{ color: "#d4af37", border: "1px solid #d4af37" }}>
              Danas
            </Button>
            <Button variant="outline" onClick={goToNext} style={{ color: "#d4af37", border: "1px solid #d4af37" }}>
              →
            </Button>
          </div>

          {/* Refresh */}
          <Button 
            variant="outline" 
            onClick={loadEvents}
            style={{ color: "#d4af37", border: "1px solid #d4af37" }}
          >
            ↻ Osveži
          </Button>
        </div>

        {/* Current date display */}
        <div style={{
          textAlign: "center",
          color: "#f5f2e8",
          fontSize: "1.2rem",
          marginBottom: "1.5rem"
        }}>
          {viewMode === "day" && formatDate(currentDate)}
          {viewMode === "week" && `Nedelja: ${formatDate(getDateRange().startISO)}`}
          {viewMode === "month" && currentDate.toLocaleDateString("sr-RS", { month: "long", year: "numeric" })}
        </div>

        {/* Loading */}
        {loading && (
          <div style={{ textAlign: "center", padding: "2rem", color: "#c0baa8" }}>
            Učitavanje termina...
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{ 
            textAlign: "center", 
            padding: "1rem", 
            background: "rgba(239, 68, 68, 0.2)",
            border: "1px solid #ef4444",
            borderRadius: "8px",
            color: "#ef4444",
            marginBottom: "1rem"
          }}>
            {error}
          </div>
        )}

        {/* Events */}
        {!loading && !error && (
          <>
            {events.length === 0 ? (
              <div style={{ 
                textAlign: "center", 
                padding: "3rem", 
                color: "#888",
                background: "rgba(255,255,255,0.02)",
                borderRadius: "12px"
              }}>
                <Calendar size={48} style={{ marginBottom: "1rem", opacity: 0.5 }} />
                <p>Nema zakazanih termina za ovaj period.</p>
              </div>
            ) : (
              <div>
                {Object.entries(groupedEvents).map(([date, dateEvents]) => (
                  <div key={date} style={{ marginBottom: "1.5rem" }}>
                    <h3 style={{ 
                      color: "#d4af37", 
                      fontSize: "1.1rem",
                      marginBottom: "0.75rem",
                      paddingBottom: "0.5rem",
                      borderBottom: "1px solid rgba(212, 175, 55, 0.3)"
                    }}>
                      {date}
                    </h3>
                    {dateEvents.map(renderEventCard)}
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* Stats */}
        {!loading && events.length > 0 && (
          <div style={{
            display: "flex",
            justifyContent: "center",
            gap: "2rem",
            marginTop: "2rem",
            padding: "1rem",
            background: "rgba(255,255,255,0.02)",
            borderRadius: "12px"
          }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ color: "#d4af37", fontSize: "1.5rem", fontWeight: "bold" }}>
                {events.length}
              </div>
              <div style={{ color: "#888", fontSize: "0.85rem" }}>Ukupno termina</div>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ color: "#4ade80", fontSize: "1.5rem", fontWeight: "bold" }}>
                {events.filter(e => e.type !== "spa" && !e.category?.toLowerCase().includes("spa")).length}
              </div>
              <div style={{ color: "#888", fontSize: "0.85rem" }}>Masaže</div>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ color: "#d4af37", fontSize: "1.5rem", fontWeight: "bold" }}>
                {events.filter(e => e.type === "spa" || e.category?.toLowerCase().includes("spa")).length}
              </div>
              <div style={{ color: "#888", fontSize: "0.85rem" }}>SPA</div>
            </div>
          </div>
        )}
      </div>

      {/* Event details modal */}
      {renderEventModal()}
    </div>
  );
};

export default Termini;
