import React, { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Helmet } from "react-helmet";
import { useLanguage } from "../context/LanguageContext";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { throttle } from "../utils/debounce";
import { getSEO } from "../utils/seoConfig";

const Home = ({ lang }) => {
  const { translate, setLanguage, language } = useLanguage();
  const heroTitleRef = useRef(null);
  const [scrollY, setScrollY] = useState(0);
  const videoRef = useRef(null);
  const [isMobile, setIsMobile] = useState(false);
  const [currentLang, setCurrentLang] = useState(lang || language || 'sr');
  const [isVoucherModalOpen, setIsVoucherModalOpen] = useState(false);

  // Sakrij/prikaži kontakt sekciju u footeru kada se modal otvori/zatvori
  useEffect(() => {
    const footerContent = document.querySelector('.footer-content');
    if (footerContent) {
      footerContent.style.display = isVoucherModalOpen ? 'none' : '';
    }
  }, [isVoucherModalOpen]);

  // Auto-set language if lang prop is provided
  useEffect(() => {
    if (lang) {
      setLanguage(lang);
      setCurrentLang(lang);
    }
  }, [lang, setLanguage]);

  // Track language changes
  useEffect(() => {
    setCurrentLang(language);
  }, [language]);

  // Get SEO config based on current language
  const homeSEO = currentLang === 'en' ? getSEO('homeEn') : getSEO('home');

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

  // Ensure video plays
  useEffect(() => {
    const video = videoRef.current;
    if (video) {
      video.play().catch(err => console.log('Video autoplay:', err));
    }
  }, []);

  useEffect(() => {
    const heroLogo = document.getElementById('hero-logo');
    
    const handleScroll = () => {
      const scrollPosition = window.scrollY;
      const heroSection = document.getElementById('hero-section');
      
      if (!heroSection || !heroLogo) return;
      
      const heroHeight = heroSection.offsetHeight;
      const scrollPercent = Math.min(scrollPosition / heroHeight, 1);
      
      if (scrollPercent > 0.05) {
        // Scroll down - transform logo to lotus IMMEDIATELY and FASTER
        const opacity = Math.max(1 - (scrollPercent - 0.05) * 3, 0);
        const scale = Math.max(1 - (scrollPercent - 0.05) * 1.5, 0.2);
        
        heroLogo.style.opacity = opacity;
        heroLogo.style.transform = `scale(${scale})`;
        heroLogo.style.filter = `blur(${(scrollPercent - 0.05) * 15}px)`;
        
        // Add lotus petals effect immediately
        if (scrollPercent > 0.1 && !heroLogo.classList.contains('lotus-transform')) {
          heroLogo.classList.add('lotus-transform');
        }
      } else {
        // Scroll up - restore logo
        heroLogo.style.opacity = 1;
        heroLogo.style.transform = 'scale(1)';
        heroLogo.style.filter = 'blur(0px)';
        heroLogo.classList.remove('lotus-transform');
      }
    };
    
    const throttledHandleScroll = throttle(handleScroll, 16);
    window.addEventListener('scroll', throttledHandleScroll);
    return () => window.removeEventListener('scroll', throttledHandleScroll);
  }, []);

  // Parallax effect for sections after Buddha
  useEffect(() => {
    const handleParallaxScroll = () => {
      const scrolled = window.scrollY;
      const heroSection = document.getElementById('hero-section');
      const buddhaHero = document.getElementById('buddha-hero');
      const buddhaOverlay = document.getElementById('buddha-overlay');
      
      if (!heroSection) return;
      
      const heroHeight = 110 * window.innerHeight / 100; // 110vh in pixels
      const buddhaStartTrigger = heroHeight * 0.5; // Buddha starts moving at 50%
      
      // Buddha movement - FASTER movement
      if (scrolled > buddhaStartTrigger) {
        // Calculate how much to move - FASTER now
        const moveAmount = (scrolled - buddhaStartTrigger) * 1.2; // 1.2 for FASTER movement (was 0.6)
        
        // Move Buddha hero up FAST (NO FADE)
        heroSection.style.transform = `translateY(-${moveAmount}px)`;
        heroSection.style.opacity = 1; // Keep full opacity
      } else {
        // Reset Buddha when scrolling back to top
        heroSection.style.transform = 'translateY(0)';
        heroSection.style.opacity = 1;
      }
      
      // Apply parallax only to sections after hero
      if (scrolled > heroHeight) {
        // Quote section moves faster up
        const quoteSection = document.querySelector('.pim-quote');
        if (quoteSection) {
          const quoteFastSpeed = 0.8; // Faster parallax for quote section
          const quoteYPos = -(scrolled - heroHeight) * quoteFastSpeed;
          quoteSection.style.transform = `translateY(${quoteYPos}px)`;
        }
        
        // Other sections move at normal speed
        const otherSections = document.querySelectorAll('.pim-welcome, .pim-philosophy');
        otherSections.forEach((section) => {
          const speed = 0.5; // Normal parallax speed
          const yPos = -(scrolled - heroHeight) * speed;
          section.style.transform = `translateY(${yPos}px)`;
        });
      }
    };

    const throttledHandleParallaxScroll = throttle(handleParallaxScroll, 16);
    window.addEventListener('scroll', throttledHandleParallaxScroll);
    return () => window.removeEventListener('scroll', throttledHandleParallaxScroll);
  }, []);

  return (
    <div className="pim-style-homepage">
      {/* SEO Meta Tags */}
      <Helmet>
        <title>{homeSEO.title}</title>
        <meta name="description" content={homeSEO.description} />
        <meta name="keywords" content={homeSEO.keywords} />
        <link rel="canonical" href={homeSEO.canonical} />
        <meta property="og:type" content="website" />
        <meta property="og:url" content={homeSEO.canonical} />
        <meta property="og:title" content={currentLang === 'en' ? "Bua Luang Thai Spa Belgrade" : "Bua Luang Thai Spa Beograd"} />
        <meta property="og:description" content={currentLang === 'en' ? "Thai massages & luxury SPA treatments. Online booking and gift vouchers." : "Thai masaže i luksuzni SPA tretmani. Online rezervacije i poklon vaučeri."} />
        <meta property="og:image" content={homeSEO.ogImage} />
        <meta name="twitter:card" content="summary_large_image" />
        <link rel="alternate" href="https://www.bualuangthaispa.rs/" hreflang="sr-RS" />
        <link rel="alternate" href="https://www.bualuangthaispa.rs/en" hreflang="en" />
        <link rel="alternate" href="https://www.bualuangthaispa.rs/" hreflang="x-default" />
      </Helmet>
      
      {/* Fixed Video Background - No overlay filter */}
      <div className="fixed-video-background">
        <video 
          ref={videoRef}
          autoPlay 
          loop 
          muted 
          playsInline
          preload="auto"
          className="global-fixed-video"
        >
          {/* Mobile gets optimized smaller video (2.62 MB vs 4.09 MB) */}
          {isMobile ? (
            <source src="https://customer-assets.emergentagent.com/job_thaispa-mobile/artifacts/fmiknawg_POCETNA.mp4" type="video/mp4" />
          ) : (
            <source src="https://customer-assets.emergentagent.com/job_goldenlinesdesign/artifacts/flpuvnqw_POCETNA.mp4" type="video/mp4" />
          )}
        </video>
      </div>

      {/* Hero Banner */}
      <section className="pim-hero" id="hero-section">
        <div className="pim-hero-overlay" id="buddha-overlay"></div>
        <div className="pim-hero-content">
          <img 
            src="https://customer-assets.emergentagent.com/job_serene-retreat-1/artifacts/r2vm59ex_Bualuang%20logo%20senka.png"
            alt="Bua Luang Thai Spa Logo"
            className="hero-logo-animated"
            id="hero-logo"
          />
        </div>
      </section>

      {/* Second Hero section removed as requested */}

      {/* Container for parallax sections that go over hero */}
      <div style={{position: 'relative', zIndex: 20, marginTop: '110vh', background: 'transparent'}}>
        {/* Transparent footer bar below Buddha */}
        <div className="transparent-footer-bar"></div>

        {/* Welcome Section - Dobro došli */}
        <section className="pim-welcome" id="welcome-section">
          {/* SVG sa pozadinom koja tačno prati krive linije */}
          <div className="pim-welcome-svg-container">
            <svg className="pim-welcome-svg" viewBox="0 0 1440 600" preserveAspectRatio="none">
              {/* Ispuna TAČNO između gornje i donje krive linije */}
              <path 
                className="pim-welcome-fill"
                d="M0,80 Q360,0 720,60 Q1080,120 1440,40 
                   L1440,520 Q1080,600 720,540 Q360,480 0,560 Z"
              />
              {/* Gornja zlatna linija */}
              <path 
                className="pim-welcome-curve-line"
                d="M0,80 Q360,0 720,60 Q1080,120 1440,40"
              />
              {/* Donja zlatna linija - ISTI path rotiran 180 stepeni */}
              <path 
                className="pim-welcome-curve-line"
                d="M0,80 Q360,0 720,60 Q1080,120 1440,40"
                transform="rotate(180, 720, 300)"
              />
            </svg>
            
            {/* Sadržaj pozicioniran preko SVG-a */}
            <div className="pim-welcome-content-overlay">
              <h3 className="pim-welcome-subtitle">{translate("welcomeSubtitle")}</h3>
              <h2 className="pim-welcome-title">{translate("welcomeTitle")}</h2>
              <div className="pim-welcome-content">
                <div className="pim-welcome-text">
                  <p>{translate("welcomeText1")}</p>
                  <p>{translate("welcomeText2")}</p>
                </div>
              </div>
            </div>
          </div>
        </section>

      {/* Quote Section - Normal */}
      <section className="pim-quote">
        <div className="pim-quote-content">
          <p className="pim-quote-text">{translate("quoteText")}</p>
          <p className="pim-quote-author">{translate("quoteAuthor")}</p>
          <Button asChild className="pim-quote-button">
            {/* ZADATAK 2: Vodi na Masaže stranicu */}
            <Link to="/massage">{translate("reserveOnline")}</Link>
          </Button>
        </div>
      </section>

      {/* Philosophy Section - sa SVG krivim linijama identično kao Dobrodošli */}
      <section className="pim-philosophy" id="philosophy-section">
        <div className="pim-welcome-svg-container">
          <svg className="pim-welcome-svg" viewBox="0 0 1440 787" preserveAspectRatio="none">
            {/* Transparentna pozadina između linija */}
            <path 
              className="pim-welcome-fill"
              d="M0,80 Q360,0 720,60 Q1080,120 1440,40 
                 L1440,707 Q1080,787 720,727 Q360,667 0,747 Z"
            />
            {/* Gornja zlatna linija */}
            <path 
              className="pim-welcome-curve-line"
              d="M0,80 Q360,0 720,60 Q1080,120 1440,40"
            />
            {/* Donja zlatna linija - rotirana 180 stepeni */}
            <path 
              className="pim-welcome-curve-line"
              d="M0,80 Q360,0 720,60 Q1080,120 1440,40"
              transform="rotate(180, 720, 393.5)"
            />
          </svg>
          
          {/* Sadržaj pozicioniran preko SVG-a */}
          <div className="pim-welcome-content-overlay">
            <h2 className="pim-welcome-title" style={{fontSize: '3rem'}}>{translate("philosophyTitle")}</h2>
            <div className="pim-welcome-content">
              <div className="pim-welcome-text">
                <p>{translate("philosophyText1")}</p>
                <p>{translate("philosophyText2")}</p>
                <p>{translate("philosophyText3")}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Gift Voucher Section */}
      <section className="pim-gift">
        <h2 className="pim-gift-title">{translate("giftTitle")}</h2>
        <p className="pim-gift-subtitle">{translate("giftSubtitle")}</p>
        <div className="pim-gift-voucher-showcase">
          <img 
            src="https://customer-assets.emergentagent.com/job_serene-thai-spa/artifacts/1uemvsqg_Poklon%20vaucer%20sa%20kovertom%20srpski.png" 
            alt="Poklon Vaucer"
            className="pim-gift-voucher-breathing"
          />
        </div>
        <div className="pim-gift-buttons">
          <Dialog open={isVoucherModalOpen} onOpenChange={setIsVoucherModalOpen}>
            <DialogTrigger asChild>
              <Button className="pim-gift-button-info">{translate("howToBuyVoucher")}</Button>
            </DialogTrigger>
            <DialogContent className="pim-voucher-dialog">
              <DialogHeader>
                <DialogTitle className="pim-voucher-dialog-title">{translate("voucherModalTitle")}</DialogTitle>
              </DialogHeader>
              <div className="pim-voucher-dialog-content">
                <p>{translate("voucherModalIntro")}</p>
                
                <h3>{translate("voucherHowToGet")}</h3>
                <p>{translate("voucherStep1")}</p>
                <p>{translate("voucherStep2")}</p>
                <p>{translate("voucherStep3")}</p>
                
                <h3>{translate("voucherHowToReceive")}</h3>
                <p>{translate("voucherReceiveText")}</p>
                
                <h3>{translate("voucherWhyMassage")}</h3>
                <p>{translate("voucherWhyText")}</p>
              </div>
            </DialogContent>
          </Dialog>
          <Button asChild className="pim-gift-button-bottom">
            <a href="tel:+38162625500">{translate("callUs")}</a>
          </Button>
        </div>
      </section>

      {/* Testimonial - Empty with transparent background */}
      <section className="pim-testimonial">
        {/* Content removed */}
      </section>
      </div> {/* Close parallax container */}
    </div>
  );
};

export default Home;