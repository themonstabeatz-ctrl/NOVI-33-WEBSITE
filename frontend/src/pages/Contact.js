import React, { useState, useEffect } from "react";
import { Helmet } from "react-helmet";
import { useLanguage } from "../context/LanguageContext";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { useToast } from "../hooks/use-toast";
import { Mail, Phone, MapPin, Clock, Instagram, Send, X, Calendar } from "lucide-react";
import { LOCKDOWN } from "../lockdown";
import { API_BASE } from "../config/api";

const EXPECTED = "BL_LOCK_2025_12_16";
if (LOCKDOWN.MASAZE_LOCKED && LOCKDOWN.LOCK_TOKEN !== EXPECTED) {
  throw new Error("LOCKDOWN VIOLATION: MASAŽE su zaključane.");
}
import { useLocation, useNavigate } from "react-router-dom";
import CustomCalendarModal from "../components/CustomCalendarModal";
import CustomTimePickerModal from "../components/CustomTimePickerModal";
import { getSEO } from "../utils/seoConfig";
import "react-datepicker/dist/react-datepicker.css";

const Contact = () => {
  const { translate, currentLanguage } = useLanguage();
  const language = currentLanguage; // Alias for backward compatibility
  const { toast } = useToast();
  const location = useLocation();
  const navigate = useNavigate(); // ✅ FIX: Added for redirect after booking success
  
  // Helper function to translate massage names
  const translateMassageName = (massageName) => {
    // Remove [PAROVI] prefix if present
    const cleanName = massageName.replace(/^\[PAROVI\]\s*/, '');
    
    // Remove duration suffix like " - 60 min", " - 90 min", etc.
    const nameWithoutDuration = cleanName.replace(/\s*-\s*\d+\s*min\s*$/i, '').trim();
    
    const nameMap = {
      'Tradicionalna tajlandska masaža': 'massageTraditionalThai',
      'Aroma terapija': 'massageAromaTherapy',
      'Masaža toplim uljem': 'massageHotOil',
      'Glava, vrat, ramena i leđa': 'massageHeadNeckShoulders',
      'Masaža stopala': 'massageFoot',
      'Aroma duboko tkivo': 'massageAromaDeepTissue',
      'Aromaterapija & topli kamen': 'massageAromaHotStone',
      'Aroma sa toplim biljnim kompresama': 'massageAromaThaiHerbal',
      'Thai masaža sa toplim biljnim kompresama': 'massageThaiHerbal',
      'Masaža za parove': 'couplesMassage'
    };
    
    const translationKey = nameMap[nameWithoutDuration];
    if (translationKey) {
      return translate(translationKey);
    }
    
    // If no mapping found, return original name
    return massageName;
  };
  
  // Helper function to check if service is couples massage (works in all languages)
  const isCouplesMassage = (serviceName) => {
    if (!serviceName) return false;
    
    // Couples massages have [PAROVI] prefix
    if (serviceName.includes('[PAROVI]')) {
      return true;
    }
    
    // Also check against language variations for backwards compatibility
    const couplesTranslations = [
      'Masaža za parove',           // Serbian
      'Couples Massage',             // English
      'Массаж для пар',              // Russian
      'นวดสำหรับคู่รัก'              // Thai
    ];
    
    return couplesTranslations.some(translation => 
      serviceName.includes(translation)
    );
  };

  // ✅ SPA HELPER: Format RSD price
  const formatRsd = (n) => {
    const x = Number(n || 0);
    return x.toLocaleString('sr-RS') + ' RSD';
  };

  // ✅ SPA FLOW: Check if this is SPA booking
  // ✅ FIX B: Added 'coupleSpecial' for Romantični paketi
  const getSpaFlowType = () => {
    const params = new URLSearchParams(location.search);
    const source = params.get('source');
    return ['spa', 'spaZone', 'spaSpecial', 'coupleSpecial'].includes(source) ? source : null;
  };

  // ✅ UX POLISH: Handle booking success - simple message, no redirect
  // State for secondary message (email confirmation)
  const [secondaryMessage, setSecondaryMessage] = useState("");
  
  const handleBookingSuccess = (bookingDetails = {}) => {
    const { bookingType, bookingId, responseData, notifyFailed } = bookingDetails;
    
    // ✅ SAMO JEDNA PORUKA - bez dodatnih tekstova
    const SUCCESS_MESSAGE = "USPEŠNO STE ZAKAZALI VAŠ TRETMAN";
    
    // Debug log (samo u console, ne u UI)
    console.log("✅ Booking success:", { bookingType, bookingId, notifyFailed, responseData });
    
    setSuccessMsg(SUCCESS_MESSAGE);
    setSubmitStatus("success");
    setIsSubmitting(false);
    
    // ✅ NEMA dodatnih poruka o email-u - samo console log
    if (notifyFailed || responseData?.notify_status === "failed") {
      console.log("⚠️ Email notification failed, but booking is confirmed");
    }
    
    // Ukloni secondaryMessage - samo jedna rečenica
    setSecondaryMessage("");
    
    // ✅ UX FIX B: Reset form (keep phone/email for convenience)
    setFormData(prev => ({
      ...prev,
      firstName: "",
      lastName: "",
      preferredDate: null,
      preferredTime: "",
      message: "",
    }));
    
    // ✅ UX A: NO AUTO REDIRECT - korisnik ostaje na strani
  };
  
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    phone: "",
    email: "",
    message: "",
    preferredDate: null, // Changed to null for DatePicker
    preferredTime: "",
    source: "message" // 'booking', 'voucher', 'message', or 'spa'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null); // 'success' or 'error'
  const [error, setError] = useState(null); // Error message state
  const submitTimeoutRef = React.useRef(null);
  
  // ✅ UX FIX: Success message with auto-hide and booking details
  const [successMsg, setSuccessMsg] = useState("");
  const [redirectCountdown, setRedirectCountdown] = useState(0);
  
  // ✅ UX FIX A: Auto-hide success message after 6 seconds
  useEffect(() => {
    if (!successMsg) return;
    const t = setTimeout(() => {
      setSuccessMsg("");
      setSubmitStatus(null);
    }, 6000);
    return () => clearTimeout(t);
  }, [successMsg]);
  
  // ✅ UX FIX: Countdown timer for redirect
  useEffect(() => {
    if (redirectCountdown <= 0) return;
    const t = setTimeout(() => setRedirectCountdown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [redirectCountdown]);
  
  // ✅ UX FIX: Redirect when countdown reaches 0
  useEffect(() => {
    if (redirectCountdown === 1) {
      navigate("/");
    }
  }, [redirectCountdown, navigate]);
  
  // SPA booking metadata
  const [spaBookingMeta, setSpaBookingMeta] = useState(null);
  
  // ✅ NEW: Pricing from /api/spa/quote (for SPA bookings)
  const [quotePricing, setQuotePricing] = useState(null);
  const [quotePricingLoading, setQuotePricingLoading] = useState(false);
  
  // ✅ UPDATE: When quotePricing arrives, update the message with correct price
  // ✅ FIX: Use translate() for ALL languages (SR, EN, RU, TH)
  useEffect(() => {
    if (!quotePricing || !spaBookingMeta) return;
    
    console.log("📊 BOOKING quote pricing received:", quotePricing);
    console.log("📊 BOOKING card_id:", spaBookingMeta.cardId);
    console.log("📊 BOOKING service_ids:", spaBookingMeta.serviceIds);
    
    // Build price lines from quote (the ONLY source of truth)
    const formatPrice = (n) => Number(n || 0).toLocaleString('sr-RS');
    let priceLines;
    
    if (quotePricing.has_discount) {
      // ✅ FIX: Use translate() for multi-language support
      priceLines = [
        `${translate("spaOriginalPrice")} ${formatPrice(quotePricing.original_total)} RSD`,
        `${translate("msgDiscount")} -${quotePricing.discount_percent}%`,
        `${translate("spaFinalPrice")} ${formatPrice(quotePricing.final_total)} RSD`
      ].join('\n');
    } else {
      priceLines = `${translate("spaTotalPrice")} ${formatPrice(quotePricing.final_total || quotePricing.original_total)} RSD`;
    }
    
    // Update message with correct pricing
    setFormData(prev => {
      if (!prev.message) return prev;
      
      // ✅ FIX: Regex that matches ALL language price labels (SR, EN, RU, TH)
      // Matches: "Ukupna cena:", "Total price:", "Общая цена:", "ราคารวม:", 
      //          "Originalna cena:", "Original price:", etc.
      const priceLineRegex = /(Ukupna cena:|Total price:|Общая цена:|ราคารวม:|Originalna cena:|Original price:|Оригинальная цена:|ราคาเดิม:|Popust:|Discount:|Скидка:|ส่วนลด:|Cena za naplatu:|Price to pay:|К оплате:|ราคาที่ต้องชำระ:).*$/gm;
      
      // Remove all existing price lines first
      let cleanedMessage = prev.message;
      let match;
      while ((match = priceLineRegex.exec(prev.message)) !== null) {
        cleanedMessage = cleanedMessage.replace(match[0], '');
      }
      
      // Remove empty lines at the end and add price lines
      cleanedMessage = cleanedMessage.replace(/\n+$/, '');
      const updatedMessage = cleanedMessage + '\n' + priceLines;
      
      console.log("📝 Updated booking message with quote price (translated):", priceLines);
      
      return {
        ...prev,
        message: updatedMessage
      };
    });
  }, [quotePricing, spaBookingMeta, translate]);
  
  // Dynamic service mapping from booking system
  const [serviceMapping, setServiceMapping] = useState({});
  const [servicesLoaded, setServicesLoaded] = useState(false);
  const [availableServices, setAvailableServices] = useState({ single: [], couples: [] });

  // ✅ SPA FLOW: Auto-populate message for SPA bookings
  useEffect(() => {
    const spaFlow = getSpaFlowType();
    if (!spaFlow) return;

    const p = new URLSearchParams(location.search);
    const name = p.get('spaName') || p.get('spaPackageName') || 'SPA';
    const duration = p.get('duration') || p.get('totalMinutes') || '';
    const price = p.get('price') || p.get('totalPrice') || '';
    const spaZoneItems = p.get('spaZoneItems') || p.get('spaZoneLabel') || '';

    let lines = [];
    
    if (spaFlow === 'spaZone') {
      lines.push('SPA Zona rezervacija');
      if (spaZoneItems) lines.push(`Zone: ${decodeURIComponent(spaZoneItems)}`);
    } else if (spaFlow === 'spaSpecial') {
      lines.push(`Poseban SPA paket: ${decodeURIComponent(name)}`);
    } else {
      lines.push(`SPA paket: ${decodeURIComponent(name)}`);
    }
    
    if (duration) lines.push(`Ukupno trajanje: ${duration} min`);
    if (price) lines.push(`Ukupna cena: ${formatRsd(price)}`);

    setFormData(prev => ({
      ...prev,
      message: lines.join('\n'),
      source: spaFlow
    }));

    console.log('✅ SPA FLOW detected:', spaFlow, { name, duration, price });
  }, [location.search]);

  // Load services from booking system on mount (ONLY for non-SPA flow)
  useEffect(() => {
    const loadServices = async () => {
      // ✅ SPA GUARD: Don't load massage services for SPA flow
      const spaFlow = getSpaFlowType();
      if (spaFlow) {
        console.log('🛡️ SPA FLOW - skipping massage API calls');
        setServicesLoaded(true);
        return;
      }

      try {
        const backendUrlRaw = API_BASE;
        
        if (!backendUrlRaw) {
          throw new Error('❌ API_BASE IS NOT DEFINED (check config/api.js)');
        }
        
        const backendUrl = backendUrlRaw.replace(/\/$/, '');
        console.log('📍 Loading services from Contact page:', backendUrl);

        const [singleResponse, couplesResponse] = await Promise.all([
          fetch(`${backendUrl}/api/services/single/list`),
          fetch(`${backendUrl}/api/services/couples/list`)
        ]);
        
        // ✅ FIX: Read body only once to avoid "body stream already read"
        const singleRaw = await singleResponse.text();
        const couplesRaw = await couplesResponse.text();
        
        let singleServices = [];
        let couplesServices = [];
        
        try {
          singleServices = singleRaw ? JSON.parse(singleRaw) : [];
        } catch {
          console.error('❌ Failed to parse single services JSON:', singleRaw);
        }
        
        try {
          couplesServices = couplesRaw ? JSON.parse(couplesRaw) : [];
        } catch {
          console.error('❌ Failed to parse couples services JSON:', couplesRaw);
        }
        
        // Combine all services
        const allServices = [...singleServices, ...couplesServices];
        
        // Build service mapping: "Service Name - Duration" -> ID
        // Store both exact name AND normalized name for flexible matching
        const mapping = {};
        allServices.forEach(service => {
          // Store with exact name
          mapping[service.name] = service.id;
          
          // Also store with normalized name (without duration, trimmed)
          const normalized = service.name
            .replace(/\s*[-–—]\s*\d+\s*min\s*$/i, '') // Remove "- 60 min", "– 90 min", etc.
            .trim();
          
          // Don't overwrite if normalized name already exists (keep first match)
          if (!mapping[normalized] || mapping[normalized] === service.id) {
            mapping[normalized] = service.id;
          }
          
          console.log(`   📝 Mapped: "${service.name}" -> ${service.id.substring(0, 8)}...`);
          if (service.name !== normalized) {
            console.log(`      Also: "${normalized}" -> ${service.id.substring(0, 8)}...`);
          }
        });
        
        console.log('✅ Loaded service mapping:', Object.keys(mapping).length, 'keys for', allServices.length, 'services');
        console.log('   Single:', singleServices.length, 'Couples:', couplesServices.length);
        setServiceMapping(mapping);
        setAvailableServices({ single: singleServices, couples: couplesServices });
        setServicesLoaded(true);
      } catch (error) {
        console.error('❌ Failed to load services from booking system:', error);
        setServicesLoaded(true); // Set to true anyway to prevent blocking
      }
    };
    
    loadServices();
  }, []);

  // Safety: Reset isSubmitting on component mount to prevent stuck disabled state
  useEffect(() => {
    setIsSubmitting(false);
    return () => {
      if (submitTimeoutRef.current) {
        clearTimeout(submitTimeoutRef.current);
      }
    };
  }, []);

  // Map language codes to HTML lang attribute - force sr-RS for date format
  const getHtmlLang = () => {
    // Always use sr-RS for Serbian date format (DD.MM.YYYY)
    return 'sr-RS';
  };

  // Set HTML lang attribute for native date picker localization
  useEffect(() => {
    document.documentElement.lang = getHtmlLang();
  }, [language]);

  // Scroll to top when component mounts and check for service parameter
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Get service parameter from URL
    const searchParams = new URLSearchParams(location.search);
    const service = searchParams.get('service');
    const source = searchParams.get('source'); // 'voucher', 'massage', 'spa', or null
    const couplesData = searchParams.get('couplesData');
    
    // SPA BOOKING – URL format:
    // /contact?source=spa&spaCategory=...&spaPackageId=...&spaName=...&duration=...&price=...
    // ✅ FIX B: Added "coupleSpecial" for Romantični paketi
    if (source === "spa" || source === "spaSpecial" || source === "spaZone" || source === "coupleSpecial") {
      const spaCategory    = searchParams.get("spaCategory") || "SPA";
      const spaPackageId   = searchParams.get("spaPackageId");
      const spa_package_id = searchParams.get("spa_package_id"); // For coupleSpecial
      const spaName        = searchParams.get("spaName") || searchParams.get("spaPackageName") || "SPA";
      const variantId      = searchParams.get("variantId");
      const variantLabel   = searchParams.get("variantLabel");
      const spaZoneLabel   = searchParams.get("spaZoneLabel");
      const guests         = Number(searchParams.get("guests") || 1);
      
      // ✅ NEW: Card ID and Service IDs for card-level discounts
      const cardId         = searchParams.get("card_id") || "";
      const serviceIds     = searchParams.get("service_ids") || "";
      
      // New detailed params
      const basePrice      = Number(searchParams.get("basePrice") || 0);
      const baseDuration   = Number(searchParams.get("baseDuration") || 0);
      const face           = searchParams.get("face") === "1";
      const saunaMin       = Number(searchParams.get("sauna") || 0);
      const steamMin       = Number(searchParams.get("steam") || 0);
      const jacuzziMin     = Number(searchParams.get("jacuzzi") || 0);
      const addonPrice     = Number(searchParams.get("addonPrice") || 0);
      const addonDuration  = Number(searchParams.get("addonDuration") || 0);
      const totalPrice     = Number(searchParams.get("totalPrice") || searchParams.get("price") || 0);
      const totalDuration  = Number(searchParams.get("totalDuration") || searchParams.get("totalMinutes") || searchParams.get("duration") || 0);
      
      // ✅ NEW: Original and final prices from Spa.js (for Herbal packages)
      const originalPrice  = Number(searchParams.get("originalPrice") || totalPrice || 0);
      const finalPrice     = Number(searchParams.get("finalPrice") || totalPrice || 0);
      const hasDiscount    = searchParams.get("hasDiscount") === "true";
      const discountPercent = Number(searchParams.get("discountPercent") || 0);

      // Format prices for sr-RS
      const formatRsdLocal = (n) => Number(n || 0).toLocaleString("sr-RS");

      console.log('🔍 SPA booking detected:', { 
        source, spaCategory, spaPackageId, spa_package_id, spaName, variantLabel, 
        face, saunaMin, steamMin, jacuzziMin, guests,
        basePrice, addonPrice, totalPrice, totalDuration,
        cardId, serviceIds // ✅ Log card_id and service_ids
      });

      // 1) Save all SPA metadata (for handleSubmit)
      setSpaBookingMeta({
        source,
        spaCategory,
        spaPackageId,
        spa_package_id, // For coupleSpecial
        spaName,
        variantId,
        variantLabel,
        spaZoneLabel,
        face,
        saunaMin,
        steamMin,
        jacuzziMin,
        guests,
        basePrice,
        baseDuration,
        addonPrice,
        addonDuration,
        totalPrice,
        totalDuration,
        // ✅ NEW: Original and final prices from URL params (for Herbal packages)
        originalPrice,
        finalPrice,
        hasDiscount,
        discountPercent,
        // ✅ Card ID and Service IDs
        cardId,
        serviceIds: serviceIds ? serviceIds.split(",") : []
      });

      // ✅ NEW: Fetch quote pricing from backend (if we have card_id and service_ids)
      // Use IIFE to handle async inside useEffect
      if (cardId && serviceIds) {
        const serviceIdArray = serviceIds.split(",").filter(Boolean);
        if (serviceIdArray.length > 0) {
          (async () => {
            setQuotePricingLoading(true);
            try {
              const quoteRes = await fetch(`${API_BASE}/api/spa/quote`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                cache: "no-store",
                body: JSON.stringify({ service_ids: serviceIdArray, card_id: cardId })
              });
              if (quoteRes.ok) {
                const quoteData = await quoteRes.json();
                const discountPct = Number(quoteData.discount_percent ?? quoteData.discount_percentage ?? 0);
                setQuotePricing({
                  original_total: Number(quoteData.original_total || 0),
                  final_total: Number(quoteData.final_total || quoteData.original_total || 0),
                  discount_percent: discountPct,
                  has_discount: discountPct > 0
                });
                console.log("📊 Contact page quote pricing:", quoteData);
              }
            } catch (err) {
              console.error("❌ Failed to fetch quote pricing:", err);
            } finally {
              setQuotePricingLoading(false);
            }
          })();
        }
      }

      // 2) Pre-populate form message with detailed breakdown
      let messageLines = [];
      
      // ✅ Get additional params for different SPA categories
      const includedSpaZone = searchParams.get("includedSpaZone");
      const selectedSpaZones = searchParams.get("selectedSpaZones");
      
      // ✅ FIX B: Handle coupleSpecial (Romantični paketi za parove)
      if (source === "coupleSpecial" || spaCategory === "SPA_SPECIAL_COUPLE") {
        messageLines.push(translate("msgRomanticSpaCouple"));
        messageLines.push(`${translate("msgPackage")} ${decodeURIComponent(spaName)}`);
        messageLines.push(translate("msgForPersons"));
      } else if (source === "spaSpecial") {
        messageLines.push(`${translate("msgSpecialSpaPackage")} ${decodeURIComponent(spaName)}`);
      } else if (source === "spaZone") {
        // ✅ SPA ZONE ONLY - show selected zones
        messageLines.push(translate("msgSpaZoneOnly"));
        if (selectedSpaZones) {
          const zones = selectedSpaZones.split("|");
          messageLines.push(translate("msgSelectedZones"));
          zones.forEach(zone => {
            // Translate zone names from Serbian to current language
            let translatedZone = zone;
            if (zone.includes("Sauna")) translatedZone = zone.replace("Sauna", translate("spaSauna"));
            if (zone.includes("Parno kupatilo")) translatedZone = zone.replace("Parno kupatilo", translate("spaSteamBath"));
            if (zone.includes("Jacuzzi")) translatedZone = zone.replace("Jacuzzi", translate("spaJacuzzi"));
            messageLines.push(`  • ${translatedZone}`);
          });
        } else if (spaZoneLabel && spaZoneLabel !== "Bez SPA zona") {
          messageLines.push(`${translate("msgSelectedZones")} ${spaZoneLabel}`);
        }
      } else if (spaCategory === "SPA_HERBAL") {
        // ✅ HERBAL packages - show included SPA zone
        messageLines.push(`${translate("msgSpaPackage")} ${decodeURIComponent(spaName)}`);
        
        // Show included SPA zone (doesn't affect price)
        if (includedSpaZone && includedSpaZone !== "none") {
          let zoneName = translate("spaWithout");
          if (includedSpaZone === "sauna15") zoneName = translate("spaSauna15");
          if (includedSpaZone === "steam15") zoneName = translate("spaSteamBath15");
          messageLines.push(`${translate("msgSpaZoneIncluded")} ${zoneName}`);
        } else {
          messageLines.push(`${translate("msgSpaZone")} ${translate("spaWithout")}`);
        }
      } else {
        // Regular SPA Ritual
        messageLines.push(`${translate("msgSpaPackage")} ${decodeURIComponent(spaName)}`);
        
        // Variant (face massage)
        if (variantLabel) {
          const variantText = face 
            ? translate("msgWithFaceMassage")
            : translate("msgWithoutFaceMassage");
          messageLines.push(`${translate("msgVariant")} ${variantText}`);
        }

        // SPA Zone breakdown (only for regular rituals, not HERBAL)
        if (saunaMin > 0 || steamMin > 0 || jacuzziMin > 0) {
          messageLines.push(`${translate("msgSpaZone")}`);
          if (saunaMin > 0) messageLines.push(`  • ${translate("msgSauna")} ${saunaMin} min`);
          if (steamMin > 0) messageLines.push(`  • ${translate("msgSteamBath")} ${steamMin} min`);
          if (jacuzziMin > 0) messageLines.push(`  • ${translate("msgJacuzzi")} ${jacuzziMin} min`);
        } else if (spaZoneLabel && spaZoneLabel !== "Bez SPA zona") {
          messageLines.push(`${translate("msgSpaZone")} ${spaZoneLabel}`);
        }
      }

      // Totals
      messageLines.push('');
      messageLines.push(`${translate("spaTotalDuration")} ${totalDuration} min`);
      
      // ✅ Show discount pricing for coupleSpecial and other SPA packages
      if (hasDiscount && discountPercent > 0 && finalPrice < originalPrice) {
        messageLines.push(`${translate("spaOriginalPrice")} ${formatRsdLocal(originalPrice)} RSD`);
        messageLines.push(`${translate("msgDiscount")} -${discountPercent}%`);
        messageLines.push(`${translate("spaFinalPrice")} ${formatRsdLocal(finalPrice)} RSD`);
      } else {
        messageLines.push(`${translate("spaTotalPrice")} ${formatRsdLocal(originalPrice || totalPrice)} RSD`);
      }

      const message = messageLines.join('\n');

      setFormData(prev => ({
        ...prev,
        serviceName: `SPA: ${decodeURIComponent(spaName)}${variantLabel ? ` (${decodeURIComponent(variantLabel)})` : ''}`,
        message: message,
        source: source
      }));

      console.log('✅ SPA form pre-populated with detailed breakdown');
      return; // Exit early, don't process regular service logic
    }
    
    if (service) {
      // Translate the service name
      const translatedService = translateMassageName(service);
      
      // ✅ NEW: Get detailed localized data from URL params
      const localizedName = searchParams.get('localizedName');
      const localizedDesc = searchParams.get('localizedDesc');
      const localizedBenefits = searchParams.get('localizedBenefits');
      const durationFromUrl = searchParams.get('duration');
      const lang = searchParams.get('lang') || 'sr';
      
      // Store language for backend
      setFormData(prev => ({ ...prev, lang: lang }));
      
      // Build detailed message based on whether we have localized data
      let message = '';
      
      if (localizedName && !couplesData) {
        // ✅ NEW: Detailed localized message for single massages
        const durationLabel = {
          'sr': 'Trajanje',
          'en': 'Duration',
          'ru': 'Продолжительность',
          'th': 'ระยะเวลา'
        }[lang] || 'Trajanje';
        
        const descLabel = {
          'sr': 'Opis',
          'en': 'Description',
          'ru': 'Описание',
          'th': 'รายละเอียด'
        }[lang] || 'Opis';
        
        const benefitsLabel = {
          'sr': 'Benefiti',
          'en': 'Benefits',
          'ru': 'Преимущества',
          'th': 'ประโยชน์'
        }[lang] || 'Benefiti';
        
        const minLabel = {
          'sr': 'min',
          'en': 'min',
          'ru': 'мин',
          'th': 'นาที'
        }[lang] || 'min';
        
        // ✅ NEW 2025-01-09: Pricing labels for regular massages
        const priceLabel = {
          'sr': 'Cena',
          'en': 'Price',
          'ru': 'Цена',
          'th': 'ราคา'
        }[lang] || 'Cena';
        
        const discountLabel = {
          'sr': 'Popust',
          'en': 'Discount',
          'ru': 'Скидка',
          'th': 'ส่วนลด'
        }[lang] || 'Popust';
        
        const originalPriceLabel = {
          'sr': 'Originalna cena',
          'en': 'Original price',
          'ru': 'Исходная цена',
          'th': 'ราคาเดิม'
        }[lang] || 'Originalna cena';
        
        const discountedPriceLabel = {
          'sr': 'Cena sa popustom',
          'en': 'Price with discount',
          'ru': 'Цена со скидкой',
          'th': 'ราคาหลังหักส่วนลด'
        }[lang] || 'Cena sa popustom';
        
        // ✅ NEW 2025-01-09: Get pricing from URL params
        const originalPrice = parseInt(searchParams.get('originalPrice') || '0', 10);
        const finalPrice = parseInt(searchParams.get('finalPrice') || '0', 10);
        const discountPercent = parseInt(searchParams.get('discountPercent') || '0', 10);
        const hasDiscount = searchParams.get('hasDiscount') === 'true';
        
        // Helper to format price
        const formatPrice = (n) => new Intl.NumberFormat('sr-RS').format(Math.round(Number(n)));
        
        message = `${translate('youSelected')} ${decodeURIComponent(localizedName)}\n\n`;
        
        if (durationFromUrl) {
          message += `${durationLabel}: ${durationFromUrl} ${minLabel}\n`;
        }
        
        // ✅ NEW 2025-01-09: Add pricing info to message
        if (hasDiscount && discountPercent > 0 && originalPrice > 0) {
          message += `\n${discountLabel}: -${discountPercent}%\n`;
          message += `${originalPriceLabel}: ${formatPrice(originalPrice)} RSD\n`;
          message += `${discountedPriceLabel}: ${formatPrice(finalPrice)} RSD\n`;
        } else if (finalPrice > 0) {
          message += `\n${priceLabel}: ${formatPrice(finalPrice)} RSD\n`;
        } else if (originalPrice > 0) {
          message += `\n${priceLabel}: ${formatPrice(originalPrice)} RSD\n`;
        }
        
        if (localizedDesc) {
          message += `\n${descLabel}:\n${decodeURIComponent(localizedDesc)}\n`;
        }
        
        if (localizedBenefits) {
          message += `\n${benefitsLabel}:\n${decodeURIComponent(localizedBenefits)}`;
        }
        
        console.log('📝 Detailed localized massage message generated');
        console.log('📝 Language:', lang);
        console.log('📝 Pricing:', { originalPrice, finalPrice, discountPercent, hasDiscount });
      } else {
        // Fallback to simple message
        message = `${translate('youSelected')} ${translatedService}`;
      }
      
      console.log('🔍 Contact page - service:', service);
      console.log('🔍 Contact page - couplesData param:', couplesData);
      
      // Special handling for couples massage
      if (couplesData) {
        try {
          // Try to decode, but if it fails, use the raw string
          let decodedData = couplesData;
          try {
            decodedData = decodeURIComponent(couplesData);
          } catch (decodeError) {
            console.warn('⚠️ Could not decode URI, using raw string:', decodeError);
          }
          
          const data = JSON.parse(decodedData);
          console.log('✅ Parsed couples data:', data);
          
          // ✅ Build message using ARRAYS (person1_services, person2_services)
          message = `${translate('couplesMassageBooking')}\n\n`;
          
          // Person 1 - show ALL services
          const p1Services = data.person1_services || (data.person1 ? [data.person1] : []);
          message += `${translate('person1')}:\n`;
          p1Services.forEach(s => {
            const translatedMassage = translateMassageName(s.name);
            message += `  • ${translatedMassage} (${s.duration} min)\n`;
          });
          
          // Person 2 - show ALL services
          const p2Services = data.person2_services || (data.person2 ? [data.person2] : []);
          message += `\n${translate('person2')}:\n`;
          p2Services.forEach(s => {
            const translatedMassage = translateMassageName(s.name);
            message += `  • ${translatedMassage} (${s.duration} min)\n`;
          });
          
          // ✅ Use new couplesData structure (pair_discount_percentage, pair_original_price, pair_final_price)
          const discountText = data.pair_discount_percentage 
            ? `${data.pair_discount_percentage}%` 
            : (data.discount || 'N/A');
          const originalPriceValue = data.pair_original_price || data.originalPrice || 0;
          const finalPriceValue = data.pair_final_price || data.totalPrice || 0;
          
          message += `\n${translate('discount')}: ${discountText}\n`;
          message += `${translate('originalPrice')}: ${originalPriceValue.toLocaleString()} RSD\n`;
          message += `${translate('priceWithDiscount')}: ${finalPriceValue.toLocaleString()} RSD`;
          
          console.log('📝 Final message:', message);
        } catch (e) {
          console.error('❌ Error parsing couples data:', e);
        }
      } else if (isCouplesMassage(service)) {
        console.log('⚠️ Couples service but no couplesData param - checking for service in name');
      }
      
      setFormData(prev => ({
        ...prev,
        message: message,
        source: source || 'booking' // Store source for success message
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        source: source || 'message' // Default to message if no service
      }));
    }
  }, [location, translate, language]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    console.log(`🔄 handleInputChange: ${name} = ${value}`);
    console.log(`🔄 Event object:`, { name, value, targetType: typeof e.target });
    
    setFormData(prev => {
      const updated = {
        ...prev,
        [name]: value
      };
      console.log(`🔄 Updated formData after ${name} change:`, updated);
      return updated;
    });
  };

  // Handle date change from DatePicker
  const handleDateChange = (date) => {
    console.log('📅 handleDateChange called with:', date, 'Type:', typeof date);
    console.log('📅 Date details:', { 
      isDate: date instanceof Date, 
      value: date, 
      toString: date ? date.toString() : 'null' 
    });
    
    // Ensure we're getting a valid date or null
    const dateValue = date instanceof Date ? date : null;
    
    setFormData(prev => {
      const updated = {
        ...prev,
        preferredDate: dateValue
      };
      console.log('📅 Updated formData.preferredDate:', updated.preferredDate);
      console.log('📅 Full formData after date change:', updated);
      return updated;
    });
    
    // Log after state update (with slight delay to see updated state)
    setTimeout(() => {
      console.log('📅 formData.preferredDate after setState (check):', formData.preferredDate);
    }, 100);
  };

  const clearDate = () => {
    setFormData(prev => ({
      ...prev,
      preferredDate: null
    }));
  };

  const clearTime = () => {
    setFormData(prev => ({
      ...prev,
      preferredTime: ""
    }));
  };

  // Format date for display as DD/MM/YYYY
  const formatDateForDisplay = (isoDate) => {
    if (!isoDate) return '';
    const [year, month, day] = isoDate.split('-');
    return `${day}/${month}/${year}`;
  };

  // Format date as DD/MM/YYYY
  const formatDate = (dateString) => {
    if (!dateString) return 'Nije navedeno';
    const date = new Date(dateString + 'T00:00:00');
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
  };

  // 🔒 DO NOT MODIFY — STABLE VERIFIED BOOKING LOGIC (Bua Luang - SNAPSHOT: BuaLuang-FRONTEND-STABLE-01)
  // This handleSubmit function works correctly with backend /api/book-appointment
  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('🚀 handleSubmit called!');
    console.log('📍 Backend URL is:', API_BASE);
    
    // 🔒 HARD LOCK: API_BASE validated in config/api.js (throws if invalid)
    console.log(`✅ API_BASE (hard locked):`, API_BASE);
    
    setIsSubmitting(true);
    setSubmitStatus(null);
    
    // Safety timeout: Auto-reset after 30 seconds if stuck
    submitTimeoutRef.current = setTimeout(() => {
      console.warn('⚠️ Submit timeout - resetting isSubmitting');
      setIsSubmitting(false);
    }, 30000);
    
    try {
      console.log('✅ Entered try block');
      console.log('📋 Form data:', { 
        firstName: formData.firstName, 
        lastName: formData.lastName,
        phone: formData.phone,
        email: formData.email,
        preferredDate: formData.preferredDate,
        preferredTime: formData.preferredTime
      });
      
      // Validate required fields with detailed error messages
      const missingFields = [];
      
      if (!formData.firstName) missingFields.push('firstName');
      if (!formData.lastName) missingFields.push('lastName');
      if (!formData.phone) missingFields.push('phone');
      if (!formData.email) missingFields.push('email');
      
      // Check if this is a booking (has service parameter)
      const queryParams = new URLSearchParams(location.search);
      const serviceName = queryParams.get('service') || formData.service || '';
      const isBooking = !!serviceName;
      
      console.log('🔍 Booking check:', { serviceName, isBooking });
      
      // For bookings, date and time are required
      if (isBooking) {
        if (!formData.preferredDate) missingFields.push('date');
        if (!formData.preferredTime) missingFields.push('time');
      }
      
      console.log('⚠️ Missing fields:', missingFields);
      
      // If there are missing fields, show error and scroll to first missing field
      if (missingFields.length > 0) {
        // Create error message based on missing fields
        let errorMessage = translate('fillAllFields') || 'Molimo popunite sva obavezna polja: ';
        const fieldNames = {
          firstName: translate('firstName') || 'Ime',
          lastName: translate('lastName') || 'Prezime',
          phone: translate('phone') || 'Telefon',
          email: translate('email') || 'Email',
          date: translate('selectDate') || 'Datum',
          time: translate('selectTime') || 'Vreme'
        };
        
        const missingFieldNames = missingFields.map(field => fieldNames[field]);
        errorMessage += missingFieldNames.join(', ');
        
        // Show error toast
        toast({
          title: translate('error') || 'Greška',
          description: errorMessage,
          variant: "destructive",
        });
        
        // Scroll to first missing field
        const firstMissingField = missingFields[0];
        let fieldElement = null;
        
        if (firstMissingField === 'date') {
          fieldElement = document.querySelector('.calendar-input-trigger');
        } else if (firstMissingField === 'time') {
          fieldElement = document.querySelector('.time-input-trigger');
        } else {
          fieldElement = document.querySelector(`input[name="${firstMissingField}"]`);
        }
        
        if (fieldElement) {
          fieldElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
          // Add visual indication (red border)
          fieldElement.style.border = '2px solid #dc2626';
          fieldElement.style.animation = 'shake 0.5s';
          
          // Remove red border after 3 seconds
          setTimeout(() => {
            fieldElement.style.border = '';
            fieldElement.style.animation = '';
          }, 3000);
        }
        
        setIsSubmitting(false);
        return;
      }
      
      // ✅ FIX B: SPA SPECIAL COUPLE (Romantični paketi za parove) - direktan POST bez service mapping
      if (formData.source === "coupleSpecial" && spaBookingMeta?.spaCategory === "SPA_SPECIAL_COUPLE") {
        console.log("🚀 SPA SPECIAL COUPLE handleSubmit called!");
        console.log("🔍 spaBookingMeta:", spaBookingMeta);
        
        const bookingEndpoint = `${API_BASE}/api/spa/appointments`;
        
        // Convert Date object to YYYY-MM-DD format
        let dateStr;
        if (formData.preferredDate instanceof Date) {
          const year = formData.preferredDate.getFullYear();
          const month = String(formData.preferredDate.getMonth() + 1).padStart(2, '0');
          const day = String(formData.preferredDate.getDate()).padStart(2, '0');
          dateStr = `${year}-${month}-${day}`;
        } else {
          dateStr = formData.preferredDate;
        }
        
        const payload = {
          // ✅ A) Client info - OBAVEZNO za email
          client_first_name: formData.firstName,
          client_last_name: formData.lastName,
          client_phone: formData.phone,
          client_email: formData.email,
          
          // ✅ Appointment details
          appointment_date: dateStr,
          start_time: `${dateStr}T${formData.preferredTime}:00`,
          
          // ✅ Type - za backend template selection
          type: "spa",
          spa_category: "spa_special_couple",
          
          // ✅ Service details - za email template
          // MASTER: Koristi tačan naziv paketa SA UKUPNIM TRAJANJEM
          spa_package_id: spaBookingMeta.spa_package_id || spaBookingMeta.spaPackageId,
          service_name: `${spaBookingMeta.spaName} - ${spaBookingMeta.totalDuration} min`,
          service_description: "Romantični SPA paket za parove",
          
          // ✅ Duration & guests - MASTER: Koristi totalDuration iz URL params
          guests: 2,
          duration: spaBookingMeta.totalDuration || 0,
          duration_min: spaBookingMeta.totalDuration || 0,
          total_duration: spaBookingMeta.totalDuration || 0,
          
          // ✅ Notes - UVEK uključi srpski format za backend parsiranje
          notes: formData.message + `\n\n--- BACKEND DATA (SR) ---\nRomantični SPA paket: ${spaBookingMeta.spaName}\nBroj gostiju: 2\nUkupno trajanje: ${spaBookingMeta.totalDuration} min\nUkupna cena: ${spaBookingMeta.totalPrice} RSD`,
          
          // ✅ CARD ID & SERVICE IDs - backend računa popust sam
          card_id: spaBookingMeta.cardId || spaBookingMeta.spa_package_id || "",
          service_ids: spaBookingMeta.serviceIds || [],
          
          // ✅ SAMO ORIGINALNA CENA - backend računa popust!
          // NE SLATI final_price ili discount_percentage
          total_original: quotePricing?.original_total || spaBookingMeta.totalPrice || 0,
          
          // ✅ Language for backend email template
          lang: formData.lang || language || 'sr'
        };
        
        console.log("📦 SPA SPECIAL COUPLE payload:", payload);
        
        // ✅ A) FIX: Ne čitati response dva puta + pravi error handling
        let coupleSpecialResult = null;
        try {
          const response = await fetch(bookingEndpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          
          // Read response body ONCE as text
          const text = await response.text();
          
          // Parse JSON safely
          try { 
            coupleSpecialResult = text ? JSON.parse(text) : null; 
          } catch { 
            coupleSpecialResult = { raw: text }; 
          }
          
          console.log("📥 SPA SPECIAL COUPLE response:", response.status, coupleSpecialResult);
          
          if (!response.ok) {
            if (response.status === 404) {
              setError("⚠️ Backend nema SPA booking endpoint. Kontaktirajte recepciju.");
              alert("Backend nema SPA booking endpoint (/api/spa/appointments).\nKontaktirajte recepciju. (404)");
            } else {
              throw new Error(coupleSpecialResult?.error || coupleSpecialResult?.detail || `HTTP ${response.status}`);
            }
            setSubmitStatus("error");
            setIsSubmitting(false);
            return;
          }
          
          // ✅ UX FIX D: Check if response has ID - no fake success
          if (!coupleSpecialResult?.id) {
            console.error("❌ Booking response has no ID - rejecting");
            setError("Greška: Rezervacija nije kreirana (BOOKING_NO_ID)");
            setSubmitStatus("error");
            setIsSubmitting(false);
            return;
          }
          
          console.log("✅ SPA SPECIAL COUPLE booked:", coupleSpecialResult);
          
          // ✅ B) Check for notify_status: failed
          const notifyFailed = coupleSpecialResult?.notify_status === "failed";
          
          // ✅ UX POLISH: Use new success handler with bookingType
          handleBookingSuccess({
            bookingType: "coupleSpecial",
            bookingId: coupleSpecialResult.id,
            responseData: coupleSpecialResult,
            notifyFailed: notifyFailed
          });
          return;
        } catch (err) {
          console.error("❌ SPA SPECIAL COUPLE error:", err);
          setError(`Zakazivanje nije uspelo: ${err.message || "Network error"}`);
          setSubmitStatus("error");
          setIsSubmitting(false);
          return;
        }
      }
      
      // SPA BOOKING GRANA – Handle before single/couples logic
      if ((formData.source === "spa" || formData.source === "spaZone" || formData.source === "spaSpecial") && spaBookingMeta) {
        console.log("🚀 SPA handleSubmit called!");
        console.log("🔍 spaBookingMeta:", spaBookingMeta);

        // ✅ FIX D: SPA booking -> POST /api/spa/appointments
        const bookingEndpoint = `${API_BASE}/api/spa/appointments`;
        
        console.log('🔥 FINAL BOOKING ENDPOINT:', bookingEndpoint);
        console.log('🔒 LOCKDOWN CHECK: Booking endpoint:', bookingEndpoint);

        // Convert Date object to YYYY-MM-DD format
        let dateStr;
        if (formData.preferredDate instanceof Date) {
          const year = formData.preferredDate.getFullYear();
          const month = String(formData.preferredDate.getMonth() + 1).padStart(2, '0');
          const day = String(formData.preferredDate.getDate()).padStart(2, '0');
          dateStr = `${year}-${month}-${day}`;
        } else {
          dateStr = formData.preferredDate;
        }
        
        const startTimeIso = `${dateStr}T${formData.preferredTime}:00`;

        const payload = {
          // ✅ A) Client info - OBAVEZNO za email
          client_first_name: formData.firstName,
          client_last_name: formData.lastName,
          client_phone: formData.phone,
          client_email: formData.email,
          
          // ✅ Appointment details
          appointment_date: dateStr,
          start_time: startTimeIso,
          
          // ✅ Type - za backend template selection
          type: "spa",
          category: "SPA",
          
          // ✅ CARD ID - for card-level discounts (OBAVEZNO)
          card_id: spaBookingMeta.cardId || "",
          
          // ✅ SERVICE IDs - array of selected services (OBAVEZNO)
          service_ids: spaBookingMeta.serviceIds || [],
          
          // ✅ Service details - za email template
          // MASTER: Koristi tačan naziv paketa SA UKUPNIM TRAJANJEM
          service_id: spaBookingMeta.variantId || spaBookingMeta.spaPackageId,
          service_name: `${spaBookingMeta.spaName} - ${spaBookingMeta.totalDuration} min`,
          service_description: spaBookingMeta.variantLabel || spaBookingMeta.spaZoneLabel || "",
          
          // ✅ Duration & pricing - MASTER: Koristi totalDuration iz URL params
          // Šaljemo eksplicitno SVE duration polja da backend sigurno vidi
          duration: spaBookingMeta.totalDuration || 0,
          duration_min: spaBookingMeta.totalDuration || 0,
          total_duration: spaBookingMeta.totalDuration || 0,
          base_duration: spaBookingMeta.baseDuration || 0,
          
          // ✅ SPA zone info (ako postoji)
          spa_zone: spaBookingMeta.spaZoneText || "",
          
          // ✅ Notes - UVEK uključi srpski format za backend parsiranje
          // Backend traži "Ukupno trajanje:" za prikaz u Termini/Notifikacije
          notes: formData.message + `\n\n--- BACKEND DATA (SR) ---\nSPA paket: ${spaBookingMeta.spaName}\nVarijanta: ${spaBookingMeta.variantLabel || spaBookingMeta.spaZoneLabel || 'Bez varijante'}\nUkupno trajanje: ${spaBookingMeta.totalDuration} min\nUkupna cena: ${spaBookingMeta.totalPrice} RSD`,

          // ✅ SAMO ORIGINALNA CENA - backend računa popust!
          // Prioritet: quotePricing (od API quote) > spaBookingMeta (od URL params) > 0
          total_original: quotePricing?.original_total || spaBookingMeta?.originalPrice || spaBookingMeta?.totalPrice || 0,
          
          // ✅ Language for backend email template
          lang: formData.lang || language || 'sr'
        };

        console.log("📦 SPA appointment payload:", payload);
        console.log("📤 Sending SPA booking request to:", bookingEndpoint);

        // ✅ A) FIX: Ne čitati response dva puta + pravi error handling
        let spaResult = null;
        try {
          const response = await fetch(bookingEndpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });

          // Read response body ONCE as text
          const text = await response.text();
          
          // Parse JSON safely
          try { 
            spaResult = text ? JSON.parse(text) : null; 
          } catch { 
            spaResult = { raw: text }; 
          }
          
          console.log("📥 SPA booking response status:", response.status);
          console.log("📥 SPA booking result:", spaResult); // ✅ C) Debug log

          if (!response.ok) {
            console.error("❌ SPA booking API error:", response.status, spaResult);
            
            // ✅ Specifična poruka za 404 - backend nema SPA endpoint
            if (response.status === 404) {
              setError("⚠️ Greška: Backend nema SPA booking endpoint (/api/spa/appointments). Kontaktirajte recepciju da doda rutu. (404)");
              alert("Greška: Backend nema SPA booking endpoint (/api/spa/appointments).\n\nKontaktirajte recepciju da doda rutu.\n\n(HTTP 404)");
              setSubmitStatus("error");
              setIsSubmitting(false);
              return;
            }
            
            // Throw error for catch block to handle
            throw new Error(spaResult?.error || spaResult?.detail || spaResult?.message || `HTTP ${response.status}`);
          }
        } catch (fetchError) {
          console.error("❌ SPA booking error:", fetchError);
          const msg = String(fetchError?.message || fetchError);
          
          // ✅ Specifična poruka za 404 iz exception
          if (msg.includes("HTTP_404") || msg.includes("404")) {
            setError("⚠️ Greška: Backend nema SPA booking endpoint (/api/spa/appointments). Kontaktirajte recepciju da doda rutu. (404)");
            alert("Greška: Backend nema SPA booking endpoint.\n\nKontaktirajte recepciju da doda rutu.");
            setSubmitStatus("error");
            setIsSubmitting(false);
            return;
          }
          
          // CORS ili network greška
          if (msg.includes("Failed to fetch") || msg.includes("CORS")) {
            setError("⚠️ Backend nije dostupan ili CORS blokira zahtev. Pokušajte ponovo kasnije.");
            setSubmitStatus("error");
            setIsSubmitting(false);
            return;
          }
          
          // ✅ B) UI poruka za greške
          setError(`Zakazivanje nije uspelo: ${msg}`);
          setSubmitStatus("error");
          setIsSubmitting(false);
          return;
        }

        // ✅ UX FIX: SPA booking success (200 OK)
        // ✅ C) DEBUG log (privremeno)
        console.log("📥 FINAL SPA RESULT:", spaResult);
        console.log("✅ SPA booking successful! ID:", spaResult?.id, "notify_status:", spaResult?.notify_status);
        
        // Get date/time from formData for success message
        let spaDateStr = "";
        if (formData.preferredDate instanceof Date) {
          const day = String(formData.preferredDate.getDate()).padStart(2, '0');
          const month = String(formData.preferredDate.getMonth() + 1).padStart(2, '0');
          const year = formData.preferredDate.getFullYear();
          spaDateStr = `${day}.${month}.${year}`;
        }
        
        // ✅ UX POLISH: Determine bookingType based on source
        const spaBookingType = formData.source === "spaZone" ? "spaZone" : "spa";
        
        // ✅ B) Check for notify_status: failed and show info message
        const notifyFailed = spaResult?.notify_status === "failed";
        
        handleBookingSuccess({
          bookingType: spaBookingType,
          bookingId: spaResult?.id || "spa-success",
          responseData: spaResult || {},
          notifyFailed: notifyFailed // Pass to handler for info message
        });
        
        // CRITICAL: Exit early to not fall into single/couples logic
        return;
      }
      
      // serviceName and queryParams already defined in validation above - no need to redeclare
      
      // Normalize service name for lookup
      // Try exact match first, then try normalized (without duration)
      let serviceLookupName = serviceName;
      
      // If exact match not found, try normalized version
      if (!serviceMapping[serviceLookupName]) {
        const normalized = serviceName
          .replace(/\s*[-–—]\s*\d+\s*min\s*$/i, '') // Remove "- 60 min", "– 90 min", etc.
          .trim();
        
        console.log('🔍 Trying normalized lookup:', { original: serviceName, normalized });
        serviceLookupName = normalized;
      }
      
      // Special handling for couples massage - use original duration for service_id lookup
      let couplesData = null;
      
      // Try to get couples data from localStorage first, then fall back to URL param
      if (isCouplesMassage(serviceName)) {
        try {
          const storedData = localStorage.getItem('couplesBookingData');
          if (storedData) {
            couplesData = JSON.parse(storedData);
            console.log('✅ Loaded couples data from localStorage:', couplesData);
          } else {
            // Fallback to URL param for backwards compatibility
            const couplesDataParam = queryParams.get('couplesData');
            if (couplesDataParam) {
              let decodedParam = couplesDataParam;
              try {
                decodedParam = decodeURIComponent(couplesDataParam);
              } catch (decodeError) {
                console.warn('⚠️ Could not decode URI, using as-is:', decodeError);
              }
              couplesData = JSON.parse(decodedParam);
              console.log('✅ Loaded couples data from URL param:', couplesData);
            }
          }
          
          if (couplesData) {
            // For couples booking, we don't need single service ID lookup
            // We'll use couple-specific endpoint with individual service names
            console.log('🔍 Couples Booking Debug:', {
              originalServiceName: serviceName,
              couplesData: couplesData
            });
          }
        } catch (e) {
          console.error('❌ Error parsing couples data:', e);
        }
      }
      
      // Get service UUID from dynamically loaded mapping (skip for couples - they use different endpoint)
      const isCouplesBooking = couplesData && isCouplesMassage(serviceName);
      const serviceId = isCouplesBooking ? null : serviceMapping[serviceLookupName];
      
      console.log('🔍 Service lookup:', {
        serviceName,
        serviceLookupName,
        isCouplesBooking,
        foundId: serviceId || (isCouplesBooking ? 'COUPLES BOOKING - NO ID NEEDED' : 'NOT FOUND'),
        mappingLoaded: servicesLoaded,
        availableKeys: Object.keys(serviceMapping).length
      });
      
      // CRITICAL: Validate service exists in mapping (skip for couples booking)
      if (!isCouplesBooking && !serviceId) {
        console.error('❌ SERVICE NOT FOUND IN MAPPING!', {
          serviceName,
          serviceLookupName,
          availableServices: Object.keys(serviceMapping).filter(k => k.includes(serviceName.split(' - ')[0]))
        });
        setError(translate("error") || "Usluga nije pronađena u sistemu. Molimo pokušajte ponovo.");
        setIsSubmitting(false);
        return;
      }
      
      // Debug logging
      console.log('📌 Booking Debug:', {
        serviceName,
        serviceLookupName,
        serviceId,
        found: true
      });
      
      // Only send to booking API if we have date and time
      if (formData.preferredDate && formData.preferredTime) {
        // Convert Date object to YYYY-MM-DD format using local time (Belgrade timezone)
        let dateStr;
        if (formData.preferredDate instanceof Date) {
          const year = formData.preferredDate.getFullYear();
          const month = String(formData.preferredDate.getMonth() + 1).padStart(2, '0');
          const day = String(formData.preferredDate.getDate()).padStart(2, '0');
          dateStr = `${year}-${month}-${day}`;
        } else {
          dateStr = formData.preferredDate;
        }
        
        // Check if this is a couple booking and get couples data
        let couplesBookingData = null;
        if (isCouplesMassage(serviceName)) {
          // Try localStorage first
          const storedData = localStorage.getItem('couplesBookingData');
          if (storedData) {
            couplesBookingData = JSON.parse(storedData);
          } else {
            // Fallback to URL param
            const couplesDataParam = queryParams.get('couplesData');
            if (couplesDataParam) {
              let decodedParam = couplesDataParam;
              try {
                decodedParam = decodeURIComponent(couplesDataParam);
              } catch (decodeError) {
                console.warn('⚠️ Could not decode couplesData URI, using as-is');
              }
              couplesBookingData = JSON.parse(decodedParam);
            }
          }
        }
        
        const isCoupleBooking = couplesBookingData && isCouplesMassage(serviceName);
        
        let appointmentData;
        let bookingEndpoint;
        
        if (isCoupleBooking) {
          const couplesData = couplesBookingData;
          
          // ✅ COUPLES BOOKING - ARRAY SUPPORT
          // Pravilo: UI cena = zbir SVIH izabranih [PAROVI] servisa (Person1 + Person2)
          // Slati person1_services i person2_services kao ARRAY-e
          
          // ✅ FIX: Koristi ARRAY-e umesto single values
          const person1Services = couplesData.person1_services || 
            (couplesData.person1 ? [couplesData.person1] : []);
          const person2Services = couplesData.person2_services || 
            (couplesData.person2 ? [couplesData.person2] : []);
          
          // Calculate totals from ALL services in arrays
          const p1Total = person1Services.reduce((sum, s) => sum + (s.final_price || s.price || 0), 0);
          const p2Total = person2Services.reduce((sum, s) => sum + (s.final_price || s.price || 0), 0);
          const uiTotalPrice = p1Total + p2Total;
          
          // Calculate total duration
          const p1Duration = person1Services.reduce((sum, s) => sum + parseInt(s.duration || 60), 0);
          const p2Duration = person2Services.reduce((sum, s) => sum + parseInt(s.duration || 60), 0);
          const totalMinutes = p1Duration + p2Duration;
          
          console.log('🔍 COUPLES ARRAY MODE:', {
            person1_services: person1Services,
            person2_services: person2Services,
            p1_count: person1Services.length,
            p2_count: person2Services.length,
            p1_total: p1Total,
            p2_total: p2Total,
            ui_total: uiTotalPrice,
            duration: totalMinutes
          });
          
          // Validacija: sve masaže moraju biti [PAROVI]
          const allServices = [...person1Services, ...person2Services];
          const invalidService = allServices.find(s => s.name && !s.name.includes('[PAROVI]'));
          if (invalidService) {
            console.error('❌ COUPLES STRICT: svi servisi moraju biti [PAROVI]', invalidService);
            setError('Greška: Izaberite samo [PAROVI] masaže.');
            setIsSubmitting(false);
            return;
          }
          
          if (person1Services.length === 0 || person2Services.length === 0) {
            console.error('❌ Missing services for couples booking');
            setError('Molimo izaberite masažu za obe osobe.');
            setIsSubmitting(false);
            return;
          }
          
          // Build display strings with all services joined by " + "
          const p1Display = person1Services.map(s => `${s.name} (${s.duration}min, ${s.final_price || s.price} RSD)`).join(' + ');
          const p2Display = person2Services.map(s => `${s.name} (${s.duration}min, ${s.final_price || s.price} RSD)`).join(' + ');
          
          // PRICING_DEBUG u notes (za backend dev) - with all services
          const p1Debug = person1Services.map(s => `{id:${s.service_id}, name:${s.name}, price:${s.final_price || s.price}}`).join(', ');
          const p2Debug = person2Services.map(s => `{id:${s.service_id}, name:${s.name}, price:${s.final_price || s.price}}`).join(', ');
          const pricingDebug = `PRICING_DEBUG: ui_total=${uiTotalPrice}; p1_count=${person1Services.length}; p2_count=${person2Services.length}; p1=[${p1Debug}]; p2=[${p2Debug}]`;
          
          const notesText = `COUPLES [PAROVI]: Osoba1=${p1Display}; Osoba2=${p2Display}; UKUPNO=${uiTotalPrice} RSD\n${pricingDebug}`;
          
          // 🔍 DEBUG CONSOLE LOG pre POST-a
          console.log('🔍 PRICING DEBUG INFO (ARRAYS):', {
            person1_services: person1Services,
            person2_services: person2Services,
            ui_total_price: uiTotalPrice,
            duration: totalMinutes
          });
          
          // ✅ PAYLOAD ZA /api/appointments/couple
          // Backend očekuje: person1_services i person2_services kao liste ID-eva
          const p1ServiceIds = person1Services.map(s => s.service_id);
          const p2ServiceIds = person2Services.map(s => s.service_id);
          
          // ✅ FIX: Koristi duration_type iz couplesData (paralelno trajanje, ne sabiraj!)
          // Za [PAROVI] tretmane, obe osobe se tretiraju paralelno
          const durationTypeValue = couplesBookingData.duration_type || '60';
          
          appointmentData = {
            // ✅ TYPE I CATEGORY - OBAVEZNO za backend template selection
            type: "couple",
            category: "MASAZE_PAROVI",
            
            // Client info
            client_first_name: formData.firstName,
            client_last_name: formData.lastName,
            client_phone: formData.phone,
            client_email: formData.email,
            
            // ✅ Šaljemo liste ID-eva (ne objekte)
            person1_services: p1ServiceIds,
            person2_services: p2ServiceIds,
            
            // ✅ duration_type
            duration_type: durationTypeValue,
            duration_min: parseInt(durationTypeValue, 10),
            
            // ✅ start_time
            start_time: `${dateStr}T${formData.preferredTime}:00`,
            
            // ✅ SAMO ORIGINALNA CENA - backend računa popust!
            // NE SLATI final_price ili discount_percentage
            total_original: couplesBookingData.pair_original_price || uiTotalPrice || 0,
            
            // ✅ notes za debug
            notes: notesText,
            
            // ✅ Language for backend email template (from couplesData or fallback)
            lang: couplesBookingData.lang || formData.lang || language || 'sr'
          };
          
          // ✅ DEBUG LOG
          console.log('📦 COUPLES MASSAGE payload:', appointmentData);
          console.log('➡️ POST:', '/api/appointments/couple');
          console.log('📤 person1_services IDs:', p1ServiceIds);
          console.log('📤 person2_services IDs:', p2ServiceIds);
          
          // ✅ COUPLES MORA IĆI NA /api/appointments/couple
          bookingEndpoint = '/api/appointments/couple';
        } else {
          // Regular booking data
          // Extract duration from service name (e.g., "Masaža - 90 min" -> 90)
          let duration = 60; // default
          const durationMatch = serviceName.match(/(\d+)\s*min/i);
          if (durationMatch) {
            duration = parseInt(durationMatch[1]);
            console.log(`📏 Extracted duration: ${duration} min from "${serviceName}"`);
          }
          
          appointmentData = {
            // ✅ TYPE I CATEGORY - OBAVEZNO за backend template selection
            type: "massage",
            category: "MASAZE",
            
            // Client info
            client_first_name: formData.firstName,
            client_last_name: formData.lastName,
            client_phone: formData.phone,
            client_email: formData.email,
            
            // Appointment details
            appointment_date: dateStr,
            start_time: `${dateStr}T${formData.preferredTime}:00`,
            
            // Service details
            service_id: serviceId,
            service_name: serviceName,
            duration: duration,
            duration_min: duration,
            duration_type: duration,
            
            // Notes
            notes: formData.message || "",
            lang: formData.lang || language || 'sr'  // ✅ Language for backend email template
          };
          
          // ✅ ISPRAVNO prema backendu recepcije - obične masaže koriste /api/appointments
          bookingEndpoint = '/api/appointments';
          
          // ✅ DEBUG LOG
          console.log('📦 MASSAGE payload:', appointmentData);
          console.log('➡️ POST:', bookingEndpoint);
        }
        // 🔒 Use API_BASE for all booking requests
        const url = `${API_BASE}${bookingEndpoint}`;
        const finalEndpoint = url;
        
        console.log('🔥 FINAL BOOKING ENDPOINT:', finalEndpoint);
        console.log('🔒 LOCKDOWN CHECK: Booking URL:', url);
        console.log('📦 FULL PAYLOAD being sent:', JSON.stringify(appointmentData, null, 2));
        
        // ✅ DOKAZ: Eksplicitni log za discount/price polja
        console.log('💰 PRICE PROOF:', {
          discount_percentage: appointmentData.discount_percentage ?? 'NOT_SET',
          original_price: appointmentData.original_price ?? 'NOT_SET',
          final_price: appointmentData.final_price ?? 'NOT_SET'
        });
        
        const res = await fetch(finalEndpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(appointmentData),
        });

        const text = await res.text(); // SAMO JEDNOM

        let data = {};
        try {
          data = text ? JSON.parse(text) : {};
        } catch (e) {
          console.error('JSON parse error:', e, text);
        }

        if (!res.ok) {
          console.error('❌ BOOKING FAILED', res.status, data);
          // ✅ FIX C: Better error message extraction
          const errorMsg = data?.error || data?.message || data?.detail || 'Rezervacija nije uspela.';
          setError(errorMsg);
          setSubmitStatus('error');
          setIsSubmitting(false);
          return;
        }

        console.log('✅ BOOKING SUCCESS', data);
        
        // ✅ UX POLISH: Handle success with simple message
        console.log('🎉 BOOKING SUCCESS - showing success message');
        
        // Clear couples booking data from localStorage after successful booking
        localStorage.removeItem('couplesBookingData');
        console.log('✅ Cleared couples booking data from localStorage');
        
        // ✅ FIX A: Check for booking ID before showing success
        if (!data?.id) {
          console.warn('⚠️ Booking response has no ID, but was 2xx - treating as success');
        }
        
        // ✅ UX POLISH: Determine bookingType based on category
        const massageBookingType = isCouplesMassage ? "couple" : "massage";
        
        // Use new success handler with bookingType
        handleBookingSuccess({
          bookingType: massageBookingType,
          bookingId: data?.id || "massage-success",
          responseData: data // Pass response for email_sent check
        });
      }
      
    } catch (error) {
      console.error('🚨 DETAILED BOOKING ERROR:', {
        message: error.message,
        stack: error.stack,
        name: error.name,
        cause: error.cause
      });
      
      // Detailed error handling with specific messages
      let errorMessage = 'Došlo je do greške';
      
      if (error.message.includes('Failed to fetch')) {
        errorMessage = 'Greška u komunikaciji sa serverom. Proverite internet konekciju.';
      } else if (error.message.includes('Backend not available')) {
        errorMessage = 'Server trenutno nije dostupan. Pokušajte ponovo za nekoliko minuta.';
      } else if (error.message.includes('Booking failed')) {
        errorMessage = `Greška pri rezervaciji: ${error.message}`;
      } else if (error.message.includes('NetworkError')) {
        errorMessage = 'Greška mreže. Proverite internet konekciju.';
      } else if (error.message.includes('CORS')) {
        errorMessage = 'Greška u konfiguraciji. Kontaktirajte podršku.';
      } else {
        errorMessage = `Neočekivana greška: ${error.message}`;
      }
      
      // Show specific error message to user
      setError(errorMessage);
      
      // Error - show red X
      setSubmitStatus('error');
      
      // Hide error after 5 seconds (longer for detailed messages)
      setTimeout(() => {
        setSubmitStatus(null);
        setError(null);
      }, 5000);

    } finally {
      // ALWAYS reset isSubmitting, even if error occurs
      if (submitTimeoutRef.current) {
        clearTimeout(submitTimeoutRef.current);
      }
      setIsSubmitting(false);
      console.log('✅ isSubmitting reset to false');
    }
  };

  const contactSEO = getSEO('contact');

  return (
    <div className="contact-container">
      <Helmet>
        <title>{contactSEO.title}</title>
        <meta name="description" content={contactSEO.description} />
        <meta name="keywords" content={contactSEO.keywords} />
        <link rel="canonical" href={contactSEO.canonical} />
      </Helmet>

      {/* Header */}
      <section className="page-header">
        <div className="page-header-content">
          <h1 className="page-title">BOOKING</h1>
        </div>
        <div className="page-decoration contact-logo-animation">
          <img 
            src="https://customer-assets.emergentagent.com/job_serene-retreat-1/artifacts/r2vm59ex_Bualuang%20logo%20senka.png"
            alt="Bua Luang Thai Spa Logo"
            className="contact-animated-logo"
          />
        </div>
      </section>

      {/* Unified Contact Card */}
      <section className="contact-section">
        <Card className="unified-contact-card">
          <CardContent className="unified-contact-content" style={{ padding: '2rem' }}>
            <div style={{ 
              display: 'flex', 
              gap: '2rem', 
              alignItems: 'flex-start',
              justifyContent: 'space-between'
            }}>
              {/* Contact Form Section - Left Side */}
              <div style={{ flex: '0 0 55%', maxWidth: '55%' }}>
                <form onSubmit={handleSubmit} className="unified-contact-form">
                <div className="form-row">
                  <div className="form-group">
                    <Label htmlFor="firstName">{translate("firstName")}</Label>
                    <Input
                      id="firstName"
                      name="firstName"
                      type="text"
                      value={formData.firstName}
                      onChange={handleInputChange}
                      required
                      className="form-input"
                      placeholder={translate("firstName")}
                    />
                  </div>
                  <div className="form-group">
                    <Label htmlFor="lastName">{translate("lastName")}</Label>
                    <Input
                      id="lastName"
                      name="lastName"
                      type="text"
                      value={formData.lastName}
                      onChange={handleInputChange}
                      required
                      className="form-input"
                      placeholder={translate("lastName")}
                    />
                  </div>
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <Label htmlFor="phone">{translate("phone")}</Label>
                    <Input
                      id="phone"
                      name="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={handleInputChange}
                      required
                      className="form-input"
                      placeholder={translate("phone")}
                    />
                  </div>
                  <div className="form-group">
                    <Label htmlFor="email">{translate("email")}</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      className="form-input"
                      placeholder={translate("email")}
                    />
                  </div>
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <Label htmlFor="preferredDate">
                      <Calendar className="w-4 h-4 inline mr-2" />
                      {translate("preferredDate")}
                    </Label>
                    <div style={{ width: '100%' }}>
                      <CustomCalendarModal
                        value={formData.preferredDate}
                        onChange={handleDateChange}
                        name="preferredDate"
                        minDate={new Date()}
                      />
                    </div>
                  </div>
                  <div className="form-group">
                    <Label htmlFor="preferredTime">
                      <Clock className="w-4 h-4 inline mr-2" />
                      {translate("preferredTime")}
                    </Label>
                    <div style={{ width: '100%' }}>
                      <CustomTimePickerModal
                        value={formData.preferredTime}
                        onChange={handleInputChange}
                        name="preferredTime"
                      />
                    </div>
                  </div>
                </div>
                
                {/* Service Dropdown - if no service selected from card AND not SPA booking */}
                {(() => {
                  const source = new URLSearchParams(location.search).get('source');
                  // ✅ FIX B: Added 'coupleSpecial' to hide dropdown for Romantični paketi
                  const isSpaFlow = ['spa', 'spaZone', 'spaSpecial', 'coupleSpecial'].includes(source);
                  const hasService = new URLSearchParams(location.search).get('service');
                  return !hasService && !isSpaFlow;
                })() && (
                  <div className="form-group">
                    <Label htmlFor="serviceDropdown">
                      <span style={{ fontSize: '1rem', fontWeight: '600' }}>
                        {translate("selectService") || "Izaberite uslugu"}
                      </span>
                    </Label>
                    <select
                      id="serviceDropdown"
                      name="serviceDropdown"
                      value={formData.service || ''}
                      onChange={(e) => {
                        const selectedValue = e.target.value;
                        if (selectedValue) {
                          const displayName = e.target.options[e.target.selectedIndex].text;
                          
                          setFormData(prev => ({
                            ...prev,
                            service: displayName,
                            message: `${translate('wantToBook')} ${displayName}`
                          }));
                        } else {
                          setFormData(prev => ({
                            ...prev,
                            service: '',
                            message: ''
                          }));
                        }
                      }}
                      style={{
                        width: '100%',
                        padding: '0.75rem 1rem',
                        border: '1px solid #444',
                        borderRadius: '8px',
                        background: 'rgba(0, 0, 0, 0.3)',
                        color: '#d4af37',
                        fontSize: '1rem',
                        cursor: 'pointer',
                        transition: 'all 0.3s ease'
                      }}
                    >
                      <option value="" style={{ background: '#1a1a1a', color: '#999' }}>
                        -- {translate("chooseService") || "Odaberite uslugu"} --
                      </option>
                      
                      {availableServices.single.length > 0 && (
                        <optgroup label={translate("massages") || "MASAŽE"} style={{ background: '#1a1a1a', color: '#d4af37', fontWeight: 'bold' }}>
                          {availableServices.single.map(service => {
                            const hasDiscount = service.discount_percentage > 0;
                            const displayPrice = hasDiscount 
                              ? `${service.original_price?.toLocaleString('sr-RS')} → ${service.final_price?.toLocaleString('sr-RS')} RSD (-${service.discount_percentage}%)`
                              : `${service.final_price?.toLocaleString('sr-RS')} RSD`;
                            
                            return (
                              <option
                                key={service.id}
                                value={service.name}
                                style={{ background: '#1a1a1a', color: '#d4af37' }}
                              >
                                {service.name} - {displayPrice}
                              </option>
                            );
                          })}
                        </optgroup>
                      )}
                      
                      {availableServices.couples.length > 0 && (
                        <optgroup label={translate("couplesMassage") || "MASAŽE ZA PAROVE"} style={{ background: '#1a1a1a', color: '#d4af37', fontWeight: 'bold' }}>
                          {availableServices.couples.map(service => {
                            const hasDiscount = service.discount_percentage > 0;
                            const displayPrice = hasDiscount 
                              ? `${service.original_price?.toLocaleString('sr-RS')} → ${service.final_price?.toLocaleString('sr-RS')} RSD (-${service.discount_percentage}%)`
                              : `${service.final_price?.toLocaleString('sr-RS')} RSD`;
                            
                            return (
                              <option
                                key={service.id}
                                value={service.name}
                                style={{ background: '#1a1a1a', color: '#d4af37' }}
                              >
                                {service.name} - {displayPrice}
                              </option>
                            );
                          })}
                        </optgroup>
                      )}
                    </select>
                  </div>
                )}
                
                <div className="form-group">
                  <Label htmlFor="message">{translate("message")}</Label>
                  <Textarea
                    id="message"
                    name="message"
                    value={formData.message}
                    onChange={handleInputChange}
                    required
                    rows={5}
                    className="form-textarea"
                    placeholder={translate("messagePlaceholder")}
                  />
                </div>
                
                {/* Success/Error Feedback */}
                {submitStatus && (
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '1rem',
                    borderRadius: '8px',
                    backgroundColor: submitStatus === 'success' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    border: `2px solid ${submitStatus === 'success' ? '#22c55e' : '#ef4444'}`,
                    marginBottom: '1rem'
                  }}>
                    {submitStatus === 'success' ? (
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
                        <div style={{ display: 'flex', alignItems: 'center' }}>
                          <svg style={{ width: '32px', height: '32px', color: '#22c55e', marginRight: '0.5rem' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                          </svg>
                          {/* ✅ UX B: Simple 1-sentence success message */}
                          <div style={{ color: '#22c55e', fontWeight: 'bold', fontSize: '1.1rem' }}>
                            {successMsg || "Uspešno ste zakazali termin."}
                          </div>
                        </div>
                        {/* ✅ UX C: Secondary message (email confirmation) */}
                        {secondaryMessage && (
                          <div style={{ color: '#888', fontSize: '0.9rem', marginTop: '0.5rem' }}>
                            {secondaryMessage}
                          </div>
                        )}
                        {/* ✅ UX A: Button to go back (no auto redirect) */}
                        <button 
                          onClick={() => navigate("/")}
                          style={{
                            marginTop: '1rem',
                            padding: '0.5rem 1.5rem',
                            background: 'linear-gradient(135deg, #d4af37 0%, #f4d03f 100%)',
                            border: 'none',
                            borderRadius: '6px',
                            color: '#1a1a1a',
                            fontWeight: 'bold',
                            cursor: 'pointer'
                          }}
                        >
                          Nazad na početnu
                        </button>
                      </div>
                    ) : (
                      <>
                        <svg style={{ width: '32px', height: '32px', color: '#ef4444', marginRight: '0.5rem' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                        <span style={{ color: '#ef4444', fontWeight: 'bold', fontSize: '1.1rem' }}>
                          Greška! Molimo pokušajte ponovo.
                        </span>
                      </>
                    )}
                  </div>
                )}
                
                <Button 
                  type="submit"
                  disabled={isSubmitting}
                  className="submit-button"
                >
                  <Send className="w-4 h-4 mr-2" />
                  {isSubmitting ? "Šalje se..." : translate("send")}
                </Button>
              </form>
            </div>

            {/* Booking Information Section - Right Side */}
            <div style={{ flex: '0 0 40%', maxWidth: '40%' }}>
              <h3 style={{ 
                color: 'var(--spa-gold)', 
                fontSize: '1.5rem', 
                marginBottom: '1.5rem',
                fontWeight: 'bold'
              }}>
                {translate("bookingInfoTitle")}
              </h3>
              <div className="unified-booking-details">
                <div className="unified-booking-item" style={{
                  marginBottom: '1.5rem',
                  padding: '1rem',
                  backgroundColor: 'rgba(212, 175, 55, 0.05)',
                  borderLeft: '3px solid var(--spa-gold)',
                  borderRadius: '4px'
                }}>
                  <h4 style={{ color: 'var(--spa-gold)', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                    {translate("cancellationTitle")}
                  </h4>
                  <p style={{ color: 'rgba(245, 242, 232, 0.9)', lineHeight: '1.6' }}>
                    {translate("cancellationText")}
                  </p>
                </div>
                <div className="unified-booking-item" style={{
                  marginBottom: '1.5rem',
                  padding: '1rem',
                  backgroundColor: 'rgba(212, 175, 55, 0.05)',
                  borderLeft: '3px solid var(--spa-gold)',
                  borderRadius: '4px'
                }}>
                  <h4 style={{ color: 'var(--spa-gold)', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                    {translate("lateArrivalTitle")}
                  </h4>
                  <p style={{ color: 'rgba(245, 242, 232, 0.9)', lineHeight: '1.6' }}>
                    {translate("lateArrivalText")}
                  </p>
                </div>
                <div className="unified-booking-item" style={{
                  padding: '1rem',
                  backgroundColor: 'rgba(212, 175, 55, 0.05)',
                  borderLeft: '3px solid var(--spa-gold)',
                  borderRadius: '4px'
                }}>
                  <h4 style={{ color: 'var(--spa-gold)', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                    {translate("groupBookingTitle")}
                  </h4>
                  <p style={{ color: 'rgba(245, 242, 232, 0.9)', lineHeight: '1.6' }}>
                    {translate("groupBookingText")}
                  </p>
                </div>
              </div>
            </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
};

export default Contact;