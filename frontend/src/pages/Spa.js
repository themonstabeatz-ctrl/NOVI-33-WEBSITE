import React, { useState, useEffect, useCallback } from "react";
import { Helmet } from "react-helmet";
import { useLanguage } from "../context/LanguageContext";
import { useNavigate, Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Clock, Sparkles, Leaf } from "lucide-react";
import { throttle } from "../utils/debounce";
import { API_BASE } from "../config/api";
import { PriceBlock, InlinePriceBlock, formatRSD } from "../components/PriceBlock";
import { normalizePricing, normalizeServiceList } from "../utils/normalizePricing";
import { SPA_CARD_IDS, PACKAGE_TO_CARD_MAP, PACKAGE_TO_BASE_SERVICE_IDS, BASE_SERVICE_IDS } from "../config/spaCardIds";
import { DiscountBadge } from "../components/DiscountBadge";

// HELPER: Safe number formatting - prevents undefined.toLocaleString() crashes
const formatNumber = (value) => {
  const n = typeof value === 'number' && !Number.isNaN(value) ? value : 0;
  return n.toLocaleString('sr-RS');
};

/**
 * 🔐 BACKEND SERVICE ID MAP
 * Maps frontend option IDs to backend service UUIDs
 * Used for /api/spa/quote calls
 */
const SERVICE_ID_MAP = {
  // SPA ZONE services
  SAUNA_15: "7d46da23-a15a-4836-8db5-04d748cd6b72",
  SAUNA_30: "9bcb2fa6-4474-48be-93bd-72bea64a9807",
  STEAM_15: "876dff5c-4a13-4f5d-a4ff-b431f42b81e4",
  STEAM_30: "e00a0411-30fb-4a5e-87ef-32509bd1890e",
  JACUZZI_30: "af7458f2-6c40-4957-8871-347438e9ec57",
  JACUZZI_60: "ef4206ac-372c-40d9-9cf8-1dcaf1a42979",
  
  // SPA RITUAL base services
  SPA1: "ed3d9995-e195-4e56-8041-3459d3ecd324", // Silky Body Ritual
  SPA2: "3308333f-de1a-40a5-b33a-6acc171bc538", // Gentle Touch Ritual
  SPA3: "b4067c22-e4c0-4db7-aa7a-b6b6d396e27a", // Deep Renewal Ritual
  
  // Face Massage add-on
  FACE_MASSAGE: "b398a25e-4f70-4060-80ac-e080fc34a0ef",
};

/**
 * 🔄 FETCH SPA QUOTE FROM BACKEND
 * No JS calculations - backend returns original_total, final_total, discount
 * 
 * @param {string[]} serviceIds - Array of service UUIDs
 * @param {string} cardId - Card ID from SPA_CARD_IDS for card-level discounts
 */
async function fetchSpaQuote(serviceIds, cardId = null) {
  if (!serviceIds || serviceIds.length === 0) {
    return { original_total: 0, final_total: 0, discount_percentage: 0, has_discount: false };
  }
  
  try {
    // ✅ Include card_id in request for card-level discounts
    const payload = { 
      service_ids: serviceIds,
      ...(cardId && { card_id: cardId })
    };
    
    console.log("📤 SPA Quote request:", payload);
    
    const res = await fetch(`${API_BASE}/api/spa/quote`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
      body: JSON.stringify(payload)
    });
    
    if (!res.ok) {
      console.error("❌ SPA Quote failed:", res.status);
      return null;
    }
    
    const data = await res.json();
    console.log("📊 SPA Quote response:", { cardId, ...data });
    
    // ✅ Backend may return discount_percent OR discount_percentage
    const discountPct = Number(data.discount_percent ?? data.discount_percentage ?? 0);
    const finalTotal = Number(data.final_total ?? data.original_total ?? 0);
    const originalTotal = Number(data.original_total ?? 0);
    
    return {
      original_total: originalTotal,
      final_total: finalTotal,
      discount_percentage: discountPct,
      discount_percent: discountPct, // alias
      discount_amount: Number(data.discount_amount || 0),
      has_discount: discountPct > 0 && finalTotal < originalTotal,
      total_duration: Number(data.total_duration || 0),
      breakdown: data.breakdown || "",
      services: data.services || [],
      card_id: cardId
    };
  } catch (err) {
    console.error("❌ SPA Quote error:", err);
    return null;
  }
}

// ✅ CENTRALIZOVANI IZVOR ZA SPA ZONE CENE
// Ovo je jedini izvor istine za cene SPA zona
export const SPA_ZONE_PRICES = {
  // Za rituale (extra price - dodaje se na baznu cenu)
  extraPrices: {
    SAUNA_15: { minutes: 15, price: 800 },
    SAUNA_30: { minutes: 30, price: 1400 },
    STEAM_15: { minutes: 15, price: 800 },
    STEAM_30: { minutes: 30, price: 1400 },
    JACUZZI_30: { minutes: 30, price: 1400 },
    JACUZZI_60: { minutes: 60, price: 2800 },
  },
  // Za samostalno korišćenje zona (total price)
  totalPrices: {
    SAUNA_15: { minutes: 15, price: 1400 },
    SAUNA_30: { minutes: 30, price: 2400 },
    STEAM_15: { minutes: 15, price: 1400 },
    STEAM_30: { minutes: 30, price: 2400 },
    JACUZZI_30: { minutes: 30, price: 2200 },
    JACUZZI_60: { minutes: 60, price: 3400 },
  }
};

/**
 * 📊 CARD PRICE COMPONENT
 * Displays price from /api/spa/quote response
 * Shows strikethrough original + final when discount exists
 * NO JS calculations - purely displays backend data
 */
function CardPrice({ quote, fallbackPrice = 0, size = 'normal' }) {
  // Size configurations
  const sizes = {
    small: { original: '0.85rem', final: '1rem', badge: '0.7rem' },
    normal: { original: '1rem', final: '1.3rem', badge: '0.8rem' },
    large: { original: '1.1rem', final: '1.5rem', badge: '0.9rem' },
  };
  const s = sizes[size] || sizes.normal;

  // If no quote, show fallback
  if (!quote) {
    return (
      <div style={{ fontWeight: 'bold', color: '#d4af37', fontSize: s.final }}>
        {formatNumber(fallbackPrice)} RSD
      </div>
    );
  }

  const { original_total, final_total, discount_percentage, has_discount } = quote;
  const showDiscount = has_discount && Number(final_total) < Number(original_total);

  if (!showDiscount) {
    return (
      <div style={{ fontWeight: 'bold', color: '#d4af37', fontSize: s.final }}>
        {formatNumber(original_total || fallbackPrice)} RSD
      </div>
    );
  }

  // ✅ Show strikethrough original + final with discount badge
  return (
    <div className="card-price-block">
      <div style={{ 
        textDecoration: 'line-through', 
        opacity: 0.7, 
        color: '#888',
        fontSize: s.original 
      }}>
        {formatNumber(original_total)} RSD
      </div>
      <div style={{ 
        fontWeight: 'bold', 
        color: '#d4af37', 
        fontSize: s.final,
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem'
      }}>
        {formatNumber(final_total)} RSD
        {/* ✅ Use DiscountBadge image instead of text */}
        <DiscountBadge percent={discount_percentage} size={size === 'small' ? 24 : 32} />
      </div>
    </div>
  );
}

// SPA PACKAGES - 3 ritual packages + 1 zone-only package
const SPA_PACKAGES = [
  {
    id: "SPA1",
    name: "Silky Body Ritual",
    description: "Kompletna nega tela sa pilingom, oblogom i aromaterapijom.",
    included: [
      "Body scrub – 30 min",
      "Body wrap – 60 min",
      "Aroma masaža celog tela – 60 min"
    ],
    variants: [
      {
        id: "SPA1_BASE",
        label: "Bez masaže lica",
        totalMinutes: 150,
        totalPrice: 9400
      },
      {
        id: "SPA1_WITH_FACE",
        label: "Sa masažom lica (tokom body wrap-a)",
        totalMinutes: 150,
        totalPrice: 12400
      }
    ],
    spaZones: [
      {
        id: "SAUNA",
        label: "Sauna",
        options: [
          { id: "SAUNA_15", label: "15 min", extraMinutes: 15, extraPrice: 1400 },
          { id: "SAUNA_30", label: "30 min", extraMinutes: 30, extraPrice: 2400 }
        ]
      },
      {
        id: "STEAM",
        label: "Parno kupatilo",
        options: [
          { id: "STEAM_15", label: "15 min", extraMinutes: 15, extraPrice: 1400 },
          { id: "STEAM_30", label: "30 min", extraMinutes: 30, extraPrice: 2400 }
        ]
      },
      {
        id: "JACUZZI",
        label: "Jacuzzi",
        options: [
          { id: "JACUZZI_30", label: "30 min", extraMinutes: 30, extraPrice: 2200 },
          { id: "JACUZZI_60", label: "60 min", extraMinutes: 60, extraPrice: 3400 }
        ]
      }
    ]
  },
  {
    id: "SPA2",
    name: "Gentle Touch Ritual",
    description: "Kompletna nega tela sa pilingom, oblogom i aromaterapijom.",
    included: [
      "Body scrub – 60 min",
      "Body wrap – 60 min",
      "Aroma masaža celog tela – 60 min"
    ],
    variants: [
      {
        id: "SPA2_BASE",
        label: "Bez masaže lica",
        totalMinutes: 180,
        totalPrice: 10400
      },
      {
        id: "SPA2_WITH_FACE",
        label: "Sa masažom lica (tokom body wrap-a)",
        totalMinutes: 180,
        totalPrice: 13400
      }
    ],
    spaZones: [
      {
        id: "SAUNA",
        label: "Sauna",
        options: [
          { id: "SAUNA_15", label: "15 min", extraMinutes: 15, extraPrice: 1400 },
          { id: "SAUNA_30", label: "30 min", extraMinutes: 30, extraPrice: 2400 }
        ]
      },
      {
        id: "STEAM",
        label: "Parno kupatilo",
        options: [
          { id: "STEAM_15", label: "15 min", extraMinutes: 15, extraPrice: 1400 },
          { id: "STEAM_30", label: "30 min", extraMinutes: 30, extraPrice: 2400 }
        ]
      },
      {
        id: "JACUZZI",
        label: "Jacuzzi",
        options: [
          { id: "JACUZZI_30", label: "30 min", extraMinutes: 30, extraPrice: 2200 },
          { id: "JACUZZI_60", label: "60 min", extraMinutes: 60, extraPrice: 3400 }
        ]
      }
    ]
  },
  {
    id: "SPA3",
    name: "Deep Renewal Ritual",
    description: "Intenzivan tretman za dubinsku regeneraciju kože i opuštanje.",
    included: [
      "Body scrub – 60 min",
      "Body wrap – 60 min",
      "Aroma masaža celog tela – 90 min"
    ],
    variants: [
      {
        id: "SPA3_BASE",
        label: "Bez masaže lica",
        totalMinutes: 210,
        totalPrice: 11600
      },
      {
        id: "SPA3_WITH_FACE",
        label: "Sa masažom lica (tokom body wrap-a)",
        totalMinutes: 210,
        totalPrice: 14600
      }
    ],
    spaZones: [
      {
        id: "SAUNA",
        label: "Sauna",
        options: [
          { id: "SAUNA_15", label: "15 min", extraMinutes: 15, extraPrice: 1400 },
          { id: "SAUNA_30", label: "30 min", extraMinutes: 30, extraPrice: 2400 }
        ]
      },
      {
        id: "STEAM",
        label: "Parno kupatilo",
        options: [
          { id: "STEAM_15", label: "15 min", extraMinutes: 15, extraPrice: 1400 },
          { id: "STEAM_30", label: "30 min", extraMinutes: 30, extraPrice: 2400 }
        ]
      },
      {
        id: "JACUZZI",
        label: "Jacuzzi",
        options: [
          { id: "JACUZZI_30", label: "30 min", extraMinutes: 30, extraPrice: 2200 },
          { id: "JACUZZI_60", label: "60 min", extraMinutes: 60, extraPrice: 3400 }
        ]
      }
    ]
  }
];

// NEW SPA PACKAGES - Fixed price packages with included SPA zone
// Constants for herbal packages
const HERBAL_BASE_MINUTES = 120;   // 30 min scrub + 90 min tretman
const HERBAL_SPA_BONUS = 15;       // +15 min gratis ako je SPA uključen
const HERBAL_PRICE = 7600;

const NEW_SPA_PACKAGES = [
  {
    id: "SPA_HC_1",
    name: "Silky Herbal Compress Ritual",
    description: "Nega tela sa pilingom i dubokim opuštanjem uz aromu i tople biljne komprese.",
    included: [
      "Body scrub – 30 min",
      "Aroma masaža sa toplim biljnim kompresama – 90 min"
    ]
  },
  {
    id: "SPA_HC_2",
    name: "Thai Herbal Compress Ritual",
    description: "Tradicionalni tajlandski tretman sa toplim biljnim kompresama za rasterećenje mišića i uma.",
    included: [
      "Body scrub – 30 min",
      "Thai masaža sa toplim biljnim kompresama – 90 min"
    ]
  },
  {
    id: "SPA_HC_3",
    name: "Aroma Stone Harmony Ritual",
    description: "Spoj aromaterapije i toplog kamena za dubinsko opuštanje tela i otklanjanje napetosti.",
    included: [
      "Body scrub – 30 min",
      "Aromaterapija & topli kamen – 90 min"
    ]
  }
];

// SPA ZONE-ONLY package (no ritual, just zones)
const SPA_ZONE_ONLY = {
  id: "SPAZONE",
  name: "SPA Zone",
  description: "Isključivo korišćenje SPA zona bez rituala.",
  isZoneOnly: true,
  zones: [
    {
      id: "SAUNA",
      label: "Sauna",
      options: [
        { id: "SAUNA_15", label: "15 min", totalMinutes: 15, totalPrice: 1400 },
        { id: "SAUNA_30", label: "30 min", totalMinutes: 30, totalPrice: 2400 }
      ]
    },
    {
      id: "STEAM",
      label: "Parno kupatilo",
      options: [
        { id: "STEAM_15", label: "15 min", totalMinutes: 15, totalPrice: 1400 },
        { id: "STEAM_30", label: "30 min", totalMinutes: 30, totalPrice: 2400 }
      ]
    },
    {
      id: "JACUZZI",
      label: "Jacuzzi",
      options: [
        { id: "JACUZZI_30", label: "30 min", totalMinutes: 30, totalPrice: 2200 },
        { id: "JACUZZI_60", label: "60 min", totalMinutes: 60, totalPrice: 3400 }
      ]
    }
  ]
};

// "SPA Paketi za posebne prilike" - Old packages (DO NOT MODIFY)
const getFixedPackageDetails = (serviceName, duration, price) => {
  return { duration, price, serviceId: `${serviceName} - ${duration}` };
};

const Spa = () => {
  const { translate } = useLanguage();
  const navigate = useNavigate();
  const [isMobile, setIsMobile] = useState(false);

  // Helper function to translate variant labels
  const translateVariantLabel = (label) => {
    // Map known Serbian labels to translation keys
    if (label === "Bez masaže lica") {
      return translate("spaNoFaceMassage");
    }
    if (label === "Sa masažom lica (tokom body wrap-a)") {
      return translate("spaWithFaceMassage");
    }
    // Return original if no translation found
    return label;
  };

  // Helper function to translate package descriptions
  const translatePackageDescription = (description) => {
    const descMap = {
      "Kompletna nega tela sa pilingom, oblogom i aromaterapijom.": "spaCompleteBodyCare",
      "Isključivo korišćenje SPA zona bez rituala.": "spaZoneOnlyDesc",
      // Deep Renewal Ritual
      "Intenzivan tretman za dubinsku regeneraciju kože i opuštanje.": "spaDeepRenewalDesc",
      // Herbal packages
      "Nega tela sa pilingom i dubokim opuštanjem uz aromu i tople biljne komprese.": "spaSilkyHerbalDesc",
      "Tradicionalni tajlandski tretman sa toplim biljnim kompresama za rasterećenje mišića i uma.": "spaThaiHerbalCompressDesc",
      "Spoj aromaterapije i toplog kamena za dubinsko opuštanje tela i otklanjanje napetosti.": "spaAromaStoneDesc",
    };
    const translationKey = descMap[description];
    return translationKey ? translate(translationKey) : description;
  };

  // Helper function to translate "included" items in package cards
  const translateIncludedItem = (item) => {
    const itemMap = {
      // Body Scrub
      "Body scrub – 30 min": "spaBodyScrub30",
      "Body scrub – 60 min": "spaBodyScrub60",
      // Body Wrap
      "Body wrap – 60 min": "spaBodyWrap60",
      // Aroma Massage
      "Aroma masaža celog tela – 60 min": "spaAromaMassage60",
      "Aroma masaža celog tela – 90 min": "spaAromaMassage90",
      // Herbal Massages
      "Aroma masaža sa toplim biljnim kompresama – 90 min": "spaAromaHerbal90",
      "Thai masaža sa toplim biljnim kompresama – 90 min": "spaThaiHerbal90",
      // Aroma Stone
      "Aromaterapija & topli kamen – 90 min": "spaAromaStone90",
      // Face Massage
      "Masaža lica – 60 min": "spaFaceMassage60",
      // SPA Zone items
      "Sauna – 30 min": "spaSauna30",
      "Parno kupatilo – 30 min": "spaSteamBath30",
      "Đakuzi – 30 min": "spaJacuzzi30",
    };
    
    const translationKey = itemMap[item];
    return translationKey ? translate(translationKey) : item;
  };

  // Helper function to translate SPA zone labels
  const translateZoneLabel = (label) => {
    const zoneMap = {
      "Sauna": "spaSauna",
      "Parno kupatilo": "spaSteamBath",
      "Jacuzzi": "spaJacuzzi",
    };
    const translationKey = zoneMap[label];
    return translationKey ? translate(translationKey) : label;
  };

  // Detect mobile for video optimization
  useEffect(() => {
    const checkMobile = () => {
      const width = window.visualViewport ? window.visualViewport.width : window.screen.width;
      setIsMobile(width < 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // State for selected variant per package (default: first variant)
  const [selectedVariantByPackage, setSelectedVariantByPackage] = useState(() => {
    const initial = {};
    SPA_PACKAGES.forEach(pkg => {
      initial[pkg.id] = pkg.variants[0].id;
    });
    return initial;
  });

  // State for selected SPA zones - each zone tracked independently
  const [selectedZonesByPackage, setSelectedZonesByPackage] = useState(() => {
    const initial = {};
    SPA_PACKAGES.forEach(pkg => {
      // Default: all zones set to "Bez" (null)
      initial[pkg.id] = {
        SAUNA: null,    // null means "Bez"
        STEAM: null,    // null means "Bez"
        JACUZZI: null   // null means "Bez"
      };
    });
    // For zone-only package
    initial[SPA_ZONE_ONLY.id] = {
      SAUNA: null,
      STEAM: null,
      JACUZZI: null
    };
    return initial;
  });

  // State for NEW herbal packages - tracks selected SPA zone
  const [herbalZones, setHerbalZones] = useState({
    SPA_HC_1: "NONE",   // Silky Herbal - Default: Bez SPA zone
    SPA_HC_2: "NONE",   // Thai Herbal
    SPA_HC_3: "NONE"    // Aroma Stone
  });

  // ✅ NEW: State for dynamically loaded SPA Zone prices from API
  const [spaZonePrices, setSpaZonePrices] = useState({});
  const [spaZoneError, setSpaZoneError] = useState(null);
  
  // ✅ NEW: State for CARD discounts (from /api/spa/cards)
  // Key: card_id, Value: { discount_percent, has_discount }
  const [cardDiscounts, setCardDiscounts] = useState({});
  
  // ✅ NEW: State for QUOTE data per package (from /api/spa/quote)
  // Key: packageId, Value: { original_total, final_total, discount_percentage, has_discount }
  const [packageQuotes, setPackageQuotes] = useState({});

  // ✅ Fetch SPA Card discounts from API on mount
  useEffect(() => {
    const fetchSpaCards = async () => {
      try {
        console.log('📥 Loading SPA cards from API...');
        const res = await fetch(`${API_BASE}/api/spa/cards`, { 
          cache: "no-store",
          headers: { 'Accept': 'application/json' }
        });
        
        const cards = await res.json();
        
        if (!res.ok) {
          throw new Error(cards?.error || `HTTP ${res.status}`);
        }
        
        // Build discount map by card_id
        const discountMap = {};
        cards.forEach(card => {
          discountMap[card.card_id] = {
            discount_percent: card.discount_percent || 0,
            has_discount: card.has_discount || false,
            title: card.title_sr || card.title_en
          };
        });
        
        console.log('✅ SPA Card discounts loaded:', discountMap);
        setCardDiscounts(discountMap);
      } catch (err) {
        console.error('❌ Failed to load SPA cards:', err);
      }
    };
    
    fetchSpaCards();
  }, []);

  // ✅ Fetch SPA Zone prices from API with no-cache + normalizePricing
  useEffect(() => {
    const fetchSpaZonePrices = async () => {
      try {
        console.log('📥 Loading SPA services from API (no-cache)...');
        console.log('🔗 Endpoint:', `${API_BASE}/api/spa/services`);
        
        // ✅ cache: "no-store" - obavezno dok debugging
        const res = await fetch(`${API_BASE}/api/spa/services`, { 
          cache: "no-store",
          headers: { 'Accept': 'application/json' }
        });
        
        // ✅ FIX: Read body only once to avoid "body stream already read"
        const raw = await res.text();
        let rawServices = [];
        try {
          rawServices = raw ? JSON.parse(raw) : [];
        } catch {
          console.error('❌ Failed to parse SPA services JSON:', raw);
          throw new Error('Invalid JSON response');
        }
        
        if (!res.ok) {
          throw new Error(rawServices?.error || rawServices?.message || `HTTP ${res.status}`);
        }
        
        // ✅ NORMALIZE all services - handles snake_case/camelCase variations
        const services = normalizeServiceList(rawServices);
        
        // ✅ DEBUG LOG - proveri da li imamo discount podatke
        console.log('📊 SPA SERVICES DEBUG (first 5):');
        console.table(services.slice(0, 5).map(s => ({
          name: s.name?.substring(0, 30),
          category: s.category,
          original: s.original_price,
          final: s.final_price,
          disc: s.discount_percent,
          has: s.has_discount
        })));
        
        // Build price map from spa_zone category services
        const zoneMap = {};
        services.forEach(s => {
          if (s.category === 'spa_zone') {
            zoneMap[s.name] = {
              price: s.final_price || s.price,
              original_price: s.original_price,
              final_price: s.final_price,
              discount_percent: s.discount_percent,
              has_discount: s.has_discount,
              duration: s.duration,
              id: s.id
            };
          }
        });
        
        console.log('✅ SPA Zone prices loaded:', Object.keys(zoneMap).length, 'zones');
        setSpaZonePrices(zoneMap);
      } catch (err) {
        console.error('❌ Failed to load SPA Zone prices:', err);
        setSpaZoneError('Greška pri učitavanju cena');
      }
    };
    
    fetchSpaZonePrices();
  }, []);

  // ✅ Helper to get zone FINAL price from API data (with discount applied)
  const getZonePrice = (zoneName) => {
    const zone = spaZonePrices[zoneName];
    // Koristi final_price ako postoji popust, inače original
    return zone?.final_price || zone?.price || 0;
  };
  
  // ✅ Helper to get zone pricing info (for PriceBlock display)
  const getZonePricing = (zoneName) => {
    const zone = spaZonePrices[zoneName];
    if (!zone) return null;
    return {
      original_price: zone.original_price || zone.price || 0,
      final_price: zone.final_price || zone.price || 0,
      discount_percent: zone.discount_percent || 0,
      has_discount: zone.has_discount || false
    };
  };
  
  const getZoneDuration = (zoneName) => {
    return spaZonePrices[zoneName]?.duration || 0;
  };

  // ✅ QUOTE API: Fetch quotes for all packages when selections change
  // Builds service_ids array from selections and calls /api/spa/quote
  const buildServiceIds = useCallback((pkgId, variantId, zoneSelections) => {
    const serviceIds = [];
    
    // Add base ritual service
    if (SERVICE_ID_MAP[pkgId]) {
      serviceIds.push(SERVICE_ID_MAP[pkgId]);
    }
    
    // Add face massage if variant includes it
    if (variantId && variantId.includes("WITH_FACE")) {
      serviceIds.push(SERVICE_ID_MAP.FACE_MASSAGE);
    }
    
    // Add zone selections
    if (zoneSelections) {
      Object.entries(zoneSelections).forEach(([zoneId, optionId]) => {
        if (optionId && SERVICE_ID_MAP[optionId]) {
          serviceIds.push(SERVICE_ID_MAP[optionId]);
        }
      });
    }
    
    // ✅ If no services selected, use base service IDs from config
    if (serviceIds.length === 0 && PACKAGE_TO_BASE_SERVICE_IDS[pkgId]) {
      return [...PACKAGE_TO_BASE_SERVICE_IDS[pkgId]];
    }
    
    return serviceIds;
  }, []);

  // ✅ INITIAL MOUNT: Fetch quotes immediately for all packages with default selections
  // This ensures discount badges show immediately without user interaction
  useEffect(() => {
    const fetchInitialQuotes = async () => {
      console.log("🚀 Fetching initial quotes on mount...");
      const newQuotes = {};
      
      // Fetch quotes for all SPA packages with BASE service_ids
      for (const pkg of SPA_PACKAGES) {
        const cardId = PACKAGE_TO_CARD_MAP[pkg.id];
        const baseServiceIds = PACKAGE_TO_BASE_SERVICE_IDS[pkg.id] || [];
        
        console.log(`📤 Initial quote for ${pkg.id}:`, { cardId, baseServiceIds });
        
        if (baseServiceIds.length > 0) {
          const quote = await fetchSpaQuote(baseServiceIds, cardId);
          if (quote) {
            newQuotes[pkg.id] = quote;
          }
        }
      }
      
      // Herbal cards also need initial quotes
      for (const card of NEW_SPA_PACKAGES) {
        const cardId = PACKAGE_TO_CARD_MAP[card.id];
        const baseServiceIds = PACKAGE_TO_BASE_SERVICE_IDS[card.id] || [];
        
        if (baseServiceIds.length > 0) {
          const quote = await fetchSpaQuote(baseServiceIds, cardId);
          if (quote) {
            newQuotes[card.id] = quote;
          }
        }
      }
      
      // ✅ Romantic packages - fetch quotes on mount
      const romanticPackages = [
        { id: "ROMANTIC_COUPLE", cardId: "romantic_couple_package" },
        { id: "ROMANTIC_PEELING", cardId: "romantic_peeling_couple_package" }
      ];
      
      for (const pkg of romanticPackages) {
        const baseServiceIds = PACKAGE_TO_BASE_SERVICE_IDS[pkg.id] || [];
        
        console.log(`📤 Initial quote for ${pkg.id}:`, { cardId: pkg.cardId, baseServiceIds });
        
        if (baseServiceIds.length > 0) {
          const quote = await fetchSpaQuote(baseServiceIds, pkg.cardId);
          if (quote) {
            newQuotes[pkg.id] = quote;
          }
        }
      }
      
      console.log("📊 Initial quotes loaded:", newQuotes);
      setPackageQuotes(newQuotes);
    };
    
    fetchInitialQuotes();
  }, []); // Empty deps - only run on mount

  // ✅ Fetch quote when selections CHANGE for each package
  // Uses PACKAGE_TO_CARD_MAP to send card_id for card-level discounts
  useEffect(() => {
    const fetchAllQuotes = async () => {
      const newQuotes = {};
      
      // Fetch quotes for all SPA packages
      for (const pkg of SPA_PACKAGES) {
        const variantId = selectedVariantByPackage[pkg.id];
        const zoneSelections = selectedZonesByPackage[pkg.id];
        const serviceIds = buildServiceIds(pkg.id, variantId, zoneSelections);
        
        // ✅ Get card_id from PACKAGE_TO_CARD_MAP
        const cardId = PACKAGE_TO_CARD_MAP[pkg.id];
        
        if (serviceIds.length > 0) {
          const quote = await fetchSpaQuote(serviceIds, cardId);
          if (quote) {
            newQuotes[pkg.id] = quote;
          }
        }
      }
      
      // Fetch quote for SPA Zone Only (using correct ID "SPAZONE")
      const zoneOnlySelections = selectedZonesByPackage[SPA_ZONE_ONLY.id];
      const zoneOnlyServiceIds = [];
      if (zoneOnlySelections) {
        Object.entries(zoneOnlySelections).forEach(([zoneId, optionId]) => {
          if (optionId && SERVICE_ID_MAP[optionId]) {
            zoneOnlyServiceIds.push(SERVICE_ID_MAP[optionId]);
          }
        });
      }
      if (zoneOnlyServiceIds.length > 0) {
        // ✅ SPA Zone Only uses spa_zone card_id (ID is "SPAZONE")
        const quote = await fetchSpaQuote(zoneOnlyServiceIds, PACKAGE_TO_CARD_MAP[SPA_ZONE_ONLY.id]);
        if (quote) {
          newQuotes[SPA_ZONE_ONLY.id] = quote;
        }
      }
      
      console.log("📊 All package quotes:", newQuotes);
      setPackageQuotes(prev => ({ ...prev, ...newQuotes }));
    };
    
    // Debounce to avoid too many API calls
    const timeoutId = setTimeout(fetchAllQuotes, 300);
    return () => clearTimeout(timeoutId);
  }, [selectedVariantByPackage, selectedZonesByPackage, buildServiceIds]);

  // Scroll fade-out effect for hero (IDENTICAL to Massage.js)
  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY;
      const spaHeroSection = document.querySelector('.spa-hero-fixed');
      const spaHeroLogo = document.querySelector('.spa-hero-logo');
      const spaHeroTitle = document.querySelector('.spa-hero-title');
      const spaHeroSubtitle = document.querySelector('.spa-hero-subtitle');
      
      if (!spaHeroSection || !spaHeroLogo) return;
      
      const heroHeight = spaHeroSection.offsetHeight;
      const scrollPercent = Math.min(scrollPosition / heroHeight, 1);
      
      if (scrollPercent > 0.05) {
        // Scroll down - transform logo with fade and blur
        const opacity = Math.max(1 - (scrollPercent - 0.05) * 3, 0);
        const scale = Math.max(1 - (scrollPercent - 0.05) * 1.5, 0.2);
        
        spaHeroLogo.style.opacity = opacity;
        spaHeroLogo.style.transform = `scale(${scale})`;
        spaHeroLogo.style.filter = `blur(${(scrollPercent - 0.05) * 15}px)`;
        
        if (spaHeroTitle) {
          spaHeroTitle.style.opacity = opacity;
          spaHeroTitle.style.transform = `translateY(-${(scrollPercent - 0.05) * 80}px)`;
        }
        
        if (spaHeroSubtitle) {
          spaHeroSubtitle.style.opacity = opacity;
          spaHeroSubtitle.style.transform = `translateY(-${(scrollPercent - 0.05) * 60}px)`;
        }
      } else {
        // Reset to default when at top
        spaHeroLogo.style.opacity = '1';
        spaHeroLogo.style.transform = 'scale(1)';
        spaHeroLogo.style.filter = 'none';
        
        if (spaHeroTitle) {
          spaHeroTitle.style.opacity = '1';
          spaHeroTitle.style.transform = 'translateY(0)';
        }
        
        if (spaHeroSubtitle) {
          spaHeroSubtitle.style.opacity = '1';
          spaHeroSubtitle.style.transform = 'translateY(0)';
        }
      }
    };

    const throttledHandleScroll = throttle(handleScroll, 16);
    window.addEventListener('scroll', throttledHandleScroll, { passive: true });
    return () => window.removeEventListener('scroll', throttledHandleScroll);
  }, []);

  // Parallax effect for content sections (IDENTICAL to Massage.js)
  useEffect(() => {
    const handleParallaxScroll = () => {
      const scrolled = window.scrollY;
      const spaHeroSection = document.querySelector('.spa-hero-fixed');
      
      if (!spaHeroSection) return;
      
      const heroHeight = spaHeroSection.offsetHeight;
      
      // Apply parallax to sections after hero
      if (scrolled > heroHeight * 0.3) {
        const parallaxContent = document.querySelector('.spa-parallax-content');
        if (parallaxContent) {
          const speed = 0.5;
          const yPos = -(scrolled - heroHeight * 0.3) * speed;
          parallaxContent.style.transform = `translateY(${yPos}px)`;
        }
      }
    };

    const throttledHandleParallaxScroll = throttle(handleParallaxScroll, 16);
    window.addEventListener('scroll', throttledHandleParallaxScroll, { passive: true });
    return () => window.removeEventListener('scroll', throttledHandleParallaxScroll);
  }, []);

  // Intersection Observer for slide-in animation (IDENTICAL to Massage.js)
  useEffect(() => {
    const cards = document.querySelectorAll('.spa-ritual-card, .spa-special-card');
    
    // Get grid columns for dynamic slide direction
    const grid = document.querySelector('.spa-ritual-grid');
    const gridStyle = grid ? window.getComputedStyle(grid) : null;
    const gridTemplateColumns = gridStyle ? gridStyle.gridTemplateColumns : '';
    const columns = gridTemplateColumns.split(' ').length;
    
    cards.forEach((card, index) => {
      let slideDirection;
      let transformStart;
      
      if (window.innerWidth <= 768 || columns === 1) {
        const pattern = index % 3;
        const slideDistance = 200;
        const tiltAngle = 25;
        
        if (pattern === 0) {
          slideDirection = 'from-left';
          transformStart = `translateX(-${slideDistance}px) rotateY(-${tiltAngle}deg)`;
        } else if (pattern === 1) {
          slideDirection = 'from-bottom';
          transformStart = 'translateY(150px)';
        } else {
          slideDirection = 'from-right';
          transformStart = `translateX(${slideDistance}px) rotateY(${tiltAngle}deg)`;
        }
        card.style.transition = 'opacity 1.5s ease-out, transform 1.5s cubic-bezier(0.4, 0, 0.2, 1)';
      } else {
        const columnPosition = index % columns;
        const slideDistance = 300;
        const tiltAngle = 30;
        
        if (columnPosition === 0) {
          slideDirection = 'from-left';
          transformStart = `translateX(-${slideDistance}px) rotateY(-${tiltAngle}deg)`;
        } else if (columnPosition === columns - 1) {
          slideDirection = 'from-right';
          transformStart = `translateX(${slideDistance}px) rotateY(${tiltAngle}deg)`;
        } else {
          slideDirection = 'from-bottom';
          transformStart = 'translateY(150px)';
        }
        card.style.transition = 'opacity 1.5s ease-out, transform 1.5s cubic-bezier(0.4, 0, 0.2, 1)';
      }
      
      card.setAttribute('data-slide-direction', slideDirection);
      card.setAttribute('data-transform-start', transformStart);
      card.style.transformStyle = 'preserve-3d';
      // Set initial hidden state
      card.style.opacity = '0';
      card.style.transform = transformStart;
    });

    const observerOptions = {
      root: null,
      rootMargin: '100px',
      threshold: 0.1
    };

    const handleIntersection = (entries) => {
      entries.forEach((entry) => {
        const transformStart = entry.target.getAttribute('data-transform-start');
        const isPortrait = window.innerHeight > window.innerWidth;
        
        if (entry.isIntersecting) {
          // Card entering viewport - show it
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translate(0, 0) rotateY(0deg)';
        } else if (!isPortrait) {
          // Card leaving viewport - hide ONLY on desktop/landscape (not portrait)
          entry.target.style.opacity = '0';
          entry.target.style.transform = transformStart;
        }
        // If portrait mode: do nothing when card leaves viewport (keep it visible)
      });
    };

    const observer = new IntersectionObserver(handleIntersection, observerOptions);
    
    cards.forEach((card) => {
      observer.observe(card);
    });

    return () => {
      observer.disconnect();
    };
  }, []);

  // Handle variant selection
  const handleVariantSelect = (pkgId, variantId) => {
    setSelectedVariantByPackage(prev => ({
      ...prev,
      [pkgId]: variantId
    }));
  };

  // Handle SPA zone selection
  const handleZoneOptionSelect = (pkgId, zoneId, optionId) => {
    setSelectedZonesByPackage(prev => ({
      ...prev,
      [pkgId]: {
        ...prev[pkgId],
        [zoneId]: optionId  // Set specific zone option (or null for "Bez")
      }
    }));
  };

  // Handle booking button click
  const handleSpaBookClick = (pkg) => {
    const { totalPrice, totalMinutes, selectedVariant, selectedZones } = calculateTotals(pkg);

    // ✅ VALIDATION for SPA Zone Only - at least one zone must be selected
    if (pkg.isZoneOnly && totalPrice === 0) {
      alert("Izaberite bar jednu SPA zonu (Sauna, Parno kupatilo ili Jacuzzi).");
      return;
    }

    // Get base values from variant
    const basePrice = selectedVariant?.totalPrice || 0;
    const baseDuration = selectedVariant?.totalMinutes || 0;

    // Calculate addon totals
    let addonPrice = 0;
    let addonDuration = 0;
    
    // Check if face massage is selected (variant with face)
    const hasFace = selectedVariant?.label?.includes("lica") && !selectedVariant?.label?.includes("Bez");

    // Build zone details
    const zones = pkg.isZoneOnly ? pkg.zones : pkg.spaZones;
    let saunaMin = 0, steamMin = 0, jacuzziMin = 0;
    const zoneLabels = [];
    
    // Map selection IDs to API service names for price lookup
    const selectionToApiName = {
      'SAUNA_15': 'Sauna 15 min',
      'SAUNA_30': 'Sauna 30 min',
      'STEAM_15': 'Parno kupatilo 15 min',
      'STEAM_30': 'Parno kupatilo 30 min',
      'JACUZZI_30': 'Jacuzzi 30 min',
      'JACUZZI_60': 'Jacuzzi 60 min'
    };
    
    if (zones) {
      zones.forEach(zone => {
        const selectedOptionId = selectedZones[zone.id];
        if (selectedOptionId) {
          // Use hardcoded prices from SPA_PACKAGES
          const option = zone.options.find(o => o.id === selectedOptionId);
          if (option) {
            zoneLabels.push(`${zone.label} ${option.label}`);
            addonPrice += option.extraPrice || option.totalPrice || 0;
            addonDuration += option.extraMinutes || option.totalMinutes || 0;
            
            if (zone.id === 'SAUNA') saunaMin = option.extraMinutes || option.totalMinutes || 0;
            else if (zone.id === 'STEAM') steamMin = option.extraMinutes || option.totalMinutes || 0;
            else if (zone.id === 'JACUZZI') jacuzziMin = option.extraMinutes || option.totalMinutes || 0;
          }
        }
      });
    }
    
    const spaZoneLabel = zoneLabels.length > 0 ? zoneLabels.join(", ") : "Bez SPA zona";

    // ✅ Get card_id from PACKAGE_TO_CARD_MAP
    const cardId = PACKAGE_TO_CARD_MAP[pkg.id] || "";
    
    // ✅ Build service_ids array for booking
    const bookingServiceIds = buildServiceIds(pkg.id, selectedVariant?.id, selectedZones);

    const params = new URLSearchParams({
      source: "spa",
      spaCategory: "SPA_RITUAL",
      spaPackageId: pkg.id,
      spaName: pkg.name,
      // ✅ Card ID for card-level discounts
      card_id: cardId,
      // ✅ Service IDs for booking
      service_ids: bookingServiceIds.join(","),
      // Base values
      basePrice: String(basePrice),
      baseDuration: String(baseDuration),
      // Face addon
      face: hasFace ? "1" : "0",
      // Zone addons
      sauna: String(saunaMin),
      steam: String(steamMin),
      jacuzzi: String(jacuzziMin),
      // Addon totals
      addonPrice: String(addonPrice),
      addonDuration: String(addonDuration),
      // Final totals
      totalPrice: String(totalPrice),
      totalDuration: String(totalMinutes),
      // Labels
      spaZoneLabel: spaZoneLabel
    });

    if (pkg.isZoneOnly) {
      // Override source and category for SPA_ZONE
      params.set("source", "spaZone");
      params.set("spaCategory", "SPA_ZONE");
      params.set("variantId", "ZONE_ONLY");
      params.set("variantLabel", "Samo SPA zona");
      // ✅ Add selected zones list
      params.set("selectedSpaZones", zoneLabels.join("|"));
      // ✅ Override card_id for SPA Zone Only
      params.set("card_id", PACKAGE_TO_CARD_MAP["SPA_ZONE_ONLY"] || "spa_zone");
    } else {
      params.append("variantId", selectedVariant.id);
      params.append("variantLabel", selectedVariant.label);
    }

    console.log("📍 SPA booking redirect params:", Object.fromEntries(params));

    navigate(`/contact?${params.toString()}`);
  };

  // Handle booking for HERBAL packages
  const handleNewPackageBookClick = (card) => {
    const selectedZone = herbalZones[card.id] || "NONE";
    const hasSpa = selectedZone !== "NONE";
    
    // Dynamic duration: 120 min base, +15 min if SPA selected
    const totalMinutes = HERBAL_BASE_MINUTES + (hasSpa ? HERBAL_SPA_BONUS : 0);
    
    // ✅ Get PRICE from packageQuotes (from API), fallback to HERBAL_PRICE
    const quoteData = packageQuotes[card.id];
    const originalPrice = quoteData?.original_total || HERBAL_PRICE;
    const finalPrice = quoteData?.final_total || HERBAL_PRICE;
    const hasDiscount = quoteData?.has_discount || false;
    const discountPercent = quoteData?.discount_percent || quoteData?.discount_percentage || 0;
    
    // Determine SPA zone label and included zone
    let spaZoneLabel = "Bez SPA zone";
    let includedSpaZone = "none";
    if (selectedZone === "SAUNA_15") {
      spaZoneLabel = "Sauna – 15 min (uključeno)";
      includedSpaZone = "sauna15";
    }
    if (selectedZone === "STEAM_15") {
      spaZoneLabel = "Parno kupatilo – 15 min (uključeno)";
      includedSpaZone = "steam15";
    }

    // ✅ Get card_id from PACKAGE_TO_CARD_MAP for Herbal packages
    const cardId = PACKAGE_TO_CARD_MAP[card.id] || "";

    const params = new URLSearchParams({
      source: "spa",
      spaCategory: "SPA_HERBAL",
      spaPackageId: card.id,
      spaName: card.name,
      // ✅ Card ID for card-level discounts
      card_id: cardId,
      // ✅ PRICING from API quote - NOT hardcoded!
      basePrice: String(originalPrice),
      baseDuration: String(HERBAL_BASE_MINUTES),
      includedSpaZone: includedSpaZone,
      spaZoneLabel: spaZoneLabel,
      // ✅ Variant label for listing - use SPA zone choice
      variantLabel: spaZoneLabel,
      // ✅ Send ORIGINAL price (total_original) for backend
      totalPrice: String(originalPrice),
      totalDuration: String(totalMinutes),
      // ✅ Extra pricing info for Contact page
      originalPrice: String(originalPrice),
      finalPrice: String(finalPrice),
      hasDiscount: String(hasDiscount),
      discountPercent: String(discountPercent)
    });

    console.log("📍 HERBAL package booking params:", Object.fromEntries(params));

    navigate(`/contact?${params.toString()}`);
  };

  // Handle zone selection for HERBAL packages
  const handleHerbalZoneChange = (cardId, value) => {
    setHerbalZones(prev => ({
      ...prev,
      [cardId]: value  // "NONE" | "SAUNA_15" | "STEAM_15"
    }));
  };

  // Calculate totals for display
  const calculateTotals = (pkg) => {
    const selectedZones = selectedZonesByPackage[pkg.id] || {};
    
    if (pkg.isZoneOnly) {
      // ✅ Zone-only package - use API prices
      let totalMinutes = 0;
      let totalPrice = 0;
      
      // Map selection IDs to API service names
      const selectionToApiName = {
        'SAUNA_15': 'Sauna 15 min',
        'SAUNA_30': 'Sauna 30 min',
        'STEAM_15': 'Parno kupatilo 15 min',
        'STEAM_30': 'Parno kupatilo 30 min',
        'JACUZZI_30': 'Jacuzzi 30 min',
        'JACUZZI_60': 'Jacuzzi 60 min'
      };
      
      Object.entries(selectedZones).forEach(([zoneId, optionId]) => {
        if (optionId) {
          const apiName = selectionToApiName[optionId];
          if (apiName && spaZonePrices[apiName]) {
            totalPrice += spaZonePrices[apiName].price;
            totalMinutes += spaZonePrices[apiName].duration;
          }
        }
      });
      
      return {
        totalPrice: totalPrice || 0,
        totalMinutes: totalMinutes || 0,
        selectedVariant: null,
        selectedZones
      };
    } else {
      // Regular ritual package
      const selectedVariantId = selectedVariantByPackage[pkg.id] || (pkg.variants && pkg.variants[0] && pkg.variants[0].id);
      const selectedVariant = pkg.variants && pkg.variants.find(v => v.id === selectedVariantId);
      
      if (!selectedVariant) {
        return {
          totalPrice: 0,
          totalMinutes: 0,
          selectedVariant: null,
          selectedZones
        };
      }
      
      let baseMinutes = selectedVariant.totalMinutes;
      let basePrice = selectedVariant.totalPrice;
      
      // Add ALL selected zones - use hardcoded prices from SPA_PACKAGES
      let zoneMinutes = 0;
      let zonePrice = 0;
      
      if (pkg.spaZones) {
        pkg.spaZones.forEach(zone => {
          const selectedOptionId = selectedZones[zone.id];
          if (selectedOptionId) {  // If not null (not "Bez")
            const option = zone.options.find(o => o.id === selectedOptionId);
            if (option) {
              zoneMinutes += option.extraMinutes;
              zonePrice += option.extraPrice;
            }
          }
        });
      }
      
      return {
        totalPrice: basePrice + zonePrice,
        totalMinutes: baseMinutes + zoneMinutes,
        selectedVariant,
        selectedZones
      };
    }
  };

  // Old SPA packages data
  const royalThaiRitualDetails = getFixedPackageDetails('Royal Thai Ritual', '180 min', '12,900 RSD');
  const detoxHarmonyDetails = getFixedPackageDetails('Detox Harmony', '120 min', '9,900 RSD');
  const aromaEscapeDetails = getFixedPackageDetails('Aroma Escape', '90 min', '7,900 RSD');
  const thaiBalanceDetails = getFixedPackageDetails('Thai Balance', '60 min', '6,500 RSD');
  const buaLuangRelaxDetails = getFixedPackageDetails('Bua Luang Relax Ritual', '90 min', '8,500 RSD');
  const gentleTouchCoupleDetails = getFixedPackageDetails('Gentle Touch Couple Package', '120 min', '11,900 RSD');
  const goldenReviveDetails = getFixedPackageDetails('Golden Revive', '90 min', '8,900 RSD');
  const spiritOfSiamDetails = getFixedPackageDetails('Spirit of Siam', '120 min', '10,900 RSD');
  const serenityBlossomDetails = getFixedPackageDetails('Serenity Blossom Ritual', '120 min', '9,400 RSD');
  
  const spaSpecialPackages = [
    {
      key: 'royalThaiRitual',
      name: translate("royalThaiRitual"),
      duration: royalThaiRitualDetails.duration,
      price: royalThaiRitualDetails.price,
      serviceId: royalThaiRitualDetails.serviceId,
      description: translate("royalThaiRitualDesc"),
      included: translate("royalThaiRitualIncluded"),
      note: translate("royalThaiRitualNote"),
      category: "premium",
      popular: true
    },
    {
      key: 'detoxHarmony',
      name: translate("detoxHarmony"),
      duration: detoxHarmonyDetails.duration,
      price: detoxHarmonyDetails.price,
      serviceId: detoxHarmonyDetails.serviceId,
      description: translate("detoxHarmonyDesc"),
      included: translate("detoxHarmonyIncluded"),
      note: translate("detoxHarmonyNote"),
      category: "body",
      popular: false
    },
    {
      key: 'aromaEscape',
      name: translate("aromaEscape"),
      duration: aromaEscapeDetails.duration,
      price: aromaEscapeDetails.price,
      serviceId: aromaEscapeDetails.serviceId,
      description: translate("aromaEscapeDesc"),
      included: translate("aromaEscapeIncluded"),
      note: translate("aromaEscapeNote"),
      category: "relaxation",
      popular: true
    },
    {
      key: 'thaiBalance',
      name: translate("thaiBalance"),
      duration: thaiBalanceDetails.duration,
      price: thaiBalanceDetails.price,
      serviceId: thaiBalanceDetails.serviceId,
      description: translate("thaiBalanceDesc"),
      included: translate("thaiBalanceIncluded"),
      note: translate("thaiBalanceNote"),
      category: "body",
      popular: false
    },
    {
      key: 'buaLuangRelax',
      name: translate("buaLuangRelax"),
      duration: buaLuangRelaxDetails.duration,
      price: buaLuangRelaxDetails.price,
      serviceId: buaLuangRelaxDetails.serviceId,
      description: translate("buaLuangRelaxDesc"),
      included: translate("buaLuangRelaxIncluded"),
      note: translate("buaLuangRelaxNote"),
      category: "relaxation",
      popular: true
    },
    {
      key: 'gentleTouchCouple',
      name: translate("gentleTouchCouple"),
      duration: gentleTouchCoupleDetails.duration,
      price: gentleTouchCoupleDetails.price,
      serviceId: gentleTouchCoupleDetails.serviceId,
      description: translate("gentleTouchCoupleDesc"),
      included: translate("gentleTouchCoupleIncluded"),
      note: translate("gentleTouchCoupleNote"),
      category: "premium",
      popular: true
    },
    {
      key: 'goldenRevive',
      name: translate("goldenRevive"),
      duration: goldenReviveDetails.duration,
      price: goldenReviveDetails.price,
      serviceId: goldenReviveDetails.serviceId,
      description: translate("goldenReviveDesc"),
      included: translate("goldenReviveIncluded"),
      note: translate("goldenReviveNote"),
      category: "face",
      popular: false
    },
    {
      key: 'spiritOfSiam',
      name: translate("spiritOfSiam"),
      duration: spiritOfSiamDetails.duration,
      price: spiritOfSiamDetails.price,
      serviceId: spiritOfSiamDetails.serviceId,
      description: translate("spiritOfSiamDesc"),
      included: translate("spiritOfSiamIncluded"),
      note: translate("spiritOfSiamNote"),
      category: "premium",
      popular: true
    },
    {
      key: 'serenityBlossom',
      name: translate("serenityBlossom"),
      duration: serenityBlossomDetails.duration,
      price: serenityBlossomDetails.price,
      serviceId: serenityBlossomDetails.serviceId,
      description: translate("serenityBlossomDesc"),
      included: translate("serenityBlossomIncluded"),
      note: translate("serenityBlossomNote"),
      category: "face",
      popular: true
    }
  ];

  const getCategoryIcon = (category) => {
    switch(category) {
      case "premium":
        return <Sparkles className="w-4 h-4 text-amber-400" />;
      case "relaxation":
        return <Leaf className="w-4 h-4 text-green-400" />;
      default:
        return <Clock className="w-4 h-4 text-blue-400" />;
    }
  };

  const getCategoryColor = (category) => {
    switch(category) {
      case "premium":
        return "bg-gradient-to-r from-amber-500 to-yellow-600";
      case "relaxation":
        return "bg-gradient-to-r from-green-500 to-teal-600";
      case "face":
        return "bg-gradient-to-r from-pink-500 to-rose-600";
      default:
        return "bg-gradient-to-r from-blue-500 to-indigo-600";
    }
  };

  return (
    <div className="spa-page" id="top">
      <Helmet>
        <title>SPA Paketi - Bua Luang Thai Spa</title>
        <meta name="description" content="Ekskluzivni SPA tretmani sa body scrub, body wrap i aromaterapijom" />
      </Helmet>

      {/* Hero Section - IDENTICAL to Massage.js */}
      <section className="spa-hero-fixed">
        <div className="spa-hero-video-container">
          <video 
            autoPlay 
            muted 
            loop 
            playsInline
            preload="auto"
            className="spa-hero-video"
          >
            {isMobile ? (
              <source src="https://customer-assets.emergentagent.com/job_thaispa-mobile/artifacts/a5g7ogwu_SPA.mp4" type="video/mp4" />
            ) : (
              <source src="https://customer-assets.emergentagent.com/job_thaibookingspa/artifacts/4z9ic4bo_SPA.mp4" type="video/mp4" />
            )}
          </video>
          <div className="spa-hero-overlay"></div>
        </div>
        
        <div className="spa-hero-content">
          <div className="spa-hero-logo">
            <img 
              src="https://customer-assets.emergentagent.com/job_83ed575e-3634-46be-8586-79a3348def97/artifacts/7sfhgz1m_Bua%20luang%20logo.png"
              alt="Bua Luang Logo"
              className="hero-logo-image"
            />
          </div>
          <h1 className="spa-hero-title">{translate("spaRitualsTitle")}</h1>
          <div className="spa-hero-divider"></div>
          <p className="spa-hero-subtitle">
            {translate("spaRitualsSubtitle")}
          </p>
        </div>
      </section>

      {/* Parallax Content Section */}
      <div className="spa-parallax-content">

      {/* SPA Ritual Packages Grid */}
      <section style={{
        padding: '80px 20px',
        maxWidth: '1400px',
        margin: '0 auto',
        background: 'transparent'
      }}>
        <div className="spa-ritual-grid" style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))',
          gap: '2.5rem'
        }}>
          {SPA_PACKAGES.map((pkg, index) => {
            const { totalPrice, totalMinutes, selectedVariant, selectedZones } = calculateTotals(pkg);
            const selectedVariantId = selectedVariantByPackage[pkg.id];

            return (
              <Card key={pkg.id} 
                className="spa-ritual-card"
                style={{
                  background: 'rgba(10, 10, 10, 0.65)',
                  backdropFilter: 'blur(8px)',
                  border: '1px solid rgba(212, 175, 55, 0.3)',
                  borderRadius: '16px',
                  overflow: 'hidden',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  cursor: 'pointer',
                  position: 'relative' // For absolute badge positioning
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = '#d4af37';
                  e.currentTarget.style.transform = 'translateY(-8px)';
                  e.currentTarget.style.boxShadow = '0 12px 32px rgba(212, 175, 55, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(212, 175, 55, 0.3)';
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}>
                
                <CardContent style={{ padding: '0.6rem' }}>
                  {/* Header: Duration and Price */}
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '0.3rem',
                    paddingBottom: '0.3rem',
                    borderBottom: '1px solid rgba(212, 175, 55, 0.2)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <Clock size={14} color="#d4af37" />
                      <span style={{ color: '#f5f2e8', fontSize: '0.8rem', fontWeight: '600' }}>
                        {packageQuotes[pkg.id]?.total_duration || formatNumber(totalMinutes)} min
                      </span>
                    </div>
                    {/* ✅ Use CardPrice with quote data - NO JS calculations */}
                    <CardPrice 
                      quote={packageQuotes[pkg.id]} 
                      fallbackPrice={totalPrice}
                      size="small"
                    />
                  </div>

                  {/* Package Name */}
                  <h3 style={{
                    fontSize: '1rem',
                    color: '#d4af37',
                    marginBottom: '0.2rem',
                    fontWeight: 'bold'
                  }}>
                    {pkg.name}
                  </h3>

                  {/* Description */}
                  <p style={{
                    color: '#c0baa8',
                    marginBottom: '0.4rem',
                    fontSize: '0.72rem',
                    lineHeight: '1.3'
                  }}>
                    {translatePackageDescription(pkg.description)}
                  </p>

                  {/* Included Services */}
                  <div style={{ marginBottom: '0.4rem' }}>
                    <h4 style={{
                      color: '#d4af37',
                      fontSize: '0.72rem',
                      marginBottom: '0.2rem',
                      fontWeight: '600'
                    }}>
                      {translate("spaIncluded")}
                    </h4>
                    <ul style={{
                      listStyle: 'none',
                      padding: 0,
                      margin: 0
                    }}>
                      {pkg.included.map((item, idx) => (
                        <li key={idx} style={{
                          color: '#f5f2e8',
                          fontSize: '0.68rem',
                          marginBottom: '0.1rem',
                          paddingLeft: '1rem',
                          position: 'relative',
                          lineHeight: '1.3'
                        }}>
                          <Sparkles size={9} color="#d4af37" style={{
                            position: 'absolute',
                            left: 0,
                            top: '2px'
                          }} />
                          {translateIncludedItem(item)}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Variant Selection (Radio Buttons) */}
                  <div style={{ marginBottom: '0.4rem' }}>
                    <h4 style={{
                      color: '#d4af37',
                      fontSize: '0.72rem',
                      marginBottom: '0.25rem',
                      fontWeight: '600'
                    }}>
                      {translate("spaSelectVariant")}
                    </h4>
                    {pkg.variants.map((variant) => (
                      <label key={variant.id} style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.35rem',
                        marginBottom: '0.25rem',
                        cursor: 'pointer',
                        color: '#f5f2e8',
                        fontSize: '0.72rem',
                        padding: '0.25rem',
                        borderRadius: '4px',
                        background: selectedVariantId === variant.id ? 'rgba(212, 175, 55, 0.1)' : 'transparent',
                        transition: 'background 0.3s ease'
                      }}>
                        <input
                          type="radio"
                          name={`variant-${pkg.id}`}
                          value={variant.id}
                          checked={selectedVariantId === variant.id}
                          onChange={() => handleVariantSelect(pkg.id, variant.id)}
                          style={{
                            accentColor: '#d4af37',
                            cursor: 'pointer',
                            width: '12px',
                            height: '12px'
                          }}
                        />
                        <span>
                          {translateVariantLabel(variant.label)}
                          {variant.totalPrice > pkg.variants[0].totalPrice && (
                            <span style={{ color: '#d4af37', fontSize: '0.68rem', marginLeft: '0.25rem' }}>
                              (+{formatNumber(variant.totalPrice - pkg.variants[0].totalPrice)} RSD)
                            </span>
                          )}
                        </span>
                      </label>
                    ))}
                  </div>

                  {/* SPA ZONA - Premium Boxed Section */}
                  <div style={{
                    marginBottom: '0.4rem',
                    padding: '0.4rem 0.5rem',
                    background: 'rgba(0, 0, 0, 0.3)',
                    border: '1px solid rgba(212, 175, 55, 0.4)',
                    borderRadius: '8px',
                    boxShadow: '0 2px 8px rgba(212, 175, 55, 0.1)'
                  }}>
                    <h4 style={{
                      color: '#d4af37',
                      fontSize: '0.72rem',
                      marginBottom: '0.3rem',
                      fontWeight: 'bold',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px'
                    }}>
                      {translate("spaZoneTitle")}
                    </h4>
                    
                    {pkg.spaZones.map((zone) => (
                      <div key={zone.id} style={{ marginBottom: '0.3rem' }}>
                        <p style={{
                          color: '#d4af37',
                          fontSize: '0.68rem',
                          marginBottom: '0.15rem',
                          fontWeight: '600'
                        }}>
                          {translateZoneLabel(zone.label)}:
                        </p>
                        {/* "Bez" option */}
                        <label style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.2rem',
                          marginBottom: '0.1rem',
                          cursor: 'pointer',
                          color: '#f5f2e8',
                          fontSize: '0.68rem',
                          padding: '0.12rem',
                          borderRadius: '3px',
                          background: selectedZones[zone.id] === null ? 'rgba(212, 175, 55, 0.15)' : 'transparent',
                          transition: 'background 0.3s ease'
                        }}>
                          <input
                            type="radio"
                            name={`zone-${pkg.id}-${zone.id}`}
                            value="bez"
                            checked={selectedZones[zone.id] === null}
                            onChange={() => handleZoneOptionSelect(pkg.id, zone.id, null)}
                            style={{
                              accentColor: '#d4af37',
                              cursor: 'pointer',
                              width: '10px',
                              height: '10px'
                            }}
                          />
                          <span>{translate("spaWithout")}</span>
                        </label>
                        {/* Zone options - ✅ Using API prices with DISCOUNT DISPLAY */}
                        {zone.options.map((option) => {
                          const isSelected = selectedZones[zone.id] === option.id;
                          // ✅ Map option ID to API service name
                          const apiNameMap = {
                            'SAUNA_15': 'Sauna 15 min',
                            'SAUNA_30': 'Sauna 30 min',
                            'STEAM_15': 'Parno kupatilo 15 min',
                            'STEAM_30': 'Parno kupatilo 30 min',
                            'JACUZZI_30': 'Jacuzzi 30 min',
                            'JACUZZI_60': 'Jacuzzi 60 min'
                          };
                          const apiName = apiNameMap[option.id];
                          const zonePricing = getZonePricing(apiName);
                          const displayPrice = zonePricing?.final_price || option.extraPrice || option.totalPrice || 0;
                          const hasDiscount = zonePricing?.has_discount || false;
                          const originalPrice = zonePricing?.original_price || displayPrice;
                          const discountPct = zonePricing?.discount_percent || 0;
                          
                          return (
                            <label key={option.id} style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '0.2rem',
                              marginBottom: '0.1rem',
                              cursor: 'pointer',
                              color: '#f5f2e8',
                              fontSize: '0.68rem',
                              padding: '0.12rem',
                              borderRadius: '3px',
                              background: isSelected ? 'rgba(212, 175, 55, 0.15)' : 'transparent',
                              transition: 'background 0.3s ease'
                            }}>
                              <input
                                type="radio"
                                name={`zone-${pkg.id}-${zone.id}`}
                                value={option.id}
                                checked={isSelected}
                                onChange={() => handleZoneOptionSelect(pkg.id, zone.id, option.id)}
                                style={{
                                  accentColor: '#d4af37',
                                  cursor: 'pointer',
                                  width: '10px',
                                  height: '10px'
                                }}
                              />
                              <span>
                                {option.label}{' '}
                                {hasDiscount ? (
                                  <span>
                                    <span style={{ color: '#888', textDecoration: 'line-through', fontSize: '0.85em' }}>
                                      {formatNumber(originalPrice)}
                                    </span>{' '}
                                    <span style={{ color: '#4ade80', fontWeight: '600' }}>
                                      {formatNumber(displayPrice)} RSD
                                    </span>{' '}
                                    <DiscountBadge percent={discountPct} size={16} />
                                  </span>
                                ) : (
                                  <span style={{ color: '#d4af37', fontWeight: '600', opacity: 0.9 }}>
                                    (+{formatNumber(displayPrice)} RSD)
                                  </span>
                                )}
                              </span>
                            </label>
                          );
                        })}
                      </div>
                    ))}
                  </div>

                  {/* Total Summary */}
                  <div style={{
                    background: 'rgba(212, 175, 55, 0.1)',
                    padding: '0.35rem',
                    borderRadius: '5px',
                    marginBottom: '0.4rem',
                    border: '1px solid rgba(212, 175, 55, 0.2)'
                  }}>
                    <p style={{
                      color: '#f5f2e8',
                      fontSize: '0.68rem',
                      margin: 0,
                      lineHeight: '1.3'
                    }}>
                      <strong style={{ color: '#d4af37' }}>{translate("spaTotalDuration")}</strong> {formatNumber(totalMinutes)} min<br />
                      {packageQuotes[pkg.id]?.has_discount ? (
                        <>
                          <strong style={{ color: '#d4af37' }}>{translate("spaOriginalPrice")}</strong>{' '}
                          <span style={{ textDecoration: 'line-through', opacity: 0.6 }}>
                            {formatNumber(packageQuotes[pkg.id].original_total)} RSD
                          </span>
                          <br />
                          <strong style={{ color: '#d4af37' }}>{translate("spaFinalPrice")}</strong>{' '}
                          <span style={{ color: '#4ade80', fontWeight: 600 }}>
                            {formatNumber(packageQuotes[pkg.id].final_total)} RSD
                          </span>{' '}
                          <DiscountBadge percent={packageQuotes[pkg.id].discount_percent || packageQuotes[pkg.id].discount_percentage} size={20} />
                        </>
                      ) : (
                        <>
                          <strong style={{ color: '#d4af37' }}>{translate("spaTotalPrice")}</strong>{' '}
                          <span>{formatNumber(packageQuotes[pkg.id]?.original_total || totalPrice)} RSD</span>
                        </>
                      )}
                    </p>
                  </div>

                  {/* Book Button */}
                  <button
                    onClick={() => handleSpaBookClick(pkg)}
                    style={{
                      width: '100%',
                      padding: '0.55rem',
                      background: 'linear-gradient(135deg, #d4af37 0%, #f4d03f 100%)',
                      border: 'none',
                      borderRadius: '6px',
                      color: '#1a1a1a',
                      fontSize: '0.8rem',
                      fontWeight: 'bold',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 4px 15px rgba(212, 175, 55, 0.3)'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.transform = 'translateY(-2px)';
                      e.target.style.boxShadow = '0 8px 25px rgba(212, 175, 55, 0.5)';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.transform = 'translateY(0)';
                      e.target.style.boxShadow = '0 4px 15px rgba(212, 175, 55, 0.3)';
                    }}
                  >
                    {translate("spaBookButton")}
                  </button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      {/* NEW FIXED-PRICE SPA PACKAGES - 3 Herbal & Stone Rituals */}
      <section style={{
        padding: '80px 20px',
        maxWidth: '1400px',
        margin: '0 auto',
        background: 'transparent'
      }}>
        <h2 style={{
          textAlign: 'center',
          fontSize: '2.5rem',
          color: '#d4af37',
          marginBottom: '1rem'
        }}>
          {translate("spaHerbalTitle")}
        </h2>
        <p style={{
          textAlign: 'center',
          color: '#c0baa8',
          maxWidth: '700px',
          margin: '0 auto 3rem',
          fontSize: '1.1rem'
        }}>
          {translate("spaHerbalSubtitle")}
        </p>
        <div className="spa-ritual-grid" style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))',
          gap: '2.5rem'
        }}>
          {NEW_SPA_PACKAGES.map((pkg) => {
            const selectedZone = herbalZones[pkg.id] || "NONE";
            const hasSpa = selectedZone !== "NONE";
            
            // Dynamic duration: 120 min base, +15 min if SPA selected
            const totalMinutes = HERBAL_BASE_MINUTES + (hasSpa ? HERBAL_SPA_BONUS : 0);
            const totalPrice = HERBAL_PRICE;

            return (
              <Card key={pkg.id} 
                className="spa-ritual-card"
                style={{
                  background: 'rgba(10, 10, 10, 0.65)',
                  backdropFilter: 'blur(8px)',
                  border: '1px solid rgba(212, 175, 55, 0.3)',
                  borderRadius: '16px',
                  overflow: 'hidden',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = '#d4af37';
                  e.currentTarget.style.transform = 'translateY(-8px)';
                  e.currentTarget.style.boxShadow = '0 12px 32px rgba(212, 175, 55, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(212, 175, 55, 0.3)';
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}>
                <CardContent style={{ padding: '0.6rem' }}>
                  {/* Header: Duration and Price - DYNAMIC from packageQuotes */}
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '0.3rem',
                    paddingBottom: '0.3rem',
                    borderBottom: '1px solid rgba(212, 175, 55, 0.2)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <Clock size={14} color="#d4af37" />
                      <span style={{ color: '#f5f2e8', fontSize: '0.8rem', fontWeight: '600' }}>
                        {formatNumber(totalMinutes)} min
                      </span>
                    </div>
                    {packageQuotes[pkg.id]?.has_discount ? (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <span style={{ textDecoration: 'line-through', opacity: 0.6, color: '#f5f2e8', fontSize: '0.85rem' }}>
                          {formatNumber(packageQuotes[pkg.id].original_total)} RSD
                        </span>
                        <span style={{ fontSize: '1rem', fontWeight: 'bold', color: '#4ade80' }}>
                          {formatNumber(packageQuotes[pkg.id].final_total)} RSD
                        </span>
                        <DiscountBadge percent={packageQuotes[pkg.id].discount_percent || packageQuotes[pkg.id].discount_percentage} size={18} />
                      </div>
                    ) : (
                      <div style={{
                        fontSize: '1rem',
                        fontWeight: 'bold',
                        color: '#d4af37'
                      }}>
                        {formatNumber(packageQuotes[pkg.id]?.original_total || totalPrice)} RSD
                      </div>
                    )}
                  </div>

                  {/* Package Name */}
                  <h3 style={{
                    fontSize: '1rem',
                    color: '#d4af37',
                    marginBottom: '0.2rem',
                    fontWeight: 'bold'
                  }}>
                    {pkg.name}
                  </h3>

                  {/* Description */}
                  <p style={{
                    color: '#c0baa8',
                    marginBottom: '0.4rem',
                    fontSize: '0.72rem',
                    lineHeight: '1.3'
                  }}>
                    {translatePackageDescription(pkg.description)}
                  </p>

                  {/* Included Services */}
                  <div style={{ marginBottom: '0.4rem' }}>
                    <h4 style={{
                      color: '#d4af37',
                      fontSize: '0.72rem',
                      marginBottom: '0.2rem',
                      fontWeight: '600'
                    }}>
                      {translate("spaIncluded")}
                    </h4>
                    <ul style={{
                      listStyle: 'none',
                      padding: 0,
                      margin: 0
                    }}>
                      {pkg.included.map((item, idx) => (
                        <li key={idx} style={{
                          color: '#f5f2e8',
                          fontSize: '0.68rem',
                          marginBottom: '0.1rem',
                          paddingLeft: '1rem',
                          position: 'relative',
                          lineHeight: '1.3'
                        }}>
                          <Sparkles size={9} color="#d4af37" style={{
                            position: 'absolute',
                            left: 0,
                            top: '2px'
                          }} />
                          {translateIncludedItem(item)}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* MINI SPA ZONA Section */}
                  <div style={{
                    marginBottom: '0.4rem',
                    padding: '0.4rem 0.5rem',
                    background: 'rgba(0, 0, 0, 0.3)',
                    border: '1px solid rgba(212, 175, 55, 0.4)',
                    borderRadius: '8px',
                    boxShadow: '0 2px 8px rgba(212, 175, 55, 0.1)'
                  }}>
                    <h4 style={{
                      color: '#d4af37',
                      fontSize: '0.72rem',
                      marginBottom: '0.3rem',
                      fontWeight: 'bold',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px'
                    }}>
                      {translate("spaZoneIncluded")}
                    </h4>
                    
                    <div style={{ marginBottom: '0.2rem' }}>
                      <p style={{
                        color: '#d4af37',
                        fontSize: '0.68rem',
                        marginBottom: '0.15rem',
                        fontWeight: '600'
                      }}>
                        {translate("spaSelectOption")}
                      </p>
                      
                      {/* "Bez SPA zone" option - DEFAULT */}
                      <label style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.2rem',
                        marginBottom: '0.1rem',
                        cursor: 'pointer',
                        color: '#f5f2e8',
                        fontSize: '0.68rem',
                        padding: '0.12rem',
                        borderRadius: '3px',
                        background: selectedZone === "NONE" ? 'rgba(212, 175, 55, 0.15)' : 'transparent',
                        transition: 'background 0.3s ease'
                      }}>
                        <input
                          type="radio"
                          name={`herbal-spa-${pkg.id}`}
                          value="NONE"
                          checked={selectedZone === "NONE"}
                          onChange={() => handleHerbalZoneChange(pkg.id, "NONE")}
                          style={{
                            accentColor: '#d4af37',
                            cursor: 'pointer',
                            width: '10px',
                            height: '10px'
                          }}
                        />
                        <span>{translate("spaNone")}</span>
                      </label>
                      
                      {/* Sauna option - ✅ Shows "(uključeno)" not "+0 RSD" */}
                      <label style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.2rem',
                        marginBottom: '0.1rem',
                        cursor: 'pointer',
                        color: '#f5f2e8',
                        fontSize: '0.68rem',
                        padding: '0.12rem',
                        borderRadius: '3px',
                        background: selectedZone === "SAUNA_15" ? 'rgba(212, 175, 55, 0.15)' : 'transparent',
                        transition: 'background 0.3s ease'
                      }}>
                        <input
                          type="radio"
                          name={`herbal-spa-${pkg.id}`}
                          value="SAUNA_15"
                          checked={selectedZone === "SAUNA_15"}
                          onChange={() => handleHerbalZoneChange(pkg.id, "SAUNA_15")}
                          style={{
                            accentColor: '#d4af37',
                            cursor: 'pointer',
                            width: '10px',
                            height: '10px'
                          }}
                        />
                        <span>{translate("spaSauna15")} <span style={{ color: '#4ade80', fontWeight: '600' }}>{translate("spaIncludedLabel")}</span></span>
                      </label>
                      
                      {/* Parno kupatilo option - ✅ Shows "(uključeno)" not "+0 RSD" */}
                      <label style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.2rem',
                        marginBottom: '0.1rem',
                        cursor: 'pointer',
                        color: '#f5f2e8',
                        fontSize: '0.68rem',
                        padding: '0.12rem',
                        borderRadius: '3px',
                        background: selectedZone === "STEAM_15" ? 'rgba(212, 175, 55, 0.15)' : 'transparent',
                        transition: 'background 0.3s ease'
                      }}>
                        <input
                          type="radio"
                          name={`herbal-spa-${pkg.id}`}
                          value="STEAM_15"
                          checked={selectedZone === "STEAM_15"}
                          onChange={() => handleHerbalZoneChange(pkg.id, "STEAM_15")}
                          style={{
                            accentColor: '#d4af37',
                            cursor: 'pointer',
                            width: '10px',
                            height: '10px'
                          }}
                        />
                        <span>{translate("spaSteamBath15")} <span style={{ color: '#4ade80', fontWeight: '600' }}>{translate("spaIncludedLabel")}</span></span>
                      </label>
                    </div>
                  </div>

                  {/* Total Summary */}
                  <div style={{
                    background: 'rgba(212, 175, 55, 0.1)',
                    padding: '0.35rem',
                    borderRadius: '5px',
                    marginBottom: '0.4rem',
                    border: '1px solid rgba(212, 175, 55, 0.2)'
                  }}>
                    <p style={{
                      color: '#f5f2e8',
                      fontSize: '0.68rem',
                      margin: 0,
                      lineHeight: '1.3'
                    }}>
                      <strong style={{ color: '#d4af37' }}>{translate("spaTotalDuration")}</strong> {formatNumber(totalMinutes)} min<br />
                      {packageQuotes[pkg.id]?.has_discount ? (
                        <>
                          <strong style={{ color: '#d4af37' }}>{translate("spaOriginalPrice")}</strong>{' '}
                          <span style={{ textDecoration: 'line-through', opacity: 0.6 }}>
                            {formatNumber(packageQuotes[pkg.id].original_total)} RSD
                          </span>
                          <br />
                          <strong style={{ color: '#d4af37' }}>{translate("spaFinalPrice")}</strong>{' '}
                          <span style={{ color: '#4ade80', fontWeight: 600 }}>
                            {formatNumber(packageQuotes[pkg.id].final_total)} RSD
                          </span>{' '}
                          <DiscountBadge percent={packageQuotes[pkg.id].discount_percent || packageQuotes[pkg.id].discount_percentage} size={20} />
                        </>
                      ) : (
                        <>
                          <strong style={{ color: '#d4af37' }}>{translate("spaTotalPrice")}</strong>{' '}
                          <span>{formatNumber(packageQuotes[pkg.id]?.original_total || totalPrice)} RSD</span>
                        </>
                      )}
                    </p>
                  </div>

                  {/* Book Button */}
                  <button
                    onClick={() => handleNewPackageBookClick(pkg)}
                    style={{
                      width: '100%',
                      padding: '0.55rem',
                      background: 'linear-gradient(135deg, #d4af37 0%, #f4d03f 100%)',
                      border: 'none',
                      borderRadius: '6px',
                      color: '#1a1a1a',
                      fontSize: '0.8rem',
                      fontWeight: 'bold',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 4px 15px rgba(212, 175, 55, 0.3)'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.transform = 'translateY(-2px)';
                      e.target.style.boxShadow = '0 8px 25px rgba(212, 175, 55, 0.5)';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.transform = 'translateY(0)';
                      e.target.style.boxShadow = '0 4px 15px rgba(212, 175, 55, 0.3)';
                    }}
                  >
                    {translate("spaBookButton")}
                  </button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

 

      {/* SPA ZONE ONLY - Moved to end */}
      <section style={{
        padding: '80px 20px',
        maxWidth: '1400px',
        margin: '0 auto',
        background: 'transparent'
      }}>
        <div className="spa-ritual-grid" style={{
          display: 'grid',
          gridTemplateColumns: '1fr',
          gap: '2.5rem'
        }}>
          {/* SPA ZONE ONLY Card - Horizontal Layout */}
          {(() => {
            const { totalPrice, totalMinutes, selectedZones } = calculateTotals(SPA_ZONE_ONLY);

            return (
              <Card 
                key={SPA_ZONE_ONLY.id}
                className="spa-ritual-card"
                style={{
                  background: 'rgba(10, 10, 10, 0.65)',
                  backdropFilter: 'blur(8px)',
                  border: '1px solid rgba(212, 175, 55, 0.3)',
                  borderRadius: '16px',
                  overflow: 'hidden',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = '#d4af37';
                  e.currentTarget.style.transform = 'translateY(-8px)';
                  e.currentTarget.style.boxShadow = '0 12px 32px rgba(212, 175, 55, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(212, 175, 55, 0.3)';
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}>
                <CardContent style={{ padding: '1.5rem' }}>
                  {/* Header */}
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: '1rem',
                    flexWrap: 'wrap',
                    gap: '1rem'
                  }}>
                    <div>
                      <h3 style={{
                        fontSize: '1.4rem',
                        color: '#d4af37',
                        marginBottom: '0.5rem',
                        fontWeight: 'bold',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                      }}>
                        {SPA_ZONE_ONLY.name}
                        {/* ✅ Show discount badge if card has discount */}
                        {cardDiscounts["spa_zone"]?.has_discount && (
                          <DiscountBadge percent={cardDiscounts["spa_zone"].discount_percent} size={20} />
                        )}
                      </h3>
                    </div>

                    {/* Duration and Price */}
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '1rem'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <Clock size={18} color="#d4af37" />
                        <span style={{ color: '#f5f2e8', fontSize: '1rem', fontWeight: '600' }}>
                          {packageQuotes[SPA_ZONE_ONLY.id]?.total_duration || totalMinutes} min
                        </span>
                      </div>
                      {/* ✅ Use CardPrice with quote data - NO JS calculations */}
                      <CardPrice 
                        quote={packageQuotes[SPA_ZONE_ONLY.id]} 
                        fallbackPrice={totalPrice}
                        size="normal"
                      />
                    </div>
                  </div>

                  {/* Description */}
                  <p style={{
                    color: '#c0baa8',
                    marginBottom: '0.9rem',
                    fontSize: '0.9rem',
                    lineHeight: '1.5'
                  }}>
                    {translatePackageDescription(SPA_ZONE_ONLY.description)}
                  </p>

                  {/* Zone Options in Horizontal Layout */}
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                    gap: '1.5rem',
                    marginBottom: '1rem'
                  }}>
                    {SPA_ZONE_ONLY.zones.map((zone) => (
                      <div key={zone.id}>
                        <h4 style={{
                          color: '#d4af37',
                          fontSize: '0.9rem',
                          marginBottom: '0.5rem',
                          fontWeight: '600'
                        }}>
                        {translateZoneLabel(zone.label)}:
                        </h4>
                        {/* "Bez" option */}
                        <label style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.4rem',
                          marginBottom: '0.3rem',
                          cursor: 'pointer',
                          color: '#f5f2e8',
                          fontSize: '0.85rem',
                          padding: '0.3rem',
                          borderRadius: '4px',
                          background: selectedZones[zone.id] === null ? 'rgba(212, 175, 55, 0.15)' : 'transparent',
                          transition: 'background 0.3s ease'
                        }}>
                          <input
                            type="radio"
                            name={`zone-only-${zone.id}`}
                            value="bez"
                            checked={selectedZones[zone.id] === null}
                            onChange={() => handleZoneOptionSelect(SPA_ZONE_ONLY.id, zone.id, null)}
                            style={{
                              accentColor: '#d4af37',
                              cursor: 'pointer',
                              width: '14px',
                              height: '14px'
                            }}
                          />
                          <span>{translate("spaWithout")}</span>
                        </label>
                        {/* Zone options - ✅ Using API prices with DISCOUNT DISPLAY */}
                        {zone.options.map((option) => {
                          const isSelected = selectedZones[zone.id] === option.id;
                          // ✅ Map option ID to API service name
                          const apiNameMap = {
                            'SAUNA_15': 'Sauna 15 min',
                            'SAUNA_30': 'Sauna 30 min',
                            'STEAM_15': 'Parno kupatilo 15 min',
                            'STEAM_30': 'Parno kupatilo 30 min',
                            'JACUZZI_30': 'Jacuzzi 30 min',
                            'JACUZZI_60': 'Jacuzzi 60 min'
                          };
                          const apiName = apiNameMap[option.id];
                          const zonePricing = getZonePricing(apiName);
                          const displayPrice = zonePricing?.final_price || option.totalPrice;
                          const hasDiscount = zonePricing?.has_discount || false;
                          const originalPrice = zonePricing?.original_price || displayPrice;
                          const discountPct = zonePricing?.discount_percent || 0;
                          
                          return (
                            <label key={option.id} style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '0.4rem',
                              marginBottom: '0.3rem',
                              cursor: 'pointer',
                              color: '#f5f2e8',
                              fontSize: '0.85rem',
                              padding: '0.3rem',
                              borderRadius: '4px',
                              background: isSelected ? 'rgba(212, 175, 55, 0.15)' : 'transparent',
                              transition: 'background 0.3s ease'
                            }}>
                              <input
                                type="radio"
                                name={`zone-only-${zone.id}`}
                                value={option.id}
                                checked={isSelected}
                                onChange={() => handleZoneOptionSelect(SPA_ZONE_ONLY.id, zone.id, option.id)}
                                style={{
                                  accentColor: '#d4af37',
                                  cursor: 'pointer',
                                  width: '14px',
                                  height: '14px'
                                }}
                              />
                              <span>
                                {option.label}{' '}
                                {hasDiscount ? (
                                  <span>
                                    <span style={{ color: '#888', textDecoration: 'line-through', fontSize: '0.8em' }}>
                                      {formatNumber(originalPrice)} RSD
                                    </span>{' '}
                                    <span style={{ color: '#4ade80', fontWeight: '600' }}>
                                      {formatNumber(displayPrice)} RSD
                                    </span>{' '}
                                    <DiscountBadge percent={discountPct} size={16} />
                                  </span>
                                ) : (
                                  <span style={{ color: '#d4af37', fontWeight: '600' }}>
                                    +{formatNumber(displayPrice)} RSD
                                  </span>
                                )}
                              </span>
                            </label>
                          );
                        })}
                      </div>
                    ))}
                  </div>

                  {/* Total Summary */}
                  <div style={{
                    background: 'rgba(212, 175, 55, 0.1)',
                    padding: '0.7rem',
                    borderRadius: '8px',
                    marginBottom: '1rem',
                    border: '1px solid rgba(212, 175, 55, 0.2)'
                  }}>
                    <p style={{
                      color: '#f5f2e8',
                      fontSize: '0.9rem',
                      margin: 0,
                      lineHeight: '1.5'
                    }}>
                      <strong style={{ color: '#d4af37' }}>{translate("spaTotalDuration")}</strong> {packageQuotes[SPA_ZONE_ONLY.id]?.total_duration || formatNumber(totalMinutes)} min<br />
                      {packageQuotes[SPA_ZONE_ONLY.id]?.has_discount ? (
                        <>
                          <strong style={{ color: '#d4af37' }}>{translate("spaOriginalPrice")}</strong>{' '}
                          <span style={{ textDecoration: 'line-through', opacity: 0.6 }}>
                            {formatNumber(packageQuotes[SPA_ZONE_ONLY.id].original_total)} RSD
                          </span>
                          <br />
                          <strong style={{ color: '#d4af37' }}>{translate("spaFinalPrice")}</strong>{' '}
                          <span style={{ color: '#4ade80', fontWeight: 600 }}>
                            {formatNumber(packageQuotes[SPA_ZONE_ONLY.id].final_total)} RSD
                          </span>{' '}
                          <DiscountBadge percent={packageQuotes[SPA_ZONE_ONLY.id].discount_percent || packageQuotes[SPA_ZONE_ONLY.id].discount_percentage} size={20} />
                        </>
                      ) : (
                        <>
                          <strong style={{ color: '#d4af37' }}>{translate("spaTotalPrice")}</strong>{' '}
                          <span>{formatNumber(packageQuotes[SPA_ZONE_ONLY.id]?.original_total || totalPrice)} RSD</span>
                        </>
                      )}
                    </p>
                  </div>

                  {/* Book Button - FIX A: type="button" + logging */}
                  <button
                    type="button"
                    onClick={() => {
                      console.log("[SPA_ZONE] Book click", { selectedZones, totalPrice, totalMinutes });
                      if (totalPrice === 0) {
                        alert("Izaberite bar jednu SPA zonu (Sauna, Parno kupatilo ili Jacuzzi).");
                        return;
                      }
                      handleSpaBookClick(SPA_ZONE_ONLY);
                    }}
                    disabled={totalPrice === 0}
                    style={{
                      width: '100%',
                      padding: '0.7rem',
                      background: totalPrice === 0 
                        ? 'linear-gradient(135deg, #666 0%, #888 100%)' 
                        : 'linear-gradient(135deg, #d4af37 0%, #f4d03f 100%)',
                      border: 'none',
                      borderRadius: '8px',
                      color: totalPrice === 0 ? '#aaa' : '#1a1a1a',
                      fontSize: '0.95rem',
                      fontWeight: 'bold',
                      cursor: totalPrice === 0 ? 'not-allowed' : 'pointer',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 4px 15px rgba(212, 175, 55, 0.3)',
                      position: 'relative',
                      zIndex: 10
                    }}
                    onMouseEnter={(e) => {
                      if (totalPrice > 0) {
                        e.target.style.transform = 'translateY(-2px)';
                        e.target.style.boxShadow = '0 8px 25px rgba(212, 175, 55, 0.5)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.transform = 'translateY(0)';
                      e.target.style.boxShadow = '0 4px 15px rgba(212, 175, 55, 0.3)';
                    }}
                  >
                    {totalPrice === 0 ? translate("spaSelectZoneButton") : translate("spaBookButton")}
                  </button>
                </CardContent>
              </Card>
            );
          })()}
        </div>
      </section>

      {/* "SPA Paketi za posebne prilike" Section - SAMO 2 KARTICE */}
      <section style={{
        padding: '80px 20px 0 20px',
        maxWidth: '1400px',
        margin: '0 auto',
        borderTop: '1px solid rgba(212, 175, 55, 0.2)',
        background: 'transparent'
      }}>
        <div style={{
          textAlign: 'center',
          marginBottom: '60px'
        }}>
          <h2 style={{
            fontSize: 'clamp(2rem, 4vw, 3rem)',
            color: '#d4af37',
            marginBottom: '1rem',
            fontWeight: 'bold'
          }}>
            {translate("spaPackagesTitle")}
          </h2>
          <p style={{
            color: '#c0baa8',
            fontSize: '1.1rem',
            maxWidth: '700px',
            margin: '0 auto'
          }}>
            {translate("spaPackagesSubtitle")}
          </p>
        </div>

        {/* DVE VERTIKALNE KARTICE ZA PAROVE */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
          gap: '2.5rem',
          maxWidth: '1300px',
          margin: '0 auto 3rem',
          alignItems: 'stretch',
          justifyContent: 'center'
        }}>
          {/* Kartica 1: Romantični paket za parove */}
          <Card 
            className="spa-special-card romantic-card-special"
            style={{
              background: 'rgba(10, 10, 10, 0.65)',
              backdropFilter: 'blur(8px)',
              border: '1px solid rgba(212, 175, 55, 0.3)',
              borderRadius: '16px',
              overflow: 'hidden',
              transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
              position: 'relative',
              cursor: 'pointer',
              minHeight: '430px',
              maxWidth: '620px',
              width: '100%',
              display: 'flex',
              flexDirection: 'column'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#d4af37';
              e.currentTarget.style.transform = 'translateY(-8px)';
              e.currentTarget.style.boxShadow = '0 12px 32px rgba(212, 175, 55, 0.3)';
              const bg = e.currentTarget.querySelector('.romantic-card-background');
              if (bg) {
                bg.style.opacity = '0.4';
                bg.style.transform = 'scale(1.05)';
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'rgba(212, 175, 55, 0.3)';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
              const bg = e.currentTarget.querySelector('.romantic-card-background');
              if (bg) {
                bg.style.opacity = '0.25';
                bg.style.transform = 'scale(1)';
              }
            }}
          >
            {/* Background image - LEVA POLOVINA */}
            <div 
              className="romantic-card-background"
              style={{
                backgroundImage: 'url(https://customer-assets.emergentagent.com/job_thaibookingspa/artifacts/xhozz0qf_Romanticni%20paket%20za%20parove.jpg)',
                backgroundSize: 'cover',
                backgroundPosition: 'left center',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                opacity: 0.25,
                zIndex: 0,
                transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
              }}
            />
            
            <CardContent style={{ position: 'relative', zIndex: 1, padding: '2rem 1.5rem', display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
              {/* Content wrapper - uzima prostor */}
              <div style={{ flexGrow: 1 }}>
                {/* Header: Duration and Price - DYNAMIC from packageQuotes */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '0.5rem',
                  paddingBottom: '0.5rem',
                  borderBottom: '1px solid rgba(212, 175, 55, 0.2)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Clock size={16} color="#d4af37" />
                    <span style={{ color: '#f5f2e8', fontSize: '0.9rem', fontWeight: '600' }}>
                      210 min
                    </span>
                  </div>
                  {packageQuotes["ROMANTIC_COUPLE"]?.has_discount ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ textDecoration: 'line-through', opacity: 0.6, color: '#f5f2e8', fontSize: '0.9rem' }}>
                        {formatNumber(packageQuotes["ROMANTIC_COUPLE"].original_total)} RSD
                      </span>
                      <span style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#4ade80' }}>
                        {formatNumber(packageQuotes["ROMANTIC_COUPLE"].final_total)} RSD
                      </span>
                      <DiscountBadge percent={packageQuotes["ROMANTIC_COUPLE"].discount_percent || packageQuotes["ROMANTIC_COUPLE"].discount_percentage} size={20} />
                    </div>
                  ) : (
                    <div style={{
                      fontSize: '1.1rem',
                      fontWeight: 'bold',
                      color: '#d4af37'
                    }}>
                      {packageQuotes["ROMANTIC_COUPLE"]?.original_total ? `${formatNumber(packageQuotes["ROMANTIC_COUPLE"].original_total)} RSD` : '...'}
                    </div>
                  )}
                </div>

                {/* Naslov */}
                <h3 style={{
                  fontSize: '1.2rem',
                  color: '#d4af37',
                  marginBottom: '0.4rem',
                  fontWeight: 'bold'
                }}>
                  {translate("spaRomanticPackage")}
                </h3>
                
                {/* Kratak opis */}
                <p style={{
                  color: '#c0baa8',
                  marginBottom: '0.8rem',
                  fontSize: '0.85rem',
                  lineHeight: '1.4'
                }}>
                  {translate("spaRomanticPackageDesc")}
                </p>
                
                {/* Uključeno - lista */}
                <div style={{ marginBottom: '0.8rem' }}>
                  <h4 style={{
                    color: '#d4af37',
                    fontSize: '0.8rem',
                    marginBottom: '0.5rem',
                    fontWeight: '600'
                  }}>
                    {translate("spaIncluded")}
                  </h4>
                  <ul style={{
                    listStyle: 'none',
                    padding: 0,
                    margin: 0,
                    color: '#f5f2e8',
                    fontSize: '0.75rem',
                    lineHeight: '1.6'
                  }}>
                    <li style={{ marginBottom: '0.2rem', paddingLeft: '1rem', position: 'relative' }}>
                      <Sparkles size={9} color="#d4af37" style={{ position: 'absolute', left: 0, top: '4px' }} />
                      {translate("spaAromaMassage60")}
                    </li>
                    <li style={{ marginBottom: '0.2rem', paddingLeft: '1rem', position: 'relative' }}>
                      <Sparkles size={9} color="#d4af37" style={{ position: 'absolute', left: 0, top: '4px' }} />
                      {translate("spaFaceMassage60")}
                    </li>
                    <li style={{ marginBottom: '0.2rem', paddingLeft: '1rem', position: 'relative' }}>
                      <Sparkles size={9} color="#d4af37" style={{ position: 'absolute', left: 0, top: '4px' }} />
                      {translate("spaSauna")} – 30 min
                    </li>
                    <li style={{ marginBottom: '0.2rem', paddingLeft: '1rem', position: 'relative' }}>
                      <Sparkles size={9} color="#d4af37" style={{ position: 'absolute', left: 0, top: '4px' }} />
                      {translate("spaSteamBath")} – 30 min
                    </li>
                    <li style={{ marginBottom: '0.2rem', paddingLeft: '1rem', position: 'relative' }}>
                      <Sparkles size={9} color="#d4af37" style={{ position: 'absolute', left: 0, top: '4px' }} />
                      {translate("spaJacuzzi")} – 30 min
                    </li>
                    <li style={{ marginBottom: '0.2rem', paddingLeft: '1rem', position: 'relative' }}>
                      <Sparkles size={9} color="#d4af37" style={{ position: 'absolute', left: 0, top: '4px' }} />
                      {translate("spaChampagneFruit")}
                    </li>
                  </ul>
                </div>
              </div>
              
              {/* Actions section - pri dnu */}
              <div style={{ marginTop: '1.5rem' }}>
                {/* "Za dve osobe" box */}
                <div style={{
                  background: 'rgba(212, 175, 55, 0.1)',
                  padding: '0.5rem',
                  borderRadius: '6px',
                  marginBottom: '0.8rem',
                  border: '1px solid rgba(212, 175, 55, 0.2)',
                  textAlign: 'center'
                }}>
                  <span style={{
                    color: '#d4af37',
                    fontSize: '0.85rem',
                    fontWeight: '600',
                    textShadow: '0 0 8px rgba(212, 175, 55, 0.4)'
                  }}>
                    {translate("spaForTwoPeople")}
                  </span>
                </div>

                {/* Dugme "Zakažite" - FIX B: type="button" + spa_package_id */}
                <button
                type="button"
                onClick={() => {
                  console.log("[ROMANTIC_COUPLE_1] Book click");
                  const quote = packageQuotes["ROMANTIC_COUPLE"];
                  const originalPrice = quote?.original_total || 0;
                  const finalPrice = quote?.final_total || originalPrice;
                  const duration = quote?.total_duration || 180;
                  const hasDiscount = quote?.has_discount || false;
                  const discountPercent = quote?.discount_percent || quote?.discount_percentage || 0;
                  
                  const params = new URLSearchParams({
                    source: 'coupleSpecial',
                    spaCategory: 'SPA_SPECIAL_COUPLE',
                    spa_package_id: 'ROMANTIC_COUPLE_1',
                    card_id: 'romantic_couple_package',
                    spaName: translate("spaRomanticPackage"),
                    duration: String(duration),
                    price: String(originalPrice),
                    originalPrice: String(originalPrice),
                    finalPrice: String(finalPrice),
                    hasDiscount: String(hasDiscount),
                    discountPercent: String(discountPercent),
                    guests: '2'
                  });
                  navigate(`/contact?${params.toString()}`);
                }}
                style={{
                  width: '100%',
                  padding: '0.7rem',
                  background: 'linear-gradient(135deg, #d4af37 0%, #f4d03f 100%)',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#1a1a1a',
                  fontSize: '0.9rem',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 4px 15px rgba(212, 175, 55, 0.3)'
                }}
                onMouseEnter={(e) => {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 8px 25px rgba(212, 175, 55, 0.5)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 4px 15px rgba(212, 175, 55, 0.3)';
                }}
              >
                {translate("spaBookButton")}
              </button>
              </div>
            </CardContent>
          </Card>
          
          {/* Kartica 2: Romantični piling paket za parove - NOVA */}
          <Card 
            className="spa-special-card romantic-piling-card"
            style={{
              background: 'rgba(10, 10, 10, 0.65)',
              backdropFilter: 'blur(8px)',
              border: '1px solid rgba(212, 175, 55, 0.3)',
              borderRadius: '16px',
              overflow: 'hidden',
              transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
              position: 'relative',
              cursor: 'pointer',
              minHeight: '430px',
              maxWidth: '620px',
              width: '100%',
              display: 'flex',
              flexDirection: 'column'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#d4af37';
              e.currentTarget.style.transform = 'translateY(-8px)';
              e.currentTarget.style.boxShadow = '0 12px 32px rgba(212, 175, 55, 0.3)';
              const bg = e.currentTarget.querySelector('.romantic-piling-background');
              if (bg) {
                bg.style.opacity = '0.4';
                bg.style.transform = 'scale(1.05)';
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'rgba(212, 175, 55, 0.3)';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
              const bg = e.currentTarget.querySelector('.romantic-piling-background');
              if (bg) {
                bg.style.opacity = '0.25';
                bg.style.transform = 'scale(1)';
              }
            }}
          >
            {/* Background image - DESNA POLOVINA */}
            <div 
              className="romantic-piling-background"
              style={{
                backgroundImage: 'url(https://customer-assets.emergentagent.com/job_thaibookingspa/artifacts/xhozz0qf_Romanticni%20paket%20za%20parove.jpg)',
                backgroundSize: 'cover',
                backgroundPosition: 'right center',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                opacity: 0.25,
                zIndex: 0,
                transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
              }}
            />
            
            <CardContent style={{ position: 'relative', zIndex: 1, padding: '2rem 1.5rem', display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
              {/* Content wrapper - uzima prostor */}
              <div style={{ flexGrow: 1 }}>
                {/* Header: Duration and Price - DYNAMIC from packageQuotes */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '0.5rem',
                  paddingBottom: '0.5rem',
                  borderBottom: '1px solid rgba(212, 175, 55, 0.2)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Clock size={16} color="#d4af37" />
                    <span style={{ color: '#f5f2e8', fontSize: '0.9rem', fontWeight: '600' }}>
                      210 min
                    </span>
                  </div>
                  {packageQuotes["ROMANTIC_PEELING"]?.has_discount ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ textDecoration: 'line-through', opacity: 0.6, color: '#f5f2e8', fontSize: '0.9rem' }}>
                        {formatNumber(packageQuotes["ROMANTIC_PEELING"].original_total)} RSD
                      </span>
                      <span style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#4ade80' }}>
                        {formatNumber(packageQuotes["ROMANTIC_PEELING"].final_total)} RSD
                      </span>
                      <DiscountBadge percent={packageQuotes["ROMANTIC_PEELING"].discount_percent || packageQuotes["ROMANTIC_PEELING"].discount_percentage} size={20} />
                    </div>
                  ) : (
                    <div style={{
                      fontSize: '1.1rem',
                      fontWeight: 'bold',
                      color: '#d4af37'
                    }}>
                      {packageQuotes["ROMANTIC_PEELING"]?.original_total ? `${formatNumber(packageQuotes["ROMANTIC_PEELING"].original_total)} RSD` : '...'}
                    </div>
                  )}
                </div>

                {/* Naslov */}
                <h3 style={{
                  fontSize: '1.2rem',
                  color: '#d4af37',
                  marginBottom: '0.4rem',
                  fontWeight: 'bold'
                }}>
                  {translate("spaRomanticPeelingPackage")}
                </h3>
                
                {/* Kratak opis */}
                <p style={{
                  color: '#c0baa8',
                  marginBottom: '0.8rem',
                  fontSize: '0.85rem',
                  lineHeight: '1.4'
                }}>
                  {translate("spaRomanticPeelingDesc")}
                </p>
                
                {/* Uključeno - lista */}
                <div style={{ marginBottom: '0.8rem' }}>
                  <h4 style={{
                    color: '#d4af37',
                    fontSize: '0.8rem',
                    marginBottom: '0.5rem',
                    fontWeight: '600'
                  }}>
                    {translate("spaIncluded")}
                  </h4>
                  <ul style={{
                    listStyle: 'none',
                    padding: 0,
                    margin: 0,
                    color: '#f5f2e8',
                    fontSize: '0.75rem',
                    lineHeight: '1.6'
                  }}>
                    <li style={{ marginBottom: '0.2rem', paddingLeft: '1rem', position: 'relative' }}>
                      <Sparkles size={9} color="#d4af37" style={{ position: 'absolute', left: 0, top: '4px' }} />
                      {translate("spaBodyScrub60")}
                    </li>
                    <li style={{ marginBottom: '0.2rem', paddingLeft: '1rem', position: 'relative' }}>
                      <Sparkles size={9} color="#d4af37" style={{ position: 'absolute', left: 0, top: '4px' }} />
                      {translate("spaAromaMassage60")}
                    </li>
                    <li style={{ marginBottom: '0.2rem', paddingLeft: '1rem', position: 'relative' }}>
                      <Sparkles size={9} color="#d4af37" style={{ position: 'absolute', left: 0, top: '4px' }} />
                      {translate("spaSauna")} – 30 min
                    </li>
                    <li style={{ marginBottom: '0.2rem', paddingLeft: '1rem', position: 'relative' }}>
                      <Sparkles size={9} color="#d4af37" style={{ position: 'absolute', left: 0, top: '4px' }} />
                      {translate("spaSteamBath")} – 30 min
                    </li>
                    <li style={{ marginBottom: '0.2rem', paddingLeft: '1rem', position: 'relative' }}>
                      <Sparkles size={9} color="#d4af37" style={{ position: 'absolute', left: 0, top: '4px' }} />
                      {translate("spaJacuzzi")} – 30 min
                    </li>
                    <li style={{ marginBottom: '0.2rem', paddingLeft: '1rem', position: 'relative' }}>
                      <Sparkles size={9} color="#d4af37" style={{ position: 'absolute', left: 0, top: '4px' }} />
                      {translate("spaChampagneFruit")}
                    </li>
                  </ul>
                </div>
              </div>
              
              {/* Actions section - pri dnu */}
              <div style={{ marginTop: '1.5rem' }}>
                {/* "Za dve osobe" box */}
                <div style={{
                  background: 'rgba(212, 175, 55, 0.1)',
                  padding: '0.5rem',
                  borderRadius: '6px',
                  marginBottom: '0.8rem',
                  border: '1px solid rgba(212, 175, 55, 0.2)',
                  textAlign: 'center'
                }}>
                  <span style={{
                    color: '#d4af37',
                    fontSize: '0.85rem',
                    fontWeight: '600',
                    textShadow: '0 0 8px rgba(212, 175, 55, 0.4)'
                  }}>
                    {translate("spaForTwoPeople")}
                  </span>
                </div>

                {/* Dugme "Zakažite" - FIX B: type="button" + spa_package_id */}
                <button
                type="button"
                onClick={() => {
                  console.log("[ROMANTIC_COUPLE_2] Book click");
                  const quote = packageQuotes["ROMANTIC_PEELING"];
                  const originalPrice = quote?.original_total || 0;
                  const finalPrice = quote?.final_total || originalPrice;
                  const duration = quote?.total_duration || 150;
                  const hasDiscount = quote?.has_discount || false;
                  const discountPercent = quote?.discount_percent || quote?.discount_percentage || 0;
                  
                  const params = new URLSearchParams({
                    source: 'coupleSpecial',
                    spaCategory: 'SPA_SPECIAL_COUPLE',
                    spa_package_id: 'ROMANTIC_COUPLE_2',
                    card_id: 'romantic_peeling_couple_package',
                    spaName: translate("spaRomanticPeelingPackage"),
                    duration: String(duration),
                    price: String(originalPrice),
                    originalPrice: String(originalPrice),
                    finalPrice: String(finalPrice),
                    hasDiscount: String(hasDiscount),
                    discountPercent: String(discountPercent),
                    guests: '2'
                  });
                  navigate(`/contact?${params.toString()}`);
                }}
                style={{
                  width: '100%',
                  padding: '0.7rem',
                  background: 'linear-gradient(135deg, #d4af37 0%, #f4d03f 100%)',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#1a1a1a',
                  fontSize: '0.9rem',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 4px 15px rgba(212, 175, 55, 0.3)'
                }}
                onMouseEnter={(e) => {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 8px 25px rgba(212, 175, 55, 0.5)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 4px 15px rgba(212, 175, 55, 0.3)';
                }}
              >
                {translate("spaBookButton")}
              </button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Kartica "Devojačko veče & Lady Party" - NIŽA ALI SA CELIM SADRŽAJEM */}
        <div style={{
          maxWidth: '660px',
          width: '100%',
          margin: '100px auto 0 auto',
        }}>
          {/* Kartica 3: Devojačko veče & Lady Party - KOMPAKTNA 370px */}
          <Card 
            className="spa-special-card bridal-card-special"
            style={{
              background: 'rgba(10, 10, 10, 0.75)',
              backdropFilter: 'blur(8px)',
              border: '1px solid rgba(212, 175, 55, 0.85)',
              borderRadius: '24px',
              transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
              position: 'relative',
              cursor: 'pointer',
              width: '100%',
              minHeight: '370px',
              display: 'flex',
              flexDirection: 'column',
              padding: '1.2rem 2rem 1.3rem 2rem',
              boxShadow: '0 18px 40px rgba(0,0,0,0.65)',
              boxSizing: 'border-box'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#d4af37';
              e.currentTarget.style.transform = 'translateY(-8px)';
              e.currentTarget.style.boxShadow = '0 12px 32px rgba(212, 175, 55, 0.3)';
              const bg = e.currentTarget.querySelector('.bridal-card-background');
              if (bg) {
                bg.style.opacity = '0.5';
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'rgba(212, 175, 55, 0.8)';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
              const bg = e.currentTarget.querySelector('.bridal-card-background');
              if (bg) {
                bg.style.opacity = '0.3';
              }
            }}
          >
            {/* Background image - ISPUNJAVA CELU KARTICU */}
            <div 
              className="bridal-card-background"
              style={{
                backgroundImage: 'url(https://customer-assets.emergentagent.com/job_spa-cards-revamp/artifacts/03lls8bz_1022%20750.jpg)',
                backgroundSize: '100% 100%',
                backgroundPosition: 'center center',
                backgroundRepeat: 'no-repeat',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                opacity: 0.3,
                zIndex: 0,
                transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
              }}
            />
            
            <CardContent style={{ position: 'relative', zIndex: 1, padding: 0, display: 'flex', flexDirection: 'column', justifyContent: 'flex-start', flexGrow: 1 }}>
              {/* Content wrapper */}
              <div style={{ flexGrow: 1 }}>
                {/* Naslov - CENTRIRAN na vrhu kartice */}
                <h3 style={{
                  fontSize: '1.6rem',
                  fontWeight: 700,
                  color: '#ffd976',
                  textAlign: 'center',
                  width: '100%',
                  margin: '0 auto 0.7rem auto',
                  letterSpacing: '0.03em',
                  textShadow: '2px 2px 4px rgba(0, 0, 0, 0.85)'
                }}>
                  {translate("spaBacheloretteParty")}
                </h3>
                
                {/* Opis - samo leva polovina kartice */}
                <p style={{
                  maxWidth: '46%',
                  textAlign: 'left',
                  marginTop: '0.8rem',
                  marginBottom: '1.4rem',
                  marginLeft: '6%',
                  lineHeight: 1.45,
                  fontSize: '0.93rem',
                  color: '#f5f1e8',
                  textShadow: '2px 2px 4px rgba(0, 0, 0, 0.9)'
                }}>
                  {translate("spaBacheloretteDesc")}
                </p>
                
                {/* Uključeno - lista ispod opisa, takođe levo */}
                <div style={{
                  maxWidth: '50%',
                  marginLeft: '6%',
                  marginBottom: '1.6rem',
                  color: '#f5f1e8',
                  textShadow: '2px 2px 4px rgba(0, 0, 0, 0.9)',
                  fontSize: '0.88rem',
                  lineHeight: 1.5
                }}>
                  <h4 style={{
                    marginBottom: '0.8rem',
                    color: '#ffdf7a',
                    fontWeight: '600',
                    textShadow: '2px 2px 4px rgba(0, 0, 0, 0.85)'
                  }}>
                    {translate("spaIncluded")}
                  </h4>
                  <ul style={{
                    listStyle: 'none',
                    padding: 0,
                    margin: 0
                  }}>
                    <li style={{ marginBottom: '0.4rem', paddingLeft: '1.5rem', position: 'relative', textShadow: '2px 2px 4px rgba(0, 0, 0, 0.85)' }}>
                      <Sparkles size={12} color="#d4af37" style={{ position: 'absolute', left: 0, top: '5px' }} />
                      {translate("spaBachMassage")}
                    </li>
                    <li style={{ marginBottom: '0.4rem', paddingLeft: '1.5rem', position: 'relative', textShadow: '2px 2px 4px rgba(0, 0, 0, 0.85)' }}>
                      <Sparkles size={12} color="#d4af37" style={{ position: 'absolute', left: 0, top: '5px' }} />
                      {translate("spaBachSpaZone")}
                    </li>
                    <li style={{ marginBottom: '0.4rem', paddingLeft: '1.5rem', position: 'relative', textShadow: '2px 2px 4px rgba(0, 0, 0, 0.85)' }}>
                      <Sparkles size={12} color="#d4af37" style={{ position: 'absolute', left: 0, top: '5px' }} />
                      {translate("spaBachCocktailShow")}
                    </li>
                    <li style={{ marginBottom: '0.4rem', paddingLeft: '1.5rem', position: 'relative', textShadow: '2px 2px 4px rgba(0, 0, 0, 0.85)' }}>
                      <Sparkles size={12} color="#d4af37" style={{ position: 'absolute', left: 0, top: '5px' }} />
                      {translate("spaBachCatering")}
                    </li>
                    <li style={{ marginBottom: '0.4rem', paddingLeft: '1.5rem', position: 'relative', textShadow: '2px 2px 4px rgba(0, 0, 0, 0.85)' }}>
                      <Sparkles size={12} color="#d4af37" style={{ position: 'absolute', left: 0, top: '5px' }} />
                      {translate("spaBachCake")}
                    </li>
                    <li style={{ marginBottom: '0.4rem', paddingLeft: '1.5rem', position: 'relative', textShadow: '2px 2px 4px rgba(0, 0, 0, 0.85)' }}>
                      <Sparkles size={12} color="#d4af37" style={{ position: 'absolute', left: 0, top: '5px' }} />
                      {translate("spaBachDJ")}
                    </li>
                    <li style={{ marginBottom: '0.4rem', paddingLeft: '1.5rem', position: 'relative', textShadow: '2px 2px 4px rgba(0, 0, 0, 0.85)' }}>
                      <Sparkles size={12} color="#d4af37" style={{ position: 'absolute', left: 0, top: '5px' }} />
                      {translate("spaBachDecoration")}
                    </li>
                  </ul>
                </div>
              </div>
              
              {/* Actions section - pri dnu */}
              <div style={{ marginTop: '0.8rem' }}>
                {/* Dugme "POZOVITE" */}
                <a 
                  href="tel:062625500"
                  style={{
                    display: 'block',
                    width: '100%',
                    padding: '1rem',
                    background: 'linear-gradient(135deg, #d4af37 0%, #f4d03f 100%)',
                    border: 'none',
                    borderRadius: '10px',
                    color: '#1a1a1a',
                    fontSize: '1.1rem',
                    fontWeight: 'bold',
                    textAlign: 'center',
                    textDecoration: 'none',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    boxShadow: '0 4px 15px rgba(212, 175, 55, 0.3)',
                    marginBottom: '0.8rem'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 8px 25px rgba(212, 175, 55, 0.5)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = '0 4px 15px rgba(212, 175, 55, 0.3)';
                  }}
                >
                  {translate("spaBachCallButton")}
                </a>
                
                {/* Tekst ispod dugmeta */}
                <p style={{
                  color: '#c0baa8',
                  fontSize: '0.8rem',
                  textAlign: 'center',
                  fontStyle: 'italic',
                  lineHeight: '1.4',
                  textShadow: '2px 2px 4px rgba(0, 0, 0, 0.85)'
                }}>
                  {translate("spaBachDisclaimer")}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      </div> {/* End spa-parallax-content */}

      {/* CSS for luxury price button shine effect and page background */}
      <style>{`
        body {
          background: transparent !important;
        }
        
        .spa-page {
          background: transparent !important;
        }
        
        .spa-parallax-content {
          background: transparent !important;
        }
        
        .luxury-price-button {
          position: relative;
          overflow: hidden;
        }

        .luxury-price-button::before {
          content: '';
          position: absolute;
          top: -50%;
          left: -50%;
          width: 200%;
          height: 200%;
          background: linear-gradient(
            45deg,
            transparent,
            rgba(255, 255, 255, 0.3),
            transparent
          );
          transform: rotate(45deg);
          animation: shine 3s infinite;
        }

        @keyframes shine {
          0% {
            transform: translateX(-100%) translateY(-100%) rotate(45deg);
          }
          100% {
            transform: translateX(100%) translateY(100%) rotate(45deg);
          }
        }
      `}</style>
    </div>
  );
};

export default Spa;
