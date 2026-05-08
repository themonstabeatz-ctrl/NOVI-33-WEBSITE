import React, { useEffect, useRef, useState } from "react";
import { Helmet } from "react-helmet";
import { useLanguage } from "../context/LanguageContext";
import { getSEO } from "../utils/seoConfig";

const Gallery = () => {
  const { translate } = useLanguage();
  const [selectedImage, setSelectedImage] = useState(null);
  const [isLightboxOpen, setIsLightboxOpen] = useState(false);

  // Sample images - only 2 for demonstration as requested
  const galleryImages = [
    {
      id: 1,
      src: "https://images.unsplash.com/photo-1544161515-4ab6ce6db874?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
      alt: "Spa Treatment 1"
    },
    {
      id: 2,
      src: "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
      alt: "Spa Treatment 2"
    }
  ];

  // Create array of 42 images (40 placeholders + 2 real images)
  const allImages = [];
  for (let i = 0; i < 42; i++) {
    if (i < 2) {
      allImages.push(galleryImages[i]);
    } else {
      allImages.push({
        id: i + 1,
        src: `https://via.placeholder.com/400x300/d4af37/000000?text=Image+${i + 1}`,
        alt: `Gallery Image ${i + 1}`
      });
    }
  }

  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  // Logo transformation on scroll
  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY;
      const galleryHeroSection = document.querySelector('.gallery-hero-fixed');
      const galleryHeroLogo = document.querySelector('.gallery-hero-logo');
      const galleryHeroTitle = document.querySelector('.gallery-hero-title');
      const galleryHeroSubtitle = document.querySelector('.gallery-hero-subtitle');
      
      if (!galleryHeroSection || !galleryHeroLogo) return;
      
      const heroHeight = galleryHeroSection.offsetHeight;
      const scrollPercent = Math.min(scrollPosition / heroHeight, 1);
      
      if (scrollPercent > 0.05) {
        const opacity = Math.max(1 - (scrollPercent - 0.05) * 3, 0);
        const scale = Math.max(1 - (scrollPercent - 0.05) * 1.5, 0.2);
        
        galleryHeroLogo.style.opacity = opacity;
        galleryHeroLogo.style.transform = `scale(${scale})`;
        galleryHeroLogo.style.filter = `blur(${(scrollPercent - 0.05) * 15}px)`;
        
        // Fade out title
        if (galleryHeroTitle) {
          galleryHeroTitle.style.opacity = opacity;
          galleryHeroTitle.style.transform = `translateY(-${(scrollPercent - 0.05) * 80}px)`;
        }
        
        // Fade out subtitle
        if (galleryHeroSubtitle) {
          galleryHeroSubtitle.style.opacity = opacity;
          galleryHeroSubtitle.style.transform = `translateY(-${(scrollPercent - 0.05) * 60}px)`;
        }
      } else {
        galleryHeroLogo.style.opacity = 1;
        galleryHeroLogo.style.transform = 'scale(1)';
        galleryHeroLogo.style.filter = 'blur(0px)';
        
        if (galleryHeroTitle) {
          galleryHeroTitle.style.opacity = '1';
          galleryHeroTitle.style.transform = 'translateY(0)';
        }
        
        if (galleryHeroSubtitle) {
          galleryHeroSubtitle.style.opacity = '1';
          galleryHeroSubtitle.style.transform = 'translateY(0)';
        }
      }
    };
    
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Handle image click for lightbox
  const handleImageClick = (image) => {
    setSelectedImage(image);
    setIsLightboxOpen(true);
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
  };

  // Close lightbox
  const closeLightbox = () => {
    setIsLightboxOpen(false);
    setSelectedImage(null);
    document.body.style.overflow = 'auto'; // Restore scrolling
  };

  // Handle escape key to close lightbox
  useEffect(() => {
    const handleEscapeKey = (event) => {
      if (event.key === 'Escape' && isLightboxOpen) {
        closeLightbox();
      }
    };

    document.addEventListener('keydown', handleEscapeKey);
    return () => document.removeEventListener('keydown', handleEscapeKey);
  }, [isLightboxOpen]);

  // Create rows of 3 images each (14 rows total)
  const imageRows = [];
  for (let i = 0; i < allImages.length; i += 3) {
    imageRows.push(allImages.slice(i, i + 3));
  }

  const gallerySEO = getSEO('gallery');

  return (
    <div className="gallery-container">
      <Helmet>
        <title>{gallerySEO.title}</title>
        <meta name="description" content={gallerySEO.description} />
        <meta name="keywords" content={gallerySEO.keywords} />
        <link rel="canonical" href={gallerySEO.canonical} />
      </Helmet>

      {/* Fixed Hero Section with Background Image */}
      <section className="gallery-hero-fixed">
        <div className="gallery-hero-video-container">
          <div className="gallery-hero-background-image"></div>
          <div className="gallery-hero-overlay"></div>
        </div>
        
        <div className="gallery-hero-content">
          <div className="gallery-hero-logo">
            <img 
              src="https://customer-assets.emergentagent.com/job_83ed575e-3634-46be-8586-79a3348def97/artifacts/7sfhgz1m_Bua%20luang%20logo.png"
              alt="Bua Luang Logo"
              className="hero-logo-image"
            />
          </div>
          <h1 className="gallery-hero-title">{translate("galleryHeroTitle")}</h1>
          <div className="gallery-hero-divider"></div>
          <p className="gallery-hero-subtitle">{translate("galleryHeroSubtitle")}</p>
        </div>
      </section>

      {/* Parallax Content Section with Image Grid */}
      <div className="gallery-parallax-content">
        <div className="gallery-grid-container">
          {imageRows.map((row, rowIndex) => (
            <div key={rowIndex} className="gallery-row">
              {row.map((image, imageIndex) => (
                <div 
                  key={image.id} 
                  className={`gallery-image-wrapper gallery-image-${imageIndex + 1}`}
                  onClick={() => handleImageClick(image)}
                >
                  <img 
                    src={image.src} 
                    alt={image.alt}
                    className="gallery-image"
                    loading="lazy"
                  />
                  <div className="gallery-image-overlay">
                    <div className="gallery-image-zoom-icon">+</div>
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Lightbox Modal */}
      {isLightboxOpen && selectedImage && (
        <div className="gallery-lightbox" onClick={closeLightbox}>
          <div className="gallery-lightbox-content" onClick={(e) => e.stopPropagation()}>
            <button className="gallery-lightbox-close" onClick={closeLightbox}>
              ×
            </button>
            <img 
              src={selectedImage.src} 
              alt={selectedImage.alt}
              className="gallery-lightbox-image"
            />
            <div className="gallery-lightbox-caption">
              {selectedImage.alt}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Gallery;
