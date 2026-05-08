import React, { useEffect, useRef, useState } from "react";
import "./RefreshParallaxSection.css";

/* SVG Path koordinate za krive linije - ISTE kao iz "Naši tretmani" */
const TOP_PATH = "M0,280 Q720,410 1440,260";
const BOTTOM_PATH = "M0,1100 Q720,1230 1440,1080";

// "Osvežite se" kartice - horizontalni format, jedna ispod druge
const REFRESH_DATA = {
  sr: [
    {
      id: "teme",
      title: "Osvežite teme",
      desc: "manje suvoće, svraba i masnoće"
    },
    {
      id: "san",
      title: "Probudite se lakše",
      desc: "duboka relaksacija poboljšava kvalitet sna"
    },
    {
      id: "umor",
      title: "Oslobodite se umora",
      desc: "ublažava glavobolju, ukočen vrat i naprezanje očiju"
    },
    {
      id: "kosa",
      title: "Rešite probleme kose",
      desc: "više volumena, elastičnosti i sjaja"
    },
    {
      id: "alergija",
      title: "Lakše kroz sezonu alergija",
      desc: "osećaj čistog disanja i komfora"
    },
    {
      id: "reset",
      title: "Reset uma i tela",
      desc: "umiruje nervni sistem i vraća balans"
    },
    {
      id: "stil",
      title: "Lakše stilizovanje",
      desc: "kosa je poslušnija i jutarnja rutina brža"
    }
  ],
  en: [
    {
      id: "teme",
      title: "Refresh Your Scalp",
      desc: "less dryness, itching and oiliness"
    },
    {
      id: "san",
      title: "Wake Up Easier",
      desc: "deep relaxation improves sleep quality"
    },
    {
      id: "umor",
      title: "Release Fatigue",
      desc: "relieves headaches, stiff neck and eye strain"
    },
    {
      id: "kosa",
      title: "Solve Hair Problems",
      desc: "more volume, elasticity and shine"
    },
    {
      id: "alergija",
      title: "Easier Through Allergy Season",
      desc: "feeling of clear breathing and comfort"
    },
    {
      id: "reset",
      title: "Mind & Body Reset",
      desc: "calms the nervous system and restores balance"
    },
    {
      id: "stil",
      title: "Easier Styling",
      desc: "hair is more manageable and morning routine faster"
    }
  ]
};

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

export default function RefreshParallaxSection({ lang = "sr" }) {
  const parY = useParallax(22);
  const [clipId] = useState(() => `clip-refresh-${Math.random().toString(36).slice(2)}`);
  const cardRefs = useRef([]);
  
  const cards = REFRESH_DATA[lang] || REFRESH_DATA.sr;
  const title = lang === "en" ? "Refresh Yourself" : "Osvežite se";

  // Intersection Observer for slide-in animation (IDENTICAL to Spa.js)
  useEffect(() => {
    const cardElements = cardRefs.current.filter(Boolean);
    
    cardElements.forEach((card, index) => {
      let transformStart;
      
      // Za horizontalni layout - alternira levo/desno
      const slideDistance = 300;
      const tiltAngle = 25;
      
      if (index % 2 === 0) {
        // Parne kartice sa leve strane
        transformStart = `translateX(-${slideDistance}px) rotateY(-${tiltAngle}deg)`;
      } else {
        // Neparne kartice sa desne strane
        transformStart = `translateX(${slideDistance}px) rotateY(${tiltAngle}deg)`;
      }
      
      // Set transition and initial hidden state
      card.style.transition = 'opacity 1.5s ease-out, transform 1.5s cubic-bezier(0.4, 0, 0.2, 1)';
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
          // Card leaving viewport - hide ONLY on desktop/landscape
          entry.target.style.opacity = '0';
          entry.target.style.transform = transformStart;
        }
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
    <section className="refresh-parallax-section" data-testid="refresh-parallax-section">
      {/* SVG krive linije sa parallax efektom - ISTE kao iz "Naši tretmani" */}
      <div className="refresh-curve-wrap" style={{ transform: `translate3d(0, ${parY}px, 0)` }}>
        <svg className="refresh-curve-svg" viewBox="0 0 1440 1200" preserveAspectRatio="none">
          <defs>
            {/* ClipPath - ispuna SAMO između gornje i donje linije */}
            <clipPath id={clipId} clipPathUnits="userSpaceOnUse">
              <path d={`${TOP_PATH} L1440,1080 Q720,1230 0,1100 Z`} />
            </clipPath>
          </defs>

          {/* Tamno siva ispuna SAMO između linija */}
          <rect
            x="0"
            y="0"
            width="1440"
            height="1200"
            clipPath={`url(#${clipId})`}
            className="refresh-curve-fill"
          />

          {/* Gornja zlatna linija */}
          <path d={TOP_PATH} className="refresh-curve-line refresh-curve-top" />
          
          {/* Donja zlatna linija */}
          <path d={BOTTOM_PATH} className="refresh-curve-line refresh-curve-bottom" />
        </svg>
      </div>

      {/* Sadržaj sekcije */}
      <div className="refresh-parallax-inner">
        <h2 className="refresh-parallax-title">{title}</h2>

        <div className="refresh-card-list">
          {cards.map((card, index) => (
            <div 
              key={card.id}
              ref={el => cardRefs.current[index] = el}
              className="refresh-card"
              data-testid={`refresh-card-${card.id}`}
            >
              <h3 className="refresh-card-title">{card.title}</h3>
              <p className="refresh-card-desc">{card.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
