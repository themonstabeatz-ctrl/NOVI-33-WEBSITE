import { useEffect, useRef, useState } from 'react';

/**
 * Custom hook for lazy loading video elements
 * Uses Intersection Observer to defer video loading until visible
 * 
 * @param {number} threshold - Intersection threshold (0-1)
 * @param {string} rootMargin - Root margin for intersection observer
 * @returns {Object} - { videoRef, isLoaded } - ref to attach to video element and load status
 */
export const useLazyVideo = (threshold = 0.1, rootMargin = '50px') => {
  const videoRef = useRef(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const videoElement = videoRef.current;
    if (!videoElement) return;

    const observerOptions = {
      root: null,
      rootMargin,
      threshold
    };

    const handleIntersection = (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && !isLoaded) {
          // Start loading the video
          const video = entry.target;
          const source = video.querySelector('source');
          
          if (source && source.dataset.src) {
            source.src = source.dataset.src;
            video.load();
            setIsLoaded(true);
          }
        }
      });
    };

    const observer = new IntersectionObserver(handleIntersection, observerOptions);
    observer.observe(videoElement);

    return () => {
      if (videoElement) {
        observer.unobserve(videoElement);
      }
    };
  }, [threshold, rootMargin, isLoaded]);

  return { videoRef, isLoaded };
};
