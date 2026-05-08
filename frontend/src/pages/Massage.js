import React, { useEffect, useState } from "react";
import { Helmet } from "react-helmet";
import { useLanguage } from "../context/LanguageContext";
import { translations } from "../data/translations";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Link, useNavigate } from "react-router-dom";
import { Clock, Star } from "lucide-react";
import { throttle } from "../utils/debounce";
import CouplesMassageCard from "../components/CouplesMassageCard";
import { LOCKDOWN } from "../lockdown";
import { API_BASE } from "../config/api";

const EXPECTED = "BL_LOCK_2025_12_16";
if (LOCKDOWN.MASAZE_LOCKED && LOCKDOWN.LOCK_TOKEN !== EXPECTED) {
  throw new Error("LOCKDOWN VIOLATION: MASAŽE su zaključane.");
}

const Massage = () => {
  const { translate, currentLanguage } = useLanguage();
  const navigate = useNavigate();
  const [scrollY, setScrollY] = useState(0);
  const [isMobile, setIsMobile] = useState(false);

  // 🔐 HARD LOCK LOG (no window.location.origin)
  useEffect(() => {
    console.log("🔐 [Massage.js] API_BASE:", API_BASE);
  }, []);

  // Detect mobile device for video optimization
  useEffect(() => {
    const checkMobile = () => {
      const width = window.visualViewport ? window.visualViewport.width : window.screen.width;
      setIsMobile(width < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);
  
  // State for each massage service duration - all default to 60 min
  const [durations, setDurations] = useState({
    traditional: '60',
    aroma: '60',
    hotStone: '60',
    royal: '30',  // Changed to match API (30, 45, 60)
    foot: '30',   // Changed to match API (30, 45, 60)
    couple: '60',
    sports: '60',
    shiatsu: '60',
    reflexology: '60',
    backShoulder: '60',
    antiStress: '60',
    prenatal: '60',
    deepTissue: '60',
    bamboo: '60',
    lymphatic: '60',
    aromaDeepTissue: '60',
    aromaHotStone: '90',
    aromaThaiHerbal: '90',  // API only has 90 min
    thaiHerbal: '90'
  });

  // State for "Masaža za parove" (couples massage) selections
  const [couplesSelections, setCouplesSelections] = useState({
    duration: '60',
    person1Massage1: null,
    person1Massage2: null, // Second 60 min massage for person 1 in 120 min mode
    person2Massage1: null,
    person2Massage2: null  // Second 60 min massage for person 2 in 120 min mode
  });

  const [dropdownOpen, setDropdownOpen] = useState({ person1: false, person2: false });

  const [serviceDiscounts, setServiceDiscounts] = useState({}); // Per-service discount percentages for regular cards
  // ✅ REMOVED: couplesDiscountPercent - couples kartice na /massage ne prikazuju badge
  // 🔒 DO NOT MODIFY — STABLE VERIFIED LOGIC (Bua Luang - SNAPSHOT: BuaLuang-FRONTEND-STABLE-01)
  // Dynamic data fetching from backend API
  const [apiServices, setApiServices] = useState({});

  // Fetch ALL service data dynamically from API - NO HARDCODING
  useEffect(() => {
    const fetchAllServices = async () => {
      try {
        const backendUrl = API_BASE;
        
        console.log("🧠 Massage page – backendUrl:", backendUrl);

        const singleListUrl = `${backendUrl}/api/services/single/list`;
        const couplesListUrl = `${backendUrl}/api/services/couples/list`;

        console.log("🔗 Will fetch SINGLE from:", singleListUrl);
        console.log("🔗 Will fetch COUPLES from:", couplesListUrl);
        
        console.log('🔍 Loading services from:', `${backendUrl}/api/services/single/list`);
        
        const singleResponse = await fetch(`${backendUrl}/api/services/single/list`);
        console.log('🔍 /api/services/single/list status:', singleResponse.status);
        
        // ✅ FIX: Read body only once to avoid "body stream already read"
        const raw = await singleResponse.text();
        let singleServices = [];
        try {
          singleServices = raw ? JSON.parse(raw) : [];
        } catch {
          console.error('❌ Failed to parse services JSON:', raw);
          throw new Error('Invalid JSON response');
        }
        
        if (!singleResponse.ok) {
          throw new Error(singleServices?.error || singleServices?.message || `HTTP ${singleResponse.status}`);
        }
        
        console.log('✅ Services loaded:', singleServices.length, 'services');
        
        // Group services by base name (remove " - XX min" for grouping DISPLAY only)
        const grouped = {};
        const discountMap = {};
        
        singleServices.forEach(service => {
          const fullName = service.name; // e.g., "Masaža stopala - 30 min"
          
          // Normalize different dash types and spacing before extracting baseName
          const normalized = fullName.replace(/–/g, '-').replace(/\s*-\s*/g, ' - ');
          const baseName = normalized.replace(/\s*-\s*\d+\s*min\s*$/i, '').trim(); // "Masaža stopala"
          
          if (!grouped[baseName]) {
            grouped[baseName] = [];
          }
          
          // Store COMPLETE service data from API - NO MODIFICATIONS, NO CALCULATIONS
          // CRITICAL FIX: Root-level final_price has DOUBLE DISCOUNT bug from external API!
          // Use metadata.final_price as source of truth!
          const metadata = service.metadata || {};
          const correctFinalPrice = metadata.final_price || service.price;  // Fallback to price if metadata missing
          const correctOriginalPrice = metadata.original_price || service.price;
          
          grouped[baseName].push({
            fullName: fullName,           // Exact name from API
            serviceId: service.id,        // Exact ID from API
            duration: service.duration,   // Exact duration from API
            price: service.price,         // For reference
            finalPrice: correctFinalPrice,  // USE metadata.final_price - source of truth!
            originalPrice: correctOriginalPrice,  // Use metadata.original_price
            discount: service.discount_percentage || 0  // Just for badge display
          });
          
          // Map discount for display
          if (!discountMap[baseName] && service.discount_percentage > 0) {
            discountMap[baseName] = service.discount_percentage;
          }
        });
        
        console.log('✅ 100% DYNAMIC services grouped:', Object.keys(grouped).length, 'unique services');
        console.log('📋 Service keys:', Object.keys(grouped));
        setApiServices(grouped);
        setServiceDiscounts(discountMap);
        
        // ✅ Couples discount - REMOVED from UI display
        // Couples kartice na /massage NE SMEJU prikazivati badge iz paketa
        // Popust se prikazuje samo u booking odgovoru/snapshot-u
        // setCouplesDiscountPercent(0);  // Badge uvek OFF
        console.log('✅ Couples packages loaded (badge disabled on listing page)');
        
      } catch (error) {
        console.error("❌ Massage fetch error:", error);
        console.error('❌ Error fetching services from API:', error);
        console.error('❌ Backend URL was:', API_BASE);
        // Set empty object to prevent infinite "Učitavanje..." state
        setApiServices({});
      }
    };
    fetchAllServices();
  }, []);

  // 100% DYNAMIC function - uses ONLY API data, NO HARDCODING
  const getMassageDetails = (serviceKey, serviceName) => {
    const selectedDuration = durations[serviceKey]; // "60", "90", "120"
    
    console.log(`🔍 getMassageDetails called:`, { serviceKey, serviceName, selectedDuration });
    
    // Check if we have API data for this service
    if (apiServices[serviceName] && apiServices[serviceName].length > 0) {
      console.log(`📦 API variants for ${serviceName}:`, apiServices[serviceName].map(v => `${v.duration}min=${v.price}RSD`));
      
      // Find the service variant with matching duration
      const variant = apiServices[serviceName].find(v => v.duration === parseInt(selectedDuration));
      
      if (variant) {
        // Return EXACT data from API - NO CALCULATIONS, NO MODIFICATIONS
        console.log(`✅ MATCHED variant for ${serviceName}:`, { 
          duration: variant.duration, 
          finalPrice: variant.finalPrice, 
          originalPrice: variant.originalPrice,
          discount: variant.discount 
        });
        
        return {
          duration: `${variant.duration} min`,
          price: `${variant.finalPrice.toLocaleString('sr-RS')} RSD`,  // USE FINAL PRICE - backend already applied discount!
          originalPrice: variant.discount > 0 ? `${variant.originalPrice.toLocaleString('sr-RS')} RSD` : null,  // Show original only if there's discount
          serviceId: variant.fullName, // Use EXACT full name from API for booking link
          discount: variant.discount,  // Just for badge display
          apiServiceId: variant.serviceId // Store actual service ID for booking payload
        };
      } else {
        console.error(`❌ NO MATCH for ${serviceName} - duration ${selectedDuration} (parsed: ${parseInt(selectedDuration)})`);
        console.error(`   Available durations:`, apiServices[serviceName].map(v => v.duration));
      }
    } else {
      console.warn(`⚠️ No API data for ${serviceName} yet`);
    }
    
    // Fallback only if API data not yet loaded
    console.warn(`⚠️ Fallback for ${serviceName} - ${selectedDuration} min`);
    return {
      duration: `${selectedDuration} min`,
      price: 'Učitavanje...',
      serviceId: serviceName
    };
  };

  // REMOVE ALL HARDCODED DATA BELOW - keeping only for reference during transition
  // TODO: Delete this entire block once fully tested
  const OLD_getMassageDetails_DEPRECATED = (serviceKey, serviceName) => {
    const duration = durations[serviceKey];
    
    if (serviceKey === 'traditional' || serviceKey === 'aroma') {
      const options = {
        '60': { duration: '60 min', price: '4,400 RSD', serviceId: `${serviceName} - 60 min` },
        '90': { duration: '90 min', price: '5,600 RSD', serviceId: `${serviceName} - 90 min` },
        '120': { duration: '120 min', price: '6,800 RSD', serviceId: `${serviceName} - 120 min` }
      };
      return options[duration];
    }
    
    // Special pricing for Hot oil (no 120 min option)
    if (serviceKey === 'hotStone') {
      const options = {
        '60': { duration: '60 min', price: '4,600 RSD', serviceId: `${serviceName} - 60 min` },
        '90': { duration: '90 min', price: '5,800 RSD', serviceId: `${serviceName} - 90 min` }
      };
      return options[duration] || options['60']; // Default to 60 if 120 is selected
    }
    
    // Special pricing and duration for Glava, vrat, ramena i leđa
    if (serviceKey === 'royal') {
      const options = {
        '60': { duration: '30 min', price: '2,400 RSD', serviceId: `${serviceName} - 30 min` },
        '90': { duration: '45 min', price: '3,200 RSD', serviceId: `${serviceName} - 45 min` },
        '120': { duration: '60 min', price: '3,900 RSD', serviceId: `${serviceName} - 60 min` }
      };
      return options[duration];
    }
    
    // Special pricing and duration for Masaža stopala
    if (serviceKey === 'foot') {
      const options = {
        '60': { duration: '30 min', price: '2,400 RSD', serviceId: `${serviceName} - 30 min` },
        '90': { duration: '45 min', price: '2,900 RSD', serviceId: `${serviceName} - 45 min` },
        '120': { duration: '60 min', price: '3,500 RSD', serviceId: `${serviceName} - 60 min` }
      };
      return options[duration];
    }
    
    // Special pricing for Aroma duboko tkivo
    if (serviceKey === 'aromaDeepTissue') {
      const options = {
        '60': { duration: '60 min', price: '4,900 RSD', serviceId: `${serviceName} - 60 min` },
        '90': { duration: '90 min', price: '6,000 RSD', serviceId: `${serviceName} - 90 min` }
      };
      return options[duration] || options['60']; // Default to 60
    }
    
    // Special pricing for Aromaterapija & topli kamen
    if (serviceKey === 'aromaHotStone') {
      const options = {
        '90': { duration: '90 min', price: '6,200 RSD', serviceId: `${serviceName} - 90 min` },
        '120': { duration: '120 min', price: '7,200 RSD', serviceId: `${serviceName} - 120 min` }
      };
      return options[duration] || options['90']; // Default to 90
    }
    
    // Special pricing for Aroma sa toplim biljnim kompresama
    if (serviceKey === 'aromaThaiHerbal') {
      const options = {
        '90': { duration: '90 min', price: '6,200 RSD', serviceId: `${serviceName} - 90 min` },
        '120': { duration: '120 min', price: '7,200 RSD', serviceId: `${serviceName} - 120 min` }
      };
      return options[duration] || options['90']; // Default to 90
    }
    
    // Special pricing for Thai masaža sa toplim biljnim kompresama
    if (serviceKey === 'thaiHerbal') {
      const options = {
        '90': { duration: '90 min', price: '6,200 RSD', serviceId: `${serviceName} - 90 min` },
        '120': { duration: '120 min', price: '7,200 RSD', serviceId: `${serviceName} - 120 min` }
      };
      return options[duration] || options['90']; // Default to 90
    }
    
    // Special pricing for couple
    if (serviceKey === 'couple') {
      const options = {
        '60': { duration: '60 min', price: '4,900 RSD', serviceId: `${serviceName} - 60 min` },
        '90': { duration: '90 min', price: '6,000 RSD', serviceId: `${serviceName} - 90 min` }
      };
      return options[duration];
    }
    
    // Default pricing for all other massages
    const options = {
      '60': { duration: '60 min', price: '3,000 RSD', serviceId: `${serviceName} - 60 min` },
      '90': { duration: '90 min', price: '4,000 RSD', serviceId: `${serviceName} - 90 min` },
      '120': { duration: '120 min', price: '5,000 RSD', serviceId: `${serviceName} - 120 min` }
    };
    return options[duration];
  };

  // Map frontend keys to booking system service names
  const serviceKeyToBookingName = {
    'traditional': 'Tradicionalna tajlandska masaža',
    'aroma': 'Aroma terapija',
    'hotStone': 'Masaža toplim uljem',
    'royal': 'Glava, vrat, ramena i leđa',
    'foot': 'Masaža stopala',
    'couple': 'Masaža za parove',
    'sports': 'Sportska masaža',
    'aromaDeepTissue': 'Aroma duboko tkivo',
    'aromaHotStone': 'Aromaterapija & topli kamen',
    'aromaThaiHerbal': 'Aroma sa toplim biljnim kompresama',
    'thaiHerbal': 'Thai masaža sa toplim biljnim kompresama'
  };

  // Get discount badge image based on service discount
  const getDiscountBadge = (serviceKey) => {
    const bookingName = serviceKeyToBookingName[serviceKey];
    const discount = serviceDiscounts[bookingName] || 0;
    if (discount === 5) {
      return "https://customer-assets.emergentagent.com/job_spa-form-repair/artifacts/xdhih1ft_-5%25.png";
    } else if (discount === 10) {
      return "https://customer-assets.emergentagent.com/job_spa-form-repair/artifacts/zo9fsp4t_-10%25.png";
    } else if (discount === 15) {
      return "https://customer-assets.emergentagent.com/job_spa-form-repair/artifacts/0c5tq3wd_-15%25.png";
    }
    return null; // No discount
  };

  // Get discount percentage for a service
  const getServiceDiscount = (serviceKey) => {
    const bookingName = serviceKeyToBookingName[serviceKey];
    return serviceDiscounts[bookingName] || 0;
  };

  // 🔒 DO NOT MODIFY — STABLE VERIFIED LOGIC (Bua Luang - SNAPSHOT: BuaLuang-FRONTEND-STABLE-01)
  // Handle booking button click - navigate to Contact form
  // ✅ FIX: serviceName must be Serbian name (for backend), durationMinutes must be NUMBER
  // ✅ NEW: Pass serviceKey, lang, localizedName, description, benefits for detailed message
  // ✅ NEW 2025-01-09: Pass pricing info (originalPrice, finalPrice, discount) for detailed booking message
  const handleBookClick = (serviceName, durationMinutes, serviceKey) => {
    // Ensure duration is a number
    const durationNum = typeof durationMinutes === 'number' ? durationMinutes : parseInt(durationMinutes, 10) || 60;
    
    const serviceWithDuration = `${serviceName} - ${durationNum} min`;
    
    // Get localized service data from translations
    const t = translations[currentLanguage] || translations['sr'];
    
    // ✅ NEW: Get pricing info from API data
    const massageDetails = getMassageDetails(serviceKey, serviceName);
    const originalPrice = massageDetails?.originalPrice 
      ? parseInt(String(massageDetails.originalPrice).replace(/[^\d]/g, ''), 10) || 0 
      : 0;
    const finalPrice = massageDetails?.price 
      ? parseInt(String(massageDetails.price).replace(/[^\d]/g, ''), 10) || 0 
      : 0;
    const discountPercent = massageDetails?.discount || 0;
    const hasDiscount = discountPercent > 0 && originalPrice > finalPrice;
    
    // Map serviceKey to translation keys
    const translationKeyMap = {
      'traditional': { name: 'traditionalMassage', desc: 'traditionalMassageDesc', benefits: ['traditionalBenefit1', 'traditionalBenefit2', 'traditionalBenefit3'] },
      'aroma': { name: 'aromaTherapy', desc: 'oilMassageDesc', benefits: ['oilBenefit1', 'oilBenefit2', 'oilBenefit3'] },
      'hotStone': { name: 'hotStone', desc: 'hotStoneDesc', benefits: ['hotStoneBenefit1', 'hotStoneBenefit2', 'hotStoneBenefit3'] },
      'royal': { name: 'royalMassage', desc: 'royalMassageDesc', benefits: ['royalBenefit1', 'royalBenefit2', 'royalBenefit3', 'royalBenefit4'] },
      'foot': { name: 'footMassage', desc: 'footMassageDesc', benefits: ['footBenefit1', 'footBenefit2', 'footBenefit3'] },
      'aromaDeepTissue': { name: 'aromaDeepTissueMassage', desc: 'aromaDeepTissueMassageDesc', benefits: ['aromaDeepTissueBenefit1', 'aromaDeepTissueBenefit2', 'aromaDeepTissueBenefit3', 'aromaDeepTissueBenefit4'] },
      'aromaHotStone': { name: 'aromaHotStoneMassage', desc: 'aromaHotStoneMassageDesc', benefits: ['aromaHotStoneBenefit1', 'aromaHotStoneBenefit2', 'aromaHotStoneBenefit3'] },
      'aromaThaiHerbal': { name: 'aromaThaiHerbalMassage', desc: 'aromaThaiHerbalMassageDesc', benefits: ['aromaThaiHerbalBenefit1', 'aromaThaiHerbalBenefit2', 'aromaThaiHerbalBenefit3'] },
      'thaiHerbal': { name: 'thaiHerbalMassage', desc: 'thaiHerbalMassageDesc', benefits: ['thaiHerbalBenefit1', 'thaiHerbalBenefit2', 'thaiHerbalBenefit3'] }
    };
    
    const keyMap = translationKeyMap[serviceKey] || { name: serviceKey, desc: '', benefits: [] };
    const localizedName = t[keyMap.name] || serviceName;
    const localizedDesc = t[keyMap.desc] || '';
    const localizedBenefits = keyMap.benefits.map(b => t[b] || '').filter(Boolean).join(', ');
    
    const params = new URLSearchParams({
      service: serviceWithDuration,
      serviceKey: serviceKey,
      lang: currentLanguage,
      localizedName: localizedName,
      localizedDesc: localizedDesc,
      localizedBenefits: localizedBenefits,
      duration: String(durationNum),
      // ✅ NEW 2025-01-09: Pricing info for detailed booking message
      originalPrice: String(originalPrice),
      finalPrice: String(finalPrice),
      discountPercent: String(discountPercent),
      hasDiscount: String(hasDiscount)
    });
    
    console.log('📍 Navigating to /contact with params:', params.toString());
    console.log('📍 Service (Serbian name):', serviceName);
    console.log('📍 Service Key:', serviceKey);
    console.log('📍 Language:', currentLanguage);
    console.log('📍 Duration (number):', durationNum);
    console.log('📍 Localized Name:', localizedName);
    console.log('📍 Pricing:', { originalPrice, finalPrice, discountPercent, hasDiscount });
    
    navigate(`/contact?${params.toString()}`);
  };

  // ❌ REMOVED - Frontend MUST NOT calculate discounts!
  // Backend already provides final_price with discount applied.
  // This function was causing DOUBLE discount problem.

  // Helper to update duration for a specific service
  const updateDuration = (serviceKey, newDuration) => {
    console.log(`🔄 updateDuration called: serviceKey="${serviceKey}", newDuration="${newDuration}"`);
    setDurations(prev => ({ ...prev, [serviceKey]: newDuration }));
    
    // Reset couples selections when duration changes for couples massage
    if (serviceKey === 'sports') {
      console.log(`🎯 Updating couples massage duration to ${newDuration}`);
      setCouplesSelections({
        duration: newDuration,
        person1Massage1: null,
        person1Massage2: null,
        person2Massage1: null,
        person2Massage2: null
      });
      console.log(`✅ Couples selections reset with duration: ${newDuration}`);
    }
  };

  const calculateCouplesPrice = () => {
    let totalPrice = 0;
    
    // Add person 1 massages
    if (couplesSelections.person1Massage1) {
      totalPrice += couplesSelections.person1Massage1.price || 0;
    }
    if (couplesSelections.person1Massage2) {
      totalPrice += couplesSelections.person1Massage2.price || 0;
    }
    
    // Add person 2 massages
    if (couplesSelections.person2Massage1) {
      totalPrice += couplesSelections.person2Massage1.price || 0;
    }
    if (couplesSelections.person2Massage2) {
      totalPrice += couplesSelections.person2Massage2.price || 0;
    }
    
    // ❌ DO NOT APPLY DISCOUNT ON FRONTEND!
    // Backend already provides prices with discounts applied.
    // Just return the sum of final prices from API.
    
    console.log(`💰 Couples total price (from API final prices): ${totalPrice} RSD`);
    
    return totalPrice;  // NO DISCOUNT CALCULATION!
  };

  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  // Card slide-in animation on scroll
  useEffect(() => {
    const cards = document.querySelectorAll('.massage-card');
    if (cards.length === 0) return;
    
    const cardsGrid = document.querySelector('.services-grid');
    if (!cardsGrid) return;
    
    const gridStyle = window.getComputedStyle(cardsGrid);
    const gridColumns = gridStyle.gridTemplateColumns;
    const columns = gridColumns.split(' ').length;
    
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
  }, [isMobile]);

  // Logo transformation and parallax effects on scroll
  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY;
      const massageHeroSection = document.querySelector('.massage-hero-fixed');
      const massageHeroLogo = document.querySelector('.massage-hero-logo');
      const massageHeroTitle = document.querySelector('.massage-hero-title');
      const massageHeroSubtitle = document.querySelector('.massage-hero-subtitle');
      
      if (!massageHeroSection || !massageHeroLogo) return;
      
      const heroHeight = massageHeroSection.offsetHeight;
      const scrollPercent = Math.min(scrollPosition / heroHeight, 1);
      
      if (scrollPercent > 0.05) {
        // Scroll down - transform logo with fade and blur
        const opacity = Math.max(1 - (scrollPercent - 0.05) * 3, 0);
        const scale = Math.max(1 - (scrollPercent - 0.05) * 1.5, 0.2);
        
        massageHeroLogo.style.opacity = opacity;
        massageHeroLogo.style.transform = `scale(${scale})`;
        massageHeroLogo.style.filter = `blur(${(scrollPercent - 0.05) * 15}px)`;
        
        // Fade out title and subtitle
        if (massageHeroTitle) {
          massageHeroTitle.style.opacity = opacity;
          massageHeroTitle.style.transform = `translateY(${scrollPercent * 50}px)`;
        }
        if (massageHeroSubtitle) {
          massageHeroSubtitle.style.opacity = opacity;
          massageHeroSubtitle.style.transform = `translateY(${scrollPercent * 50}px)`;
        }
      } else {
        // Scroll up - restore logo
        massageHeroLogo.style.opacity = 1;
        massageHeroLogo.style.transform = 'scale(1)';
        massageHeroLogo.style.filter = 'blur(0px)';
        
        // Restore title and subtitle
        if (massageHeroTitle) {
          massageHeroTitle.style.opacity = 1;
          massageHeroTitle.style.transform = 'translateY(0)';
        }
        if (massageHeroSubtitle) {
          massageHeroSubtitle.style.opacity = 1;
          massageHeroSubtitle.style.transform = 'translateY(0)';
        }
      }
      
      // CTA section - no fade animation
      const ctaSection = document.querySelector('.cta-section');
      if (ctaSection) {
        ctaSection.style.opacity = 1;
        ctaSection.style.transform = 'translateY(0)';
      }
    };
    
    const throttledHandleScroll = throttle(handleScroll, 16);
    window.addEventListener('scroll', throttledHandleScroll, { passive: true });
    return () => window.removeEventListener('scroll', throttledHandleScroll);
  }, []);

  // Parallax effect for content sections
  useEffect(() => {
    const handleParallaxScroll = () => {
      const scrolled = window.scrollY;
      const massageHeroSection = document.querySelector('.massage-hero-fixed');
      
      if (!massageHeroSection) return;
      
      const heroHeight = massageHeroSection.offsetHeight;
      
      // Apply parallax to sections after hero
      if (scrolled > heroHeight * 0.3) {
        const parallaxContent = document.querySelector('.massage-parallax-content');
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

  const traditionalDetails = getMassageDetails('traditional', 'Tradicionalna tajlandska masaža');
  const aromaDetails = getMassageDetails('aroma', 'Aroma terapija');
  const hotStoneDetails = getMassageDetails('hotStone', 'Masaža toplim uljem');
  const royalDetails = getMassageDetails('royal', 'Glava, vrat, ramena i leđa');
  const footDetails = getMassageDetails('foot', 'Masaža stopala');
  const aromaDeepTissueDetails = getMassageDetails('aromaDeepTissue', 'Aroma duboko tkivo');
  const aromaHotStoneDetails = getMassageDetails('aromaHotStone', 'Aromaterapija & topli kamen');
  const aromaThaiHerbalDetails = getMassageDetails('aromaThaiHerbal', 'Aroma sa toplim biljnim kompresama');
  const thaiHerbalDetails = getMassageDetails('thaiHerbal', 'Thai masaža sa toplim biljnim kompresama');
  
  const massageServices = [
    {
      key: 'traditional',
      name: translate("traditionalMassage"),
      duration: traditionalDetails.duration,
      price: traditionalDetails.price,
      originalPrice: traditionalDetails.originalPrice,
      discount: traditionalDetails.discount,
      serviceId: traditionalDetails.serviceId,
      description: translate("traditionalMassageDesc"),
      benefits: [translate("traditionalBenefit1"), translate("traditionalBenefit2"), translate("traditionalBenefit3")],
      popular: true,
      hasDurationOptions: true
    },
    {
      key: 'aroma',
      name: translate("aromaTherapy"),
      duration: aromaDetails.duration,
      price: aromaDetails.price,
      originalPrice: aromaDetails.originalPrice,
      discount: aromaDetails.discount,
      serviceId: aromaDetails.serviceId,
      description: translate("oilMassageDesc"),
      benefits: [translate("oilBenefit1"), translate("oilBenefit2"), translate("oilBenefit3")],
      hasDurationOptions: true
    },
    {
      key: 'hotStone',
      name: translate("hotStone"),
      duration: hotStoneDetails.duration,
      price: hotStoneDetails.price,
      originalPrice: hotStoneDetails.originalPrice,
      discount: hotStoneDetails.discount,
      serviceId: hotStoneDetails.serviceId,
      description: translate("hotStoneDesc"),
      benefits: [translate("hotStoneBenefit1"), translate("hotStoneBenefit2"), translate("hotStoneBenefit3")],
      popular: false,
      hasDurationOptions: true,
      customDurations: ['60', '90'] // Only 60 and 90 min
    },
    {
      key: 'royal',
      name: translate("royalMassage"),
      duration: royalDetails.duration,
      price: royalDetails.price,
      originalPrice: royalDetails.originalPrice,
      discount: royalDetails.discount,
      serviceId: royalDetails.serviceId,
      description: translate("royalMassageDesc"),
      benefits: [translate("royalBenefit1"), translate("royalBenefit2"), translate("royalBenefit3"), translate("royalBenefit4")],
      popular: true,
      hasDurationOptions: true,
      customDurationLabels: {
        '60': '30 min',
        '90': '45 min',
        '120': '60 min'
      }
    },
    {
      key: 'foot',
      name: translate("footMassage"),
      duration: footDetails.duration,
      price: footDetails.price,
      originalPrice: footDetails.originalPrice,
      discount: footDetails.discount,
      serviceId: footDetails.serviceId,
      description: translate("footMassageDesc"),
      benefits: [translate("footBenefit1"), translate("footBenefit2"), translate("footBenefit3")],
      popular: false,
      hasDurationOptions: true,
      customDurationLabels: {
        '60': '30 min',
        '90': '45 min',
        '120': '60 min'
      }
    },
    {
      key: 'aromaDeepTissue',
      name: translate("aromaDeepTissueMassage"),
      duration: aromaDeepTissueDetails.duration,
      price: aromaDeepTissueDetails.price,
      originalPrice: aromaDeepTissueDetails.originalPrice,
      discount: aromaDeepTissueDetails.discount,
      serviceId: aromaDeepTissueDetails.serviceId,
      description: translate("aromaDeepTissueMassageDesc"),
      benefits: [
        translate("aromaDeepTissueBenefit1"), 
        translate("aromaDeepTissueBenefit2"), 
        translate("aromaDeepTissueBenefit3"),
        translate("aromaDeepTissueBenefit4")
      ],
      popular: false,
      hasDurationOptions: true,
      customDurations: ['60', '90'] // Only 60 and 90 min
    },
    {
      key: 'aromaHotStone',
      name: translate("aromaHotStoneMassage"),
      duration: aromaHotStoneDetails.duration,
      price: aromaHotStoneDetails.price,
      originalPrice: aromaHotStoneDetails.originalPrice,
      discount: aromaHotStoneDetails.discount,
      serviceId: aromaHotStoneDetails.serviceId,
      description: translate("aromaHotStoneMassageDesc"),
      benefits: [
        translate("aromaHotStoneBenefit1"), 
        translate("aromaHotStoneBenefit2"), 
        translate("aromaHotStoneBenefit3"),
        translate("aromaHotStoneBenefit4")
      ],
      popular: false,
      hasDurationOptions: true,
      customDurations: ['90', '120'] // Only 90 and 120 min
    },
    {
      key: 'aromaThaiHerbal',
      name: translate("aromaThaiHerbalMassage"),
      duration: aromaThaiHerbalDetails.duration,
      price: aromaThaiHerbalDetails.price,
      originalPrice: aromaThaiHerbalDetails.originalPrice,
      discount: aromaThaiHerbalDetails.discount,
      serviceId: aromaThaiHerbalDetails.serviceId,
      description: translate("aromaThaiHerbalMassageDesc"),
      benefits: [
        translate("aromaThaiHerbalBenefit1"), 
        translate("aromaThaiHerbalBenefit2"), 
        translate("aromaThaiHerbalBenefit3"),
        translate("aromaThaiHerbalBenefit4")
      ],
      popular: false,
      hasDurationOptions: true,
      customDurations: ['90', '120'] // Only 90 and 120 min
    },
    {
      key: 'thaiHerbal',
      name: translate("thaiHerbalMassage"),
      duration: thaiHerbalDetails.duration,
      price: thaiHerbalDetails.price,
      originalPrice: thaiHerbalDetails.originalPrice,
      discount: thaiHerbalDetails.discount,
      serviceId: thaiHerbalDetails.serviceId,
      description: translate("thaiHerbalMassageDesc"),
      benefits: [
        translate("thaiHerbalBenefit1"), 
        translate("thaiHerbalBenefit2"), 
        translate("thaiHerbalBenefit3"),
        translate("thaiHerbalBenefit4")
      ],
      popular: false,
      hasDurationOptions: true,
      customDurations: ['90', '120'] // Only 90 and 120 min
    }
  ];

  return (
    <div id="masaze" className="massage-container" style={{ scrollMarginTop: '80px' }}>
      {/* SEO Meta Tags */}
      <Helmet>
        <title>Thai Masaže Beograd | Cenovnik & Online Rezervacija - Bua Luang Spa</title>
        <meta name="description" content="Tradicionalne thai masaže u Beogradu. Aroma terapija, masaža toplim uljem, masaža za parove, refleksna masaža. Cene od 2,400 RSD. Rezervišite online na Bua Luang Thai Spa!" />
        <meta name="keywords" content="thai masaža beograd, tajlandska masaža, masaža za parove, aroma terapija, masaža toplim uljem, refleksna masaža, cenovnik masaža beograd" />
        <link rel="canonical" href="https://www.bualuangthaispa.rs/massage" />
        <meta property="og:title" content="Thai Masaže Beograd | Cenovnik & Rezervacija - Bua Luang" />
        <meta property="og:url" content="https://www.bualuangthaispa.rs/massage" />
        <meta property="og:type" content="website" />
      </Helmet>
      
      {/* Fixed Video Hero Section */}
      <section className="massage-hero-fixed">
        <div className="massage-hero-video-container">
          <video 
            autoPlay 
            muted 
            loop 
            playsInline
            preload="auto"
            className="massage-hero-video"
          >
            {/* Mobile gets optimized smaller video (2.75 MB vs 4.69 MB) */}
            {isMobile ? (
              <source src="https://customer-assets.emergentagent.com/job_thaispa-mobile/artifacts/90yarq0d_MASAZE.mp4" type="video/mp4" />
            ) : (
              <source src="https://customer-assets.emergentagent.com/job_goldenlinesdesign/artifacts/jkumv1ek_MASAZE.mp4" type="video/mp4" />
            )}
          </video>
          <div className="massage-hero-overlay"></div>
        </div>
        
        <div className="massage-hero-content">
          <div className="massage-hero-logo">
            <img 
              src="https://customer-assets.emergentagent.com/job_83ed575e-3634-46be-8586-79a3348def97/artifacts/7sfhgz1m_Bua%20luang%20logo.png"
              alt="Bua Luang Logo"
              className="hero-logo-image"
            />
          </div>
          <h1 className="massage-hero-title">{translate("massageHeroTitle")}</h1>
          <div className="massage-hero-divider"></div>
          <p className="massage-hero-subtitle">
            {translate("massageHeroSubtitle")}
          </p>
        </div>
      </section>

      {/* Parallax Content Section */}
      <div className="massage-parallax-content">

      {/* Services Grid */}
      <section className="services-section">
        <div className="services-grid">
          
          {/* Masaža za parove Card sa dropdown menijima */}
          <CouplesMassageCard
            translate={translate}
            currentLanguage={currentLanguage}
            durations={durations}
            updateDuration={updateDuration}
            couplesSelections={couplesSelections}
            setCouplesSelections={setCouplesSelections}
            dropdownOpen={dropdownOpen}
            setDropdownOpen={setDropdownOpen}
          />

          {massageServices.map((service, index) => {
            // Regular massage cards
            return (
            <Card key={index} className="massage-card">
              {service.popular && (
                <Badge className="popular-badge">
                  <Star className="w-3 h-3 mr-1" />
                  {translate("mostPopular")}
                </Badge>
              )}
              
              <CardHeader>
                <CardTitle className="massage-name">{service.name}</CardTitle>
                
                {/* DYNAMIC Duration buttons from API data - use apiKey (Serbian name) for lookup */}
                {service.hasDurationOptions && (() => {
                  // ✅ FIX: Use Serbian name (apiKey) for API lookup, not translated name
                  const apiKey = serviceKeyToBookingName[service.key];
                  const variants = apiServices[apiKey] || [];
                  
                  if (variants.length > 0) {
                    return (
                      <div style={{
                        display: 'flex',
                        gap: '0.5rem',
                        marginTop: '0.75rem',
                        marginBottom: '0.75rem'
                      }}>
                        {variants.map((variant) => (
                          <button
                            key={variant.duration}
                            onClick={() => updateDuration(service.key, String(variant.duration))}
                            style={{
                              flex: 1,
                              padding: '0.5rem',
                              border: durations[service.key] === String(variant.duration) ? '2px solid #d4af37' : '1px solid #444',
                              backgroundColor: durations[service.key] === String(variant.duration) ? 'rgba(212, 175, 55, 0.1)' : 'transparent',
                              color: '#d4af37',
                              borderRadius: '8px',
                              cursor: 'pointer',
                              fontSize: '0.875rem',
                              fontWeight: durations[service.key] === String(variant.duration) ? 'bold' : 'normal',
                              transition: 'all 0.3s ease'
                            }}
                          >
                            {variant.duration} {translate('min', 'min')}
                          </button>
                        ))}
                      </div>
                    );
                  }
                  
                  // Fallback: Show hardcoded durations if API doesn't have data
                  const fallbackDurations = service.customDurations || ['60', '90', '120'];
                  return (
                    <div style={{
                      display: 'flex',
                      gap: '0.5rem',
                      marginTop: '0.75rem',
                      marginBottom: '0.75rem'
                    }}>
                      {fallbackDurations.map((dur) => (
                        <button
                          key={dur}
                          onClick={() => updateDuration(service.key, dur)}
                          style={{
                            flex: 1,
                            padding: '0.5rem',
                            border: durations[service.key] === dur ? '2px solid #d4af37' : '1px solid #444',
                            backgroundColor: durations[service.key] === dur ? 'rgba(212, 175, 55, 0.1)' : 'transparent',
                            color: '#d4af37',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            fontSize: '0.875rem',
                            fontWeight: durations[service.key] === dur ? 'bold' : 'normal',
                            transition: 'all 0.3s ease'
                          }}
                        >
                          {service.customDurationLabels?.[dur] || `${dur} ${translate('min', 'min')}`}
                        </button>
                      ))}
                    </div>
                  );
                })()}
                
                <div className="massage-meta">
                  <div className="duration">
                    <Clock className="w-4 h-4" />
                    <span>{service.duration}</span>
                  </div>
                  {/* 🔒 DO NOT MODIFY — STABLE VERIFIED PRICE DISPLAY (Bua Luang - SNAPSHOT: BuaLuang-FRONTEND-STABLE-01) */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    {service.discount > 0 && getDiscountBadge(service.key) && (
                      <img 
                        src={getDiscountBadge(service.key)} 
                        alt={`-${service.discount}%`}
                        style={{ width: '38px', height: '38px', objectFit: 'contain' }}
                      />
                    )}
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                      {service.discount > 0 && service.originalPrice ? (
                        <>
                          {/* Original price (strikethrough) - ONLY from API */}
                          <div className="price" style={{ textDecoration: 'line-through', color: '#888', fontSize: '0.9em' }}>
                            {service.originalPrice}
                          </div>
                          {/* Final price (red, bold) - ONLY from API - NO CALCULATIONS! */}
                          <div className="price" style={{ color: '#e63946', fontWeight: 'bold' }}>
                            {service.price}
                          </div>
                        </>
                      ) : (
                        <div className="price">{service.price}</div>
                      )}
                    </div>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent>
                <p className="massage-description">{service.description}</p>
                
                <div className="benefits">
                  <h4 className="benefits-title">{translate("benefits")}</h4>
                  <ul className="benefits-list">
                    {service.benefits.map((benefit, idx) => (
                      <li key={idx} className="benefit-item">{benefit}</li>
                    ))}
                  </ul>
                </div>
                
                <button 
                  type="button"
                  className="book-button w-full" 
                  style={{
                    backgroundColor: '#d4af37',
                    color: '#1a1a1a',
                    border: 'none',
                    padding: '12px 24px',
                    borderRadius: '8px',
                    fontSize: '16px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    width: '100%'
                  }}
                  onClick={() => {
                    // ✅ FIX: Use Serbian service name (apiKey) for booking, not translated name
                    // ✅ NEW: Pass serviceKey for detailed localized message
                    const apiKey = serviceKeyToBookingName[service.key];
                    const durationNum = parseInt(durations[service.key], 10) || 60;
                    console.log('🔵 BUTTON CLICKED!', apiKey, durationNum, service.key);
                    handleBookClick(apiKey, durationNum, service.key);
                  }}
                >
                  {translate("bookAppointment")}
                </button>
              </CardContent>
            </Card>
            );
          })}
        </div>
      </section>

      {/* Call to Action */}
      <section className="cta-section">
        <div className="cta-content">
          <h2 className="cta-title">{translate("massageCtaTitle")}</h2>
          <p className="cta-subtitle">{translate("massageCtaSubtitle")}</p>
          <div className="cta-buttons">
            {/* ZADATAK 1: Uklonjen dugme "Rezervišite sada" - ostavljen samo "Pogledajte SPA tretmane" */}
            {/* SCROLL-TO-TOP: Navigacija na /spa#top za automatski scroll na vrh */}
            <Button asChild variant="outline" size="lg" className="cta-button-secondary">
              <Link to="/spa#top">{translate("massageCtaButtonSecondary")}</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Empty parallax section for spacing - like Home page */}
      <section className="massage-testimonial">
        {/* Empty section for consistent spacing */}
      </section>

      </div> {/* Close parallax-content */}
    </div>
  );
};

export default Massage;