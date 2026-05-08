import React, { useEffect, useState, useRef } from "react";
import { useLanguage } from "../context/LanguageContext";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Link } from "react-router-dom";
import { Award, Heart, Users, Star, Sparkles, Leaf, Zap } from "lucide-react";

const About = () => {
  const { translate } = useLanguage();
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [scrollY, setScrollY] = useState(0);
  const containerRef = useRef(null);

  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  // Track mouse position for 3D effects
  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Track scroll for parallax
  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const values = [
    {
      icon: <Heart className="w-8 h-8" />,
      title: "Tradicionalnost",
      description: "Naše tehnike su prenesene direktno iz Tajlanda kroz generacije među stručnim masereima."
    },
    {
      icon: <Award className="w-8 h-8" />,
      title: "Kvalitet",
      description: "Koristimo isključivo prirodne sastojke i aromatična ulja najvišeg kvaliteta."
    },
    {
      icon: <Users className="w-8 h-8" />,
      title: "Iskustvo",
      description: "Naš tim čine sertifikovani terapeuti sa više od 10 godina iskustva."
    }
  ];

  const teamMembers = [
    {
      name: "Siriporn Thanakit",
      position: "Glavni terapijska",
      experience: "15 godina iskustva",
      specialty: "Tradicionalne tajlandske masaže",
      certification: "Royal Thai Massage School, Bangkok"
    },
    {
      name: "Chanida Suwannaporn", 
      position: "Spa terapeutkinja",
      experience: "12 godina iskustva",
      specialty: "Tretmani lica i aromaterapija",
      certification: "Chiva-Som International Health Resort"
    },
    {
      name: "Niran Pongpanich",
      position: "Masažer",
      experience: "8 godina iskustva", 
      specialty: "Deep tissue i sportske masaže",
      certification: "Thai Traditional Medical College"
    }
  ];

  return (
    <div className="about-container-3d" ref={containerRef}>
      {/* 3D Hero Header */}
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

      {/* Our Story */}
      <section className="story-section">
        <div className="story-content">
          <div className="story-text">
            <h2 className="story-title">Naša Priča</h2>
            <div className="story-paragraphs">
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
          <div className="story-image">
            <img 
              src="https://customer-assets.emergentagent.com/job_83ed575e-3634-46be-8586-79a3348def97/artifacts/i03j5uou_podloga.jpg"
              alt="Thai traditional pattern"
              className="story-pattern"
            />
          </div>
        </div>
      </section>

      {/* Our Values */}
      <section className="values-section">
        <h2 className="values-title">Naše Vrednosti</h2>
        <div className="values-grid">
          {values.map((value, index) => (
            <Card key={index} className="value-card">
              <CardContent className="value-content">
                <div className="value-icon">{value.icon}</div>
                <h3 className="value-name">{value.title}</h3>
                <p className="value-description">{value.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Our Team */}
      <section className="team-section">
        <h2 className="team-title">Naš Tim</h2>
        <p className="team-subtitle">
          Upoznajte stručne terapeunte koji će se pobrinuti za vaše blagostanje
        </p>
        
        <div className="team-grid">
          {teamMembers.map((member, index) => (
            <Card key={index} className="team-card">
              <CardContent className="team-content">
                <div className="member-info">
                  <h3 className="member-name">{member.name}</h3>
                  <Badge className="member-position">{member.position}</Badge>
                  
                  <div className="member-details">
                    <div className="member-experience">
                      <Star className="w-4 h-4" />
                      <span>{member.experience}</span>
                    </div>
                    
                    <div className="member-specialty">
                      <strong>Specijalnost:</strong> {member.specialty}
                    </div>
                    
                    <div className="member-certification">
                      <strong>Sertifikacija:</strong> {member.certification}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Certifications */}
      <section className="certifications-section">
        <div className="certifications-content">
          <h2 className="certifications-title">Sertifikacije i Priznanja</h2>
          <div className="certifications-grid">
            <div className="certification-item">
              <Award className="certification-icon" />
              <div className="certification-text">
                <h4>Sertifikovano od strane Royal Thai Massage Association</h4>
                <p>Oficijalno priznanje za autentične tajlandske tehnike</p>
              </div>
            </div>
            
            <div className="certification-item">
              <Award className="certification-icon" />
              <div className="certification-text">
                <h4>Najbolji Spa u Beogradu 2023</h4>
                <p>Nagrada za izuzetnu uslugu i kvalitet tretmana</p>
              </div>
            </div>
            
            <div className="certification-item">
              <Award className="certification-icon" />
              <div className="certification-text">
                <h4>Član Srpske Asocijacije Spa Centara</h4>
                <p>Pridruživanje profesionalnim standardima industrije</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="cta-section">
        <div className="cta-content">
          <h2 className="cta-title">Spremni da doživite autentično tajlandsko iskustvo?</h2>
          <p className="cta-subtitle">Kontaktirajte nas i rezervišite vaš tretman</p>
          <div className="cta-buttons">
            <Button asChild size="lg" className="cta-button-primary">
              <Link to="/contact">Kontaktirajte nas</Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="cta-button-secondary">
              <Link to="/massage">Pogledajte naše usluge</Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;