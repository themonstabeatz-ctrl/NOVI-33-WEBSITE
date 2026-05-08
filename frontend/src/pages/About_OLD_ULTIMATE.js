import React, { useEffect, useState, useRef } from "react";
import { useLanguage } from "../context/LanguageContext";
import { Button } from "../components/ui/button";
import { Link } from "react-router-dom";
import { Award, Heart, Users, Star, Sparkles } from "lucide-react";

const About = () => {
  const { translate } = useLanguage();
  const [scrollY, setScrollY] = useState(0);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const containerRef = useRef(null);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  // Scroll tracking
  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Mouse tracking
  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const values = [
    {
      icon: <Heart className="w-12 h-12" />,
      title: "Tradicionalnost",
      description: "Naše tehnike su prenesene direktno iz Tajlanda kroz generacije među stručnim masereima."
    },
    {
      icon: <Award className="w-12 h-12" />,
      title: "Kvalitet",
      description: "Koristimo isključivo prirodne sastojke i aromatična ulja najvišeg kvaliteta."
    },
    {
      icon: <Users className="w-12 h-12" />,
      title: "Iskustvo",
      description: "Naš tim čine sertifikovani terapeuti sa više od 10 godina iskustva."
    }
  ];

  return (
    <div className="about-ultimate-container" ref={containerRef}>
      {/* Beautiful Animated Vines SVG */}
      <svg className="vines-svg" viewBox="0 0 1920 6000" preserveAspectRatio="xMidYMid slice">
        <defs>
          {/* Gradients */}
          <linearGradient id="vineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style={{ stopColor: '#FFD700', stopOpacity: 1 }}>
              <animate attributeName="stop-color" values="#FFD700;#D4AF37;#FFD700" dur="4s" repeatCount="indefinite" />
            </stop>
            <stop offset="50%" style={{ stopColor: '#D4AF37', stopOpacity: 0.9 }} />
            <stop offset="100%" style={{ stopColor: '#B8860B', stopOpacity: 0.8 }} />
          </linearGradient>

          <radialGradient id="leafGradient" cx="50%" cy="50%">
            <stop offset="0%" style={{ stopColor: '#90EE90', stopOpacity: 0.9 }} />
            <stop offset="50%" style={{ stopColor: '#228B22', stopOpacity: 0.8 }} />
            <stop offset="100%" style={{ stopColor: '#006400', stopOpacity: 0.7 }} />
          </radialGradient>

          <radialGradient id="flowerGradient" cx="50%" cy="50%">
            <stop offset="0%" style={{ stopColor: '#FFD700', stopOpacity: 1 }} />
            <stop offset="50%" style={{ stopColor: '#FFA500', stopOpacity: 0.9 }} />
            <stop offset="100%" style={{ stopColor: '#FF8C00', stopOpacity: 0.8 }} />
          </radialGradient>

          {/* Glow filter */}
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        {/* Left Vine - Complex Path */}
        <path 
          className="vine-main vine-left"
          d={`M 80,0 
             C 100,${150 + scrollY * 0.08} 70,${300 + scrollY * 0.12} 90,${450 + scrollY * 0.16}
             S 110,${600 + scrollY * 0.20} 75,${750 + scrollY * 0.24}
             S 95,${900 + scrollY * 0.28} 85,${1050 + scrollY * 0.32}
             S 100,${1200 + scrollY * 0.36} 70,${1350 + scrollY * 0.40}
             S 90,${1500 + scrollY * 0.44} 80,${1650 + scrollY * 0.48}
             S 95,${1800 + scrollY * 0.52} 75,${1950 + scrollY * 0.56}
             S 85,${2100 + scrollY * 0.60} 90,${2250 + scrollY * 0.64}
             S 80,${2400 + scrollY * 0.68} 85,${2550 + scrollY * 0.72}`}
          fill="none"
          stroke="url(#vineGradient)"
          strokeWidth="5"
          filter="url(#glow)"
        />
        
        {/* Right Vine - Complex Path */}
        <path 
          className="vine-main vine-right"
          d={`M 1840,0 
             C 1820,${150 + scrollY * 0.08} 1850,${300 + scrollY * 0.12} 1830,${450 + scrollY * 0.16}
             S 1810,${600 + scrollY * 0.20} 1845,${750 + scrollY * 0.24}
             S 1825,${900 + scrollY * 0.28} 1835,${1050 + scrollY * 0.32}
             S 1820,${1200 + scrollY * 0.36} 1850,${1350 + scrollY * 0.40}
             S 1830,${1500 + scrollY * 0.44} 1840,${1650 + scrollY * 0.48}
             S 1825,${1800 + scrollY * 0.52} 1845,${1950 + scrollY * 0.56}
             S 1835,${2100 + scrollY * 0.60} 1830,${2250 + scrollY * 0.64}
             S 1840,${2400 + scrollY * 0.68} 1835,${2550 + scrollY * 0.72}`}
          fill="none"
          stroke="url(#vineGradient)"
          strokeWidth="5"
          filter="url(#glow)"
        />

        {/* Secondary vine branches */}
        {[...Array(10)].map((_, i) => {
          const side = i % 2 === 0 ? 'left' : 'right';
          const baseX = side === 'left' ? 85 : 1835;
          const endX = side === 'left' ? baseX - 40 : baseX + 40;
          const yPos = i * 280 + scrollY * 0.15;
          
          return (
            <path
              key={`branch-${i}`}
              className="vine-branch"
              d={`M ${baseX},${yPos} Q ${(baseX + endX) / 2},${yPos + 30} ${endX},${yPos + 60}`}
              fill="none"
              stroke="url(#vineGradient)"
              strokeWidth="3"
              opacity="0.8"
              filter="url(#glow)"
            />
          );
        })}

        {/* Beautiful Leaves */}
        {[...Array(35)].map((_, i) => {
          const side = i % 2 === 0 ? 'left' : 'right';
          const baseX = side === 'left' ? 85 : 1835;
          const offsetX = (Math.sin(i) * 30) * (side === 'left' ? -1 : 1);
          const yPos = i * 80 + scrollY * 0.12;
          const rotation = Math.sin(scrollY * 0.008 + i) * 25 + (i * 10);
          const scale = 0.8 + Math.sin(scrollY * 0.01 + i) * 0.3;
          
          return (
            <g key={`leaf-${i}`} transform={`translate(${baseX + offsetX}, ${yPos})`}>
              {/* Leaf shape with stem */}
              <path
                className="vine-leaf-detailed"
                d={`M 0,0 
                   Q -${20 * scale},${15 * scale} -${25 * scale},${25 * scale}
                   Q -${20 * scale},${35 * scale} 0,${40 * scale}
                   Q ${20 * scale},${35 * scale} ${25 * scale},${25 * scale}
                   Q ${20 * scale},${15 * scale} 0,0`}
                fill="url(#leafGradient)"
                stroke="#2F4F2F"
                strokeWidth="1"
                opacity="0.85"
                filter="url(#glow)"
                style={{
                  transform: `rotate(${rotation}deg)`,
                  transformOrigin: 'center',
                }}
              />
              {/* Leaf vein */}
              <line
                x1="0"
                y1="0"
                x2="0"
                y2={40 * scale}
                stroke="#2F4F2F"
                strokeWidth="1.5"
                opacity="0.6"
                style={{
                  transform: `rotate(${rotation}deg)`,
                  transformOrigin: 'center',
                }}
              />
            </g>
          );
        })}

        {/* Golden Flowers */}
        {[...Array(12)].map((_, i) => {
          const side = i % 2 === 0 ? 'left' : 'right';
          const baseX = side === 'left' ? 85 : 1835;
          const offsetX = (Math.sin(i * 2) * 35) * (side === 'left' ? -1 : 1);
          const yPos = i * 230 + 120 + scrollY * 0.15;
          const petalRotation = (Date.now() * 0.001 + i) % 360;
          
          return (
            <g key={`flower-${i}`} transform={`translate(${baseX + offsetX}, ${yPos})`}>
              {/* Flower petals */}
              {[...Array(8)].map((_, p) => {
                const angle = (p * 45) + petalRotation;
                return (
                  <ellipse
                    key={`petal-${p}`}
                    cx="0"
                    cy="-12"
                    rx="6"
                    ry="15"
                    fill="url(#flowerGradient)"
                    opacity="0.9"
                    filter="url(#glow)"
                    style={{
                      transform: `rotate(${angle}deg)`,
                      transformOrigin: '0 0',
                    }}
                  />
                );
              })}
              {/* Flower center */}
              <circle
                cx="0"
                cy="0"
                r="8"
                fill="#FF8C00"
                opacity="0.95"
                filter="url(#glow)"
              />
              <circle
                cx="0"
                cy="0"
                r="4"
                fill="#FFD700"
                opacity="1"
              />
            </g>
          );
        })}

        {/* Decorative sparkles */}
        {[...Array(20)].map((_, i) => {
          const x = i % 2 === 0 ? 40 + Math.sin(i) * 30 : 1880 - Math.sin(i) * 30;
          const y = i * 150 + scrollY * 0.1;
          const opacity = 0.3 + Math.sin(Date.now() * 0.002 + i) * 0.3;
          
          return (
            <g key={`sparkle-${i}`} transform={`translate(${x}, ${y})`} opacity={opacity}>
              <polygon
                points="0,-8 2,-2 8,0 2,2 0,8 -2,2 -8,0 -2,-2"
                fill="#FFD700"
                filter="url(#glow)"
              />
            </g>
          );
        })}
      </svg>

      {/* Hero Section */}
      <section className="about-ultimate-hero">
        <div 
          className="hero-orbs-container"
          style={{
            transform: `translate(${mousePosition.x * 0.02}px, ${mousePosition.y * 0.02}px)`,
          }}
        >
          <div className="floating-orb orb-1"></div>
          <div className="floating-orb orb-2"></div>
          <div className="floating-orb orb-3"></div>
          <div className="floating-orb orb-4"></div>
        </div>

        <div className="hero-content-ultimate">
          <h1 
            className="hero-title-ultimate"
            style={{
              transform: `perspective(2000px) rotateX(${scrollY * 0.05}deg) translateZ(${100 - scrollY * 0.2}px)`,
            }}
          >
            O Nama
          </h1>
          <div className="hero-subtitle-container">
            <p className="hero-subtitle-ultimate">
              Otkrijte našu priču i strast prema tradicionalnim tajlandskim tretmanima
            </p>
            <div className="subtitle-sparkles">
              <Sparkles className="hero-sparkle" />
              <Sparkles className="hero-sparkle" />
            </div>
          </div>
        </div>

        {/* Floating particles */}
        <div className="particles-container">
          {[...Array(30)].map((_, i) => (
            <div
              key={i}
              className="particle"
              style={{
                left: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${5 + Math.random() * 5}s`,
              }}
            ></div>
          ))}
        </div>
      </section>

      {/* Story Section with 3D depth */}
      <section className="story-ultimate-section">
        <div 
          className="story-ultimate-card"
          style={{
            transform: `perspective(2000px) rotateY(${(mousePosition.x / window.innerWidth - 0.5) * 15}deg) rotateX(${-(mousePosition.y / window.innerHeight - 0.5) * 15}deg) translateZ(${50 - scrollY * 0.05}px)`,
          }}
        >
          <div className="story-glow-effect"></div>
          <h2 className="story-ultimate-title">Naša Priča</h2>
          <div className="story-ultimate-content">
            <p>
              Bua Luang Thai Spa je nastao iz želje da se autentično tajlandsko iskustvo 
              donese u srce Srbije. Naša osnivačka je provela godine u Tajlandu, 
              učeći tradicionalne tehnike masaže i spa tretmana od međunarodnih meštara.
            </p>
            <p>
              "Bua Luang" na tajlandskom znači "kraljevski lotos" - simbol čistoce, 
              lepote i duševnog mira. Baš kao što se lotos izdige iz blata da postane 
              prekrasna biljka, i mi verujemo da svaki gost može da pronađe svoj 
              unutrašnji mir kroz naše tretmane.
            </p>
            <p>
              Danas, naš spa predstavlja oazu mira u gradu, gde spajamo 
              hiljadugodišnju tajlandsku tradiciju sa najsavremenijim tehnikama 
              i opremom, pružajući jedinstveno iskustvo svakom gostu.
            </p>
          </div>
        </div>
      </section>

      {/* Values Section with 3D cards */}
      <section className="values-ultimate-section">
        <h2 
          className="values-ultimate-title"
          style={{
            transform: `translateY(${-scrollY * 0.1}px)`,
          }}
        >
          Naše Vrednosti
        </h2>
        <div className="values-ultimate-grid">
          {values.map((value, index) => (
            <div
              key={index}
              className="value-ultimate-card"
              style={{
                animationDelay: `${index * 0.3}s`,
              }}
            >
              <div className="value-card-ultimate-inner">
                <div className="value-card-shine"></div>
                <div className="value-icon-ultimate">{value.icon}</div>
                <h3 className="value-title-ultimate">{value.title}</h3>
                <p className="value-desc-ultimate">{value.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Team Section */}
      <section className="team-ultimate-section">
        <h2 className="team-ultimate-title">Naš Stručni Tim</h2>
        <div className="team-ultimate-grid">
          {[
            { name: "Siriporn Thanakit", role: "Glavni terapijska", exp: "15 godina" },
            { name: "Chanida Suwannaporn", role: "Spa terapeutkinja", exp: "12 godina" },
            { name: "Niran Pongpanich", role: "Masažer", exp: "8 godina" }
          ].map((member, i) => (
            <div key={i} className="team-ultimate-card">
              <div className="team-card-glow"></div>
              <div className="team-avatar-ultimate">
                <Star className="team-star-icon" />
              </div>
              <h3 className="team-member-name">{member.name}</h3>
              <p className="team-member-role">{member.role}</p>
              <p className="team-member-exp">{member.exp} iskustva</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-ultimate-section">
        <div className="cta-ultimate-container">
          <h2 className="cta-ultimate-title">
            Spremni da doživite autentično tajlandsko iskustvo?
          </h2>
          <p className="cta-ultimate-subtitle">
            Kontaktirajte nas i rezervišite vaš tretman
          </p>
          <div className="cta-ultimate-buttons">
            <Button asChild className="cta-btn-ultimate cta-btn-primary">
              <Link to="/contact">Kontaktirajte nas</Link>
            </Button>
            <Button asChild className="cta-btn-ultimate cta-btn-secondary">
              <Link to="/massage">Pogledajte naše usluge</Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;
