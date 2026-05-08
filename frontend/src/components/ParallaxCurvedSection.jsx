import React, { useEffect, useMemo, useState, useRef } from "react";
import "./ParallaxCurvedSection.css";

/* SVG Path koordinate za krive linije
   GORNJA: konkavna nadole ("frown") - još više spuštena
   DONJA: konkavna nadole - blizu sekcije Tok tretmana */
const TOP_PATH = "M0,280 Q720,410 1440,260";
const BOTTOM_PATH = "M0,1380 Q720,1510 1440,1360";

function useParallax(offset = 18) {
  const [y, setY] = useState(0);
  useEffect(() => {
    const onScroll = () => setY(window.scrollY || 0);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  return Math.round((y % 600) * (offset / 600));
}

// FlipServiceCard komponenta - HOVER flip behavior
function FlipServiceCard({ card, cardRef }) {
  const [isFlipped, setIsFlipped] = useState(false);

  // Kada kursor napusti karticu, vraća se na prednju stranu
  const handleMouseLeave = () => {
    setIsFlipped(false);
  };

  // Klik na DETALJI flipuje karticu
  const handleDetailsClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsFlipped(true);
  };

  return (
    <div 
      ref={cardRef}
      className={`blFlipCard ${isFlipped ? "isFlipped" : ""}`}
      onMouseLeave={handleMouseLeave}
    >
      <div className="blFlipInner">
        {/* FRONT */}
        <div className="blFlipFace blFront">
          <div className="blCardImage">
            <img src={card.image} alt={card.title} loading="lazy" />
          </div>
          <div className="blCardContent">
            <div className="blCardHeader">
              <h3 className="blCardTitle">{card.title}</h3>
              <div className="blCardMeta">
                <span className="blCardPrice">{card.price}</span>
                <span className="blCardDuration">{card.duration}</span>
              </div>
            </div>
            <p className="blCardDesc">{card.shortDesc}</p>
            <div className="blCardButtons">
              <button 
                type="button"
                className="blDetailsBtn"
                onClick={handleDetailsClick}
                data-testid={`flip-card-details-${card.id}`}
              >
                DETALJI
              </button>
            </div>
          </div>
        </div>
        
        {/* BACK */}
        <div className="blFlipFace blBack">
          <div className="blBackContent">
            <h3 className="blBackTitle">{card.title}</h3>
            <p className="blBackDesc">{card.fullDesc}</p>
            <div className="blBackNote">
              Sklonite kursor za povratak
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ParallaxCurvedSection({ title, cards = [] }) {
  const parY = useParallax(22);
  const clipId = useMemo(() => `clip-${Math.random().toString(36).slice(2)}`, []);
  const cardRefs = useRef([]);

  // Intersection Observer for slide-in animation (IDENTICAL to Spa.js)
  useEffect(() => {
    const cardElements = cardRefs.current.filter(Boolean);
    
    // Get grid columns for dynamic slide direction
    const grid = document.querySelector('.blCardGrid');
    const gridStyle = grid ? window.getComputedStyle(grid) : null;
    const gridTemplateColumns = gridStyle ? gridStyle.gridTemplateColumns : '';
    const columns = gridTemplateColumns.split(' ').length || 3;
    
    cardElements.forEach((card, index) => {
      let slideDirection;
      let transformStart;
      
      if (window.innerWidth <= 768 || columns === 1) {
        // Mobile: alternate pattern
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
      } else {
        // Desktop: based on column position
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
      }
      
      // Set transition and initial hidden state
      card.style.transition = 'opacity 1.5s ease-out, transform 1.5s cubic-bezier(0.4, 0, 0.2, 1)';
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
    
    cardElements.forEach((card) => {
      observer.observe(card);
    });

    return () => {
      observer.disconnect();
    };
  }, [cards]);

  return (
    <section className="blParallaxSection" data-testid="parallax-curved-section">
      {/* SVG krive linije sa parallax efektom */}
      <div className="blCurveWrap" style={{ transform: `translate3d(0, ${parY}px, 0)` }}>
        <svg className="blCurveSvg" viewBox="0 0 1440 1600" preserveAspectRatio="none">
          <defs>
            {/* ClipPath - ispuna SAMO između gornje i donje linije */}
            <clipPath id={clipId} clipPathUnits="userSpaceOnUse">
              <path d={`${TOP_PATH} L1440,1360 Q720,1510 0,1380 Z`} />
            </clipPath>
          </defs>

          {/* Tamno siva ispuna SAMO između linija */}
          <rect
            x="0"
            y="0"
            width="1440"
            height="1600"
            clipPath={`url(#${clipId})`}
            className="blCurveFill"
          />

          {/* Gornja zlatna linija */}
          <path d={TOP_PATH} className="blCurveLine blCurveTop" />
          
          {/* Donja zlatna linija - spuštena ispod kartica */}
          <path d={BOTTOM_PATH} className="blCurveLine blCurveBottom" />
        </svg>
      </div>

      {/* Sadržaj sekcije */}
      <div className="blParallaxInner">
        {title && <h2 className="blParallaxTitle">{title}</h2>}

        <div className="blCardGrid">
          {cards.map((card, index) => (
            <FlipServiceCard 
              key={card.id}
              card={card} 
              cardRef={el => cardRefs.current[index] = el}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
