import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { Button } from "./ui/button";
import { Globe } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";

const Header = () => {
  const { currentLanguage, setCurrentLanguage, translate } = useLanguage();
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const languages = [
    { code: "sr", name: "Srpski", flag: "https://flagcdn.com/w40/rs.png" },
    { code: "en", name: "English", flag: "https://flagcdn.com/w40/gb.png" },
    { code: "ru", name: "Русский", flag: "https://flagcdn.com/w40/ru.png" },
    { code: "th", name: "ไทย", flag: "https://flagcdn.com/w40/th.png" },
    { code: "zh", name: "中文", flag: "https://flagcdn.com/w40/cn.png" }
  ];

  const navigation = [
    { path: "/", label: translate("home") },
    { path: "/massage", label: translate("massage") },
    { path: "/spa", label: translate("spa") },
    { path: "/head-spa", label: "HEAD SPA" },
    { path: "/gallery", label: translate("gallery") },
    // REMOVED: { path: "/contact", label: "BOOKING" },
    { path: "/about", label: translate("about") }
  ];

  // Scroll to top when clicking navigation links
  const handleNavClick = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setIsMenuOpen(false); // Close mobile menu if open
  };

  return (
    <header className="header-container">
      <nav className="nav-wrapper">
        {/* Logo on Left */}
        <div className="nav-logo-container">
          <Link to="/">
            <img 
              src="https://customer-assets.emergentagent.com/job_serene-retreat-1/artifacts/r2vm59ex_Bualuang%20logo%20senka.png" 
              alt="Bua Luang Thai Spa" 
              className="nav-logo"
            />
          </Link>
        </div>

        {/* Desktop Navigation */}
        <div className="nav-desktop">
          {navigation.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={handleNavClick}
              className={`nav-link ${
                location.pathname === item.path ? "nav-link-active" : ""
              }`}
            >
              {item.label}
            </Link>
          ))}
        </div>

        {/* Language Selector */}
        <div className="language-selector">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="language-button">
                <img 
                  src={languages.find(lang => lang.code === currentLanguage)?.flag} 
                  alt="" 
                  className="language-flag-img"
                />
                <span className="ml-2">
                  {languages.find(lang => lang.code === currentLanguage)?.name}
                </span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="language-dropdown-custom">
              {languages.map((language) => (
                <DropdownMenuItem
                  key={language.code}
                  onClick={() => setCurrentLanguage(language.code)}
                  className={currentLanguage === language.code ? "bg-accent" : ""}
                >
                  <img 
                    src={language.flag} 
                    alt="" 
                    className="language-flag-img-item"
                  />
                  <span>{language.name}</span>
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Mobile Menu Button */}
        <button
          className="mobile-menu-button"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          <div className={`hamburger ${isMenuOpen ? "active" : ""}`}>
            <span></span>
            <span></span>
            <span></span>
          </div>
        </button>
      </nav>

      {/* Mobile Navigation */}
      <div className={`mobile-nav ${isMenuOpen ? "mobile-nav-open" : ""}`}>
        {navigation.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`mobile-nav-link ${
              location.pathname === item.path ? "mobile-nav-link-active" : ""
            }`}
            onClick={handleNavClick}
          >
            {item.label}
          </Link>
        ))}
      </div>
    </header>
  );
};

export default Header;
