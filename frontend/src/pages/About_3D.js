import React, { useEffect, useState, useRef } from "react";
import { useLanguage } from "../context/LanguageContext";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Link } from "react-router-dom";
import { Award, Heart, Users, Star, Sparkles, Leaf, Zap } from "lucide-react";

const About = () => {
  const { translate } = useLanguage();
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [scrollY, setScrollY] = useState(0);
  const containerRef = useRef(null);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const values = [
    {
      icon: <Heart className="w-12 h-12" />,
      title: "Tradicionalnost",
      description: "Naše tehnike su prenesene direktno iz Tajlanda kroz generacije među stručnim masereima.",
      color: "#D4AF37"
    },
    {
      icon: <Award className="w-12 h-12" />,
      title: "Kvalitet",
      description: "Koristimo isključivo prirodne sastojke i aromatična ulja najvišeg kvaliteta.",
      color: "#B8860B"
    },
    {
      icon: <Users className="w-12 h-12" />,
      title: "Iskustvo",
      description: "Naš tim čine sertifikovani terapeuti sa više od 10 godina iskustva.",
      color: "#FFD700"
    }
  ];

  return (
    <div className="about-container-3d" ref={containerRef}>
      {/* 3D Hero Section */}
      <section className="about-hero-3d">
        <div 
          className="about-hero-background"
          style={{
            transform: `translateY(${scrollY * 0.5}px)`,
          }}
        >
          <div className="hero-gradient-orb hero-orb-1"></div>
          <div className="hero-gradient-orb hero-orb-2"></div>
          <div className="hero-gradient-orb hero-orb-3"></div>
        </div>
        <div className="about-hero-content">
          <h1 
            className="about-hero-title-3d"
            style={{
              transform: `perspective(1000px) rotateX(${scrollY * 0.02}deg) translateZ(${scrollY * 0.1}px)`,
            }}
          >
            O Nama
          </h1>
          <p className="about-hero-subtitle-3d">
            Otkrijte našu priču i strast prema tradicionalnim tajlandskim tretmanima
          </p>
          <div className="hero-sparkles">
            <Sparkles className="sparkle sparkle-1" />
            <Sparkles className="sparkle sparkle-2" />
            <Sparkles className="sparkle sparkle-3" />
          </div>
        </div>
      </section>

      {/* 3D Story Section */}
      <section className="story-section-3d">
        <div className="story-container-3d">
          <div 
            className="story-card-3d"
            style={{
              transform: `perspective(1500px) rotateY(${(mousePosition.x / window.innerWidth - 0.5) * 10}deg) rotateX(${-(mousePosition.y / window.innerHeight - 0.5) * 10}deg)`,
            }}
          >
            <div className="story-card-glow"></div>
            <h2 className="story-title-3d">Naša Priča</h2>
            <div className="story-content-3d">
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
            <div className="lotus-decoration">
              <Leaf className="lotus-leaf" />
            </div>
          </div>
        </div>
      </section>

      {/* 3D Values Section */}
      <section className="values-section-3d">
        <h2 
          className="values-title-3d"
          style={{
            transform: `translateZ(${scrollY * 0.05}px)`,
          }}
        >
          Naše Vrednosti
        </h2>
        <div className="values-grid-3d">
          {values.map((value, index) => (
            <div
              key={index}
              className="value-card-3d"
              style={{
                animationDelay: `${index * 0.2}s`,
              }}
            >
              <div className="value-card-inner">
                <div className="value-card-front">
                  <div className="value-icon-3d" style={{ color: value.color }}>
                    {value.icon}
                  </div>
                  <h3 className="value-title">{value.title}</h3>
                </div>
                <div className="value-card-back">
                  <p className="value-description-3d">{value.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 3D Team Section */}
      <section className="team-section-3d">
        <h2 className="team-title-3d">Naš Stručni Tim</h2>
        <div className="team-grid-3d">
          <div className="team-member-3d">
            <div className="member-card-3d">
              <div className="member-avatar">
                <div className="avatar-glow"></div>
                <Star className="member-star" />
              </div>
              <h3 className="member-name-3d">Siriporn Thanakit</h3>
              <p className="member-role-3d">Glavni terapijska</p>
              <div className="member-details-3d">
                <p>15 godina iskustva</p>
                <p>Royal Thai Massage School, Bangkok</p>
              </div>
            </div>
          </div>

          <div className="team-member-3d">
            <div className="member-card-3d">
              <div className="member-avatar">
                <div className="avatar-glow"></div>
                <Star className="member-star" />
              </div>
              <h3 className="member-name-3d">Chanida Suwannaporn</h3>
              <p className="member-role-3d">Spa terapeutkinja</p>
              <div className="member-details-3d">
                <p>12 godina iskustva</p>
                <p>Chiva-Som International Health Resort</p>
              </div>
            </div>
          </div>

          <div className="team-member-3d">
            <div className="member-card-3d">
              <div className="member-avatar">
                <div className="avatar-glow"></div>
                <Star className="member-star" />
              </div>
              <h3 className="member-name-3d">Niran Pongpanich</h3>
              <p className="member-role-3d">Masažer</p>
              <div className="member-details-3d">
                <p>8 godina iskustva</p>
                <p>Thai Traditional Medical College</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3D CTA Section */}
      <section className="cta-section-3d">
        <div className="cta-container-3d">
          <Zap className="cta-zap cta-zap-1" />
          <Zap className="cta-zap cta-zap-2" />
          <h2 className="cta-title-3d">Spremni da doživite autentično tajlandsko iskustvo?</h2>
          <p className="cta-subtitle-3d">Kontaktirajte nas i rezervišite vaš tretman</p>
          <div className="cta-buttons-3d">
            <Button asChild className="cta-button-3d cta-button-primary">
              <Link to="/contact">Kontaktirajte nas</Link>
            </Button>
            <Button asChild className="cta-button-3d cta-button-secondary">
              <Link to="/massage">Pogledajte naše usluge</Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;
