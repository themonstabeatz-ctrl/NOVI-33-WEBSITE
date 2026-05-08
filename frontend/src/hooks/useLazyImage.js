import { useEffect, useRef, useState } from 'react';

/**
 * Custom hook for lazy loading images
 * @param {string} src - Image source URL
 * @param {string} placeholder - Placeholder image URL (optional)
 * @returns {object} - { imageSrc, isLoaded, imageRef }
 */
export const useLazyImage = (src, placeholder = '') => {
  const [imageSrc, setImageSrc] = useState(placeholder);
  const [isLoaded, setIsLoaded] = useState(false);
  const imageRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setImageSrc(src);
            setIsLoaded(true);
            observer.unobserve(entry.target);
          }
        });
      },
      {
        rootMargin: '50px', // Start loading 50px before image enters viewport
        threshold: 0.01
      }
    );

    if (imageRef.current) {
      observer.observe(imageRef.current);
    }

    return () => {
      if (imageRef.current) {
        observer.unobserve(imageRef.current);
      }
    };
  }, [src]);

  return { imageSrc, isLoaded, imageRef };
};
