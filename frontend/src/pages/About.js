import React, { useEffect, useRef, useState } from "react";
import { Helmet } from "react-helmet";
import { useLanguage } from "../context/LanguageContext";
import { throttle } from "../utils/debounce";
import { getSEO } from "../utils/seoConfig";

const About = () => {
  const { translate } = useLanguage();
  const parallaxSection1Ref = useRef(null);
  const parallaxSection2Ref = useRef(null);
  const textRowsRef = useRef([]);

  // Detect mobile device for video optimization
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    // Check if mobile using visualViewport or screen width
    const checkMobile = () => {
      const width = window.visualViewport ? window.visualViewport.width : window.screen.width;
      setIsMobile(width < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  // Logo transformation on scroll
  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY;
      const aboutHeroSection = document.querySelector('.about-hero-fixed');
      const aboutHeroLogo = document.querySelector('.about-hero-logo');
      const aboutHeroTitle = document.querySelector('.about-hero-title');
      const aboutHeroSubtitle = document.querySelector('.about-hero-subtitle');
      
      if (!aboutHeroSection || !aboutHeroLogo) return;
      
      const heroHeight = aboutHeroSection.offsetHeight;
      const scrollPercent = Math.min(scrollPosition / heroHeight, 1);
      
      if (scrollPercent > 0.05) {
        const opacity = Math.max(1 - (scrollPercent - 0.05) * 3, 0);
        const scale = Math.max(1 - (scrollPercent - 0.05) * 1.5, 0.2);
        
        aboutHeroLogo.style.opacity = opacity;
        aboutHeroLogo.style.transform = `scale(${scale})`;
        aboutHeroLogo.style.filter = `blur(${(scrollPercent - 0.05) * 15}px)`;
        
        // Fade out title
        if (aboutHeroTitle) {
          aboutHeroTitle.style.opacity = opacity;
          aboutHeroTitle.style.transform = `translateY(-${(scrollPercent - 0.05) * 80}px)`;
        }
        
        // Fade out subtitle
        if (aboutHeroSubtitle) {
          aboutHeroSubtitle.style.opacity = opacity;
          aboutHeroSubtitle.style.transform = `translateY(-${(scrollPercent - 0.05) * 60}px)`;
        }
      } else {
        aboutHeroLogo.style.opacity = 1;
        aboutHeroLogo.style.transform = 'scale(1)';
        aboutHeroLogo.style.filter = 'blur(0px)';
        
        if (aboutHeroTitle) {
          aboutHeroTitle.style.opacity = '1';
          aboutHeroTitle.style.transform = 'translateY(0)';
        }
        
        if (aboutHeroSubtitle) {
          aboutHeroSubtitle.style.opacity = '1';
          aboutHeroSubtitle.style.transform = 'translateY(0)';
        }
      }
    };
    
    const throttledHandleScroll = throttle(handleScroll, 16);
    window.addEventListener('scroll', throttledHandleScroll, { passive: true });
    return () => window.removeEventListener('scroll', throttledHandleScroll);
  }, []);

  // Advanced Parallax Text Animation System
  useEffect(() => {
    const observerOptions = {
      root: null,
      rootMargin: '-10% 0px -10% 0px',
      threshold: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    };

    const handleIntersection = (entries) => {
      entries.forEach((entry) => {
        const section = entry.target;
        const textRows = section.querySelectorAll('.parallax-text-row');
        
        if (entry.isIntersecting) {
          // Calculate animation progress based on intersection ratio
          const progress = entry.intersectionRatio;
          
          textRows.forEach((row, index) => {
            const delay = index * 200; // 200ms delay between rows
            const shouldAnimate = progress > (index * 0.15); // Staggered trigger points
            
            if (shouldAnimate && !row.classList.contains('animated')) {
              setTimeout(() => {
                row.classList.add('slide-in-active');
                row.classList.add('animated');
              }, delay);
            }
          });
        }
      });
    };

    const observer = new IntersectionObserver(handleIntersection, observerOptions);
    
    // Observe both parallax sections
    if (parallaxSection1Ref.current) {
      observer.observe(parallaxSection1Ref.current);
    }
    if (parallaxSection2Ref.current) {
      observer.observe(parallaxSection2Ref.current);
    }

    return () => {
      observer.disconnect();
    };
  }, []);

  // Smooth parallax scrolling effect
  useEffect(() => {
    const handleParallaxScroll = () => {
      const scrolled = window.pageYOffset;
      const parallaxElements = document.querySelectorAll('.parallax-bg-layer');
      
      parallaxElements.forEach((element, index) => {
        const speed = 0.5 + (index * 0.1); // Different speeds for layers
        const yPos = -(scrolled * speed);
        element.style.transform = `translateY(${yPos}px)`;
      });
    };

    const throttledHandleParallaxScroll = throttle(handleParallaxScroll, 16);
    window.addEventListener('scroll', throttledHandleParallaxScroll, { passive: true });
    return () => window.removeEventListener('scroll', throttledHandleParallaxScroll);
  }, []);

  const aboutSEO = getSEO('about');

  return (
    <div className="about-container">
      <Helmet>
        <title>{aboutSEO.title}</title>
        <meta name="description" content={aboutSEO.description} />
        <meta name="keywords" content={aboutSEO.keywords} />
        <link rel="canonical" href={aboutSEO.canonical} />
      </Helmet>

      {/* Fixed Video Hero Section */}
      <section className="about-hero-fixed">
        <div className="about-hero-video-container">
          <video 
            autoPlay 
            muted 
            loop 
            playsInline
            preload="auto"
            className="about-hero-video"
          >
            {/* Mobile gets optimized smaller video (9.68 MB vs 19.76 MB) */}
            {isMobile ? (
              <source src="https://customer-assets.emergentagent.com/job_thaispa-mobile/artifacts/z9z4vnsa_CAJ-3.mp4" type="video/mp4" />
            ) : (
              <source src="https://customer-assets.emergentagent.com/job_goldenlinesdesign/artifacts/9eowsbkd_CAJ.mp4" type="video/mp4" />
            )}
          </video>
          <div className="about-hero-overlay"></div>
        </div>
        
        <div className="about-hero-content">
          <div className="about-hero-logo">
            <img 
              src="https://customer-assets.emergentagent.com/job_83ed575e-3634-46be-8586-79a3348def97/artifacts/7sfhgz1m_Bua%20luang%20logo.png"
              alt="Bua Luang Logo"
              className="hero-logo-image"
            />
          </div>
          <h1 className="about-hero-title">{translate("aboutHeroTitle")}</h1>
          <div className="about-hero-divider"></div>
          <p className="about-hero-subtitle">{translate("aboutHeroSubtitle")}</p>
        </div>
      </section>

      {/* Simple Parallax Content Section */}
      <div className="about-simple-parallax">
        <div className="about-text-container">
          <div className="about-parallax-logo">
            <img 
              src="https://customer-assets.emergentagent.com/job_83ed575e-3634-46be-8586-79a3348def97/artifacts/7sfhgz1m_Bua%20luang%20logo.png"
              alt="Bua Luang Logo"
            />
          </div>
          
          <p className="about-text-paragraph">
            <span className="about-intro-highlight">{translate("aboutIntro")}</span> {translate("aboutText1")}
          </p>
          
          <p className="about-text-paragraph">{translate("aboutText2")}</p>
          
          <p className="about-text-paragraph">{translate("aboutText3")}</p>
          
          <p className="about-text-paragraph">{translate("aboutText4")}</p>
          
          <p className="about-text-paragraph">{translate("aboutText5")}</p>
          
          <p className="about-text-paragraph about-text-final">{translate("aboutText6")}</p>
        </div>
      </div>
    </div>
  );
};

export default About;
