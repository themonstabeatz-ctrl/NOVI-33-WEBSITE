import React from "react";
import { useLanguage } from "../context/LanguageContext";
import { Instagram, Mail, Phone, MapPin, Clock } from "lucide-react";

const Footer = () => {
  const { translate } = useLanguage();

  return (
    <footer className="footer-container">
      <div className="footer-content">
        {/* Contact Information */}
        <div className="footer-section">
          <h3 className="footer-title">{translate("contactTitle")}</h3>
          <div className="footer-contact">
            <div className="footer-contact-item">
              <Mail className="footer-icon" />
              <span>bualuangthailandspa@gmail.com</span>
            </div>
            <div className="footer-contact-item">
              <Phone className="footer-icon" />
              <span>+381 62 625 500</span>
            </div>
            <div className="footer-contact-item">
              <MapPin className="footer-icon" />
              <span>Abebe Bikile 10A, Zemun, Beograd 11080, Srbija</span>
            </div>
            <div className="footer-contact-item">
              <Clock className="footer-icon" />
              <span>Pon - Ned: 10:00 - 22:00</span>
            </div>
          </div>
        </div>

        {/* Social Media */}
        <div className="footer-section">
          <h3 className="footer-title">{translate("followUs")}</h3>
          <div className="footer-social">
            <a 
              href="https://www.instagram.com/bualuang_thai_spa" 
              target="_blank" 
              rel="noopener noreferrer"
              className="footer-social-link"
            >
              <Instagram className="footer-social-icon" />
              <span>@bualuang_thai_spa</span>
            </a>
          </div>
        </div>
      </div>

      {/* Copyright */}
      <div className="footer-bottom">
        <div className="footer-mandala-pattern"></div>
        <p className="footer-copyright">
          © 2025 Bua Luang Thai Spa. Sva prava zadržana.
        </p>
      </div>
    </footer>
  );
};

export default Footer;