// SEO Configuration for all pages
// Import this in each page component and use with react-helmet

export const seoConfig = {
  home: {
    title: "Bua Luang Thai Spa Beograd — Tradicionalna Thai masaža & luksuzni SPA",
    description: "Thai masaže, sauna, parno kupatilo i spa paketi u Zemunu. Online rezervacije, poklon vaučeri, profesionalni terapeuti.",
    keywords: "masaža beograd, spa beograd, tajlandska masaža, thai masaža, wellness beograd, relaks masaža, bua luang, thai spa beograd",
    canonical: "https://www.bualuangthaispa.rs/",
    ogImage: "https://www.bualuangthaispa.rs/og-cover.jpg"
  },
  
  homeEn: {
    title: "Bua Luang Thai Spa Belgrade — Traditional Thai Massage & Luxury SPA",
    description: "Thai massages, sauna, steam room and SPA packages in Zemun. Online booking, gift vouchers, professional therapists.",
    keywords: "massage belgrade, spa belgrade, thai massage, wellness belgrade, relax massage, bua luang, thai spa belgrade",
    canonical: "https://www.bualuangthaispa.rs/en",
    ogImage: "https://www.bualuangthaispa.rs/og-cover-en.jpg"
  },
  
  massage: {
    title: "Thai Masaže Beograd | Cenovnik & Online Rezervacija - Bua Luang Spa",
    description: "Tradicionalne thai masaže u Beogradu. Aroma terapija, masaža toplim uljem, masaža za parove, refleksna masaža. Cene od 2,400 RSD. Rezervišite online na Bua Luang Thai Spa!",
    keywords: "thai masaža beograd, tajlandska masaža, masaža za parove, aroma terapija, masaža toplim uljem, refleksna masaža, cenovnik masaža beograd",
    canonical: "https://www.bualuangthaispa.rs/massage",
    ogImage: "https://www.bualuangthaispa.rs/og-image-massage.jpg"
  },
  
  spa: {
    title: "Luksuzni SPA Tretmani Beograd | Royal Thai Ritual & Wellness - Bua Luang",
    description: "Ekskluzivni SPA paketi u Beogradu. Royal Thai Ritual, Detox Harmony, Aroma Escape, spa tretmani za parove. Cene od 6,500 RSD. Rezervišite luksuzno opuštanje!",
    keywords: "spa beograd, luksuzni spa, royal thai ritual, detox tretman, spa za parove, wellness beograd, spa paketi, relaksacija beograd",
    canonical: "https://www.bualuangthaispa.rs/spa",
    ogImage: "https://www.bualuangthaispa.rs/og-image-spa.jpg"
  },
  
  contact: {
    title: "Kontakt & Rezervacije | Bua Luang Thai Spa Beograd - Online Zakazivanje",
    description: "Zakažite termin u Bua Luang Thai Spa Beograd. Online rezervacija za masaže i SPA tretmane. Telefon, email, adresa, radno vreme. Najbolji spa u Beogradu!",
    keywords: "kontakt spa beograd, rezervacija masaže, zakazivanje spa tretmana, bua luang kontakt, thai spa rezervacija beograd",
    canonical: "https://www.bualuangthaispa.rs/contact",
    ogImage: "https://www.bualuangthaispa.rs/og-image.jpg"
  },
  
  about: {
    title: "O Nama | Bua Luang Thai Spa Beograd - Autentični Tajlandski Spa Centar",
    description: "Upoznajte Bua Luang Thai Spa - autentičan tajlandski spa u srcu Beograda. Naša priča, filozofija, sertifikovane terapeutkinje, tradicionalne tehnike. Vaše putovanje ka unutrašnjem miru.",
    keywords: "o nama bua luang, tajlandski spa beograd, autentični thai spa, thai terapeutkinje, tradicionalna masaža, spa filozofija",
    canonical: "https://www.bualuangthaispa.rs/about",
    ogImage: "https://www.bualuangthaispa.rs/og-image.jpg"
  },
  
  gallery: {
    title: "Galerija | Bua Luang Thai Spa Beograd - Foto & Video Spa Ambijenta",
    description: "Pogledajte našu galeriju - luksuzni spa prostori, tradicionalni tajlandski ambijent, profesionalne terapeutkinje. Doživite mir i lepotu Bua Luang Thai Spa Beograd!",
    keywords: "galerija spa beograd, spa ambijent, thai spa foto, luksuzni spa prostori, bua luang galerija",
    canonical: "https://www.bualuangthaispa.rs/gallery",
    ogImage: "https://www.bualuangthaispa.rs/og-image-gallery.jpg"
  }
};

// Helper function to get SEO data for a specific page
export const getSEO = (pageName) => {
  return seoConfig[pageName] || seoConfig.home;
};
