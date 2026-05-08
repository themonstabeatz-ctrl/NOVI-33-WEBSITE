import React, { useEffect, useRef, useState, useMemo } from "react";
import "./BenefitsParallaxSection.css";

// Benefiti kartice - podaci izvučeni sa slike
const BENEFITS_DATA = {
  sr: [
    { id: "detoks", title: "Detoks temena", desc: "Uklanjanje sebuma, naslaga i nečistoće iz pora" },
    { id: "cirkulacija", title: "Bolja cirkulacija", desc: "Masaža podstiče protok i može pomoći rastu kose" },
    { id: "lifting", title: "Lifting efekat", desc: "Opuštanje i drenaža smanjuju nadutost i zatežu lice" },
    { id: "kosa", title: "Zdravija kosa", desc: "Hranljive formule jačaju vlas i smanjuju pucanje" },
    { id: "san", title: "Bolji san", desc: "Duboka relaksacija — budite se odmoreniji" },
    { id: "reset", title: "Mentalni reset", desc: "Aromaterapija + masaža vraćaju mir i fokus" },
    { id: "oci", title: "Olakšanje za oči/vrat", desc: "Idealno za rad za računarom" },
    { id: "balans", title: "Reset uma i tela", desc: "Umiruje nervni sistem i vraća balans" }
  ],
  en: [
    { id: "detoks", title: "Scalp Detox", desc: "Removal of sebum, buildup and impurities from pores" },
    { id: "cirkulacija", title: "Better Circulation", desc: "Massage stimulates blood flow and can promote hair growth" },
    { id: "lifting", title: "Lifting Effect", desc: "Relaxation and drainage reduce puffiness and tighten the face" },
    { id: "kosa", title: "Healthier Hair", desc: "Nourishing formulas strengthen hair and reduce breakage" },
    { id: "san", title: "Better Sleep", desc: "Deep relaxation — wake up more rested" },
    { id: "reset", title: "Mental Reset", desc: "Aromatherapy + massage restore peace and focus" },
    { id: "oci", title: "Eye/Neck Relief", desc: "Ideal for computer work" },
    { id: "balans", title: "Mind & Body Reset", desc: "Calms the nervous system and restores balance" }
  ]
};

// SVG putanje za krive linije - identične kao "Više od nege kose"
const TOP_CURVE = "M0,80 Q360,0 720,60 Q1080,120 1440,40";
const BOTTOM_CURVE = "M0,80 Q360,0 720,60 Q1080,120 1440,40";

export default function BenefitsParallaxSection({ lang = "sr" }) {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);
  const cardRefs = useRef([]);
  const clipId = useMemo(() => `benefits-clip-${Math.random().toString(36).slice(2)}`, []);
  
  const benefits = BENEFITS_DATA[lang] || BENEFITS_DATA.sr;
  const title = lang === "en" ? "Benefits of Head Spa Treatment" : "Benefiti Head Spa tretmana";

  // Intersection Observer za sekciju - aktivira animaciju naslova
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(true);
          }
        });
      },
      { threshold: 0.2 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  // Intersection Observer for slide-in animation
  useEffect(() => {
    const cardElements = cardRefs.current.filter(Boolean);
    
    const grid = document.querySelector('.benefits-card-grid');
    const gridStyle = grid ? window.getComputedStyle(grid) : null;
    const gridTemplateColumns = gridStyle ? gridStyle.gridTemplateColumns : '';
    const columns = gridTemplateColumns.split(' ').length || 4;
    
    cardElements.forEach((card, index) => {
      let transformStart;
      
      if (window.innerWidth <= 768 || columns <= 2) {
        const pattern = index % 3;
        const slideDistance = 200;
        const tiltAngle = 25;
        
        if (pattern === 0) {
          transformStart = `translateX(-${slideDistance}px) rotateY(-${tiltAngle}deg)`;
        } else if (pattern === 1) {
          transformStart = 'translateY(150px)';
        } else {
          transformStart = `translateX(${slideDistance}px) rotateY(${tiltAngle}deg)`;
        }
      } else {
        const columnPosition = index % columns;
        const slideDistance = 300;
        const tiltAngle = 30;
        
        if (columnPosition === 0) {
          transformStart = `translateX(-${slideDistance}px) rotateY(-${tiltAngle}deg)`;
        } else if (columnPosition === columns - 1) {
          transformStart = `translateX(${slideDistance}px) rotateY(${tiltAngle}deg)`;
        } else {
          transformStart = 'translateY(150px)';
        }
      }
      
      card.style.transition = 'opacity 1.5s ease-out, transform 1.5s cubic-bezier(0.4, 0, 0.2, 1)';
      card.setAttribute('data-transform-start', transformStart);
      card.style.transformStyle = 'preserve-3d';
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
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translate(0, 0) rotateY(0deg)';
        } else if (!isPortrait) {
          entry.target.style.opacity = '0';
          entry.target.style.transform = transformStart;
        }
      });
    };

    const observer = new IntersectionObserver(handleIntersection, observerOptions);
    cardElements.forEach((card) => observer.observe(card));

    return () => observer.disconnect();
  }, [benefits]);

  return (
    <section className="benefits-parallax-section" ref={sectionRef} data-testid="benefits-parallax-section">
      {/* SVG sa video pozadinom i clip-path */}
      <svg className="benefits-svg-container" viewBox="0 0 1440 900" preserveAspectRatio="none">
        <defs>
          {/* ClipPath - oblast SAMO između dve krive linije */}
          <clipPath id={clipId}>
            <path d="M0,80 Q360,0 720,60 Q1080,120 1440,40 L1440,860 Q1080,780 720,840 Q360,900 0,820 Z" />
          </clipPath>
        </defs>

        {/* Video unutar clip-path oblasti */}
        <foreignObject x="0" y="0" width="1440" height="900" clipPath={`url(#${clipId})`}>
          <div className="benefits-video-container" xmlns="http://www.w3.org/1999/xhtml">
            <video 
              className="benefits-video"
              autoPlay 
              muted 
              loop 
              playsInline
              data-testid="benefits-video"
            >
              <source src="https://customer-assets.emergentagent.com/job_visual-spa-ui/artifacts/ooc2882x_Ultra-realistic_extreme_close%20hair.mp4" type="video/mp4" />
            </video>
            <div className="benefits-video-overlay"></div>
          </div>
        </foreignObject>

        {/* Gornja zlatna linija */}
        <path d={TOP_CURVE} className="benefits-curve-line" />
        
        {/* Donja zlatna linija */}
        <path d="M0,820 Q360,900 720,840 Q1080,780 1440,860" className="benefits-curve-line" />
      </svg>

      {/* Sadržaj iznad videa */}
      <div className={`benefits-content ${isVisible ? 'benefits-visible' : 'benefits-hidden'}`}>
        <h2 className="benefits-title">{title}</h2>
        
        <div className="benefits-card-grid">
          {benefits.map((benefit, index) => (
            <div 
              key={benefit.id}
              ref={el => cardRefs.current[index] = el}
              className="benefits-card"
              data-testid={`benefit-card-${benefit.id}`}
            >
              <h3 className="benefits-card-title">{benefit.title}</h3>
              <p className="benefits-card-desc">{benefit.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
