import React, { createContext, useContext, useState, useEffect } from "react";
import { translations } from "../data/translations";

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  // Get language from URL param, localStorage, or default to "sr"
  const [currentLanguage, setCurrentLanguage] = useState(() => {
    // First check URL param
    const urlParams = new URLSearchParams(window.location.search);
    const urlLang = urlParams.get('lang');
    if (urlLang && translations[urlLang]) {
      return urlLang;
    }
    // Then check localStorage
    const savedLanguage = localStorage.getItem("bua-luang-language");
    return savedLanguage || "sr";
  });

  // Listen for URL changes and update language
  useEffect(() => {
    const handleUrlChange = () => {
      const urlParams = new URLSearchParams(window.location.search);
      const urlLang = urlParams.get('lang');
      if (urlLang && translations[urlLang] && urlLang !== currentLanguage) {
        setCurrentLanguage(urlLang);
      }
    };
    
    // Check on mount and when URL changes
    handleUrlChange();
    window.addEventListener('popstate', handleUrlChange);
    
    return () => window.removeEventListener('popstate', handleUrlChange);
  }, [currentLanguage]);

  // Save language to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem("bua-luang-language", currentLanguage);
  }, [currentLanguage]);

  const translate = (key) => {
    return translations[currentLanguage]?.[key] || translations['sr']?.[key] || key;
  };

  return (
    <LanguageContext.Provider value={{
      currentLanguage,
      setCurrentLanguage,
      translate
    }}>
      {children}
    </LanguageContext.Provider>
  );
};