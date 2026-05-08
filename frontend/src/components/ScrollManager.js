import { useEffect } from "react";
import { useLocation } from "react-router-dom";

/**
 * ScrollManager - Robust scroll handler for React Router
 * 
 * CRITICAL: For #top hash, forces HARD scroll to absolute top (scrollY = 0)
 * Multiple fallbacks ensure scroll works even with lazy-loaded content
 */

// Disable browser's automatic scroll restoration
if (typeof window !== 'undefined') {
  window.history.scrollRestoration = "manual";
}

// Force scroll to absolute top with multiple fallbacks
function forceScrollToTop() {
  console.log("📍 ScrollManager: forcing scrollTo(0,0)");
  
  // Immediate scroll
  window.scrollTo({ top: 0, left: 0, behavior: "auto" });
  
  // Fallback 1: requestAnimationFrame (after paint)
  requestAnimationFrame(() => {
    window.scrollTo(0, 0);
  });
  
  // Fallback 2: Short delay for layout shifts
  setTimeout(() => {
    window.scrollTo(0, 0);
  }, 50);
  
  // Fallback 3: Longer delay for video/image loads
  setTimeout(() => {
    window.scrollTo(0, 0);
    console.log(`📍 ScrollManager: final scrollY = ${window.scrollY}`);
  }, 200);
}

export default function ScrollManager() {
  const { pathname, hash } = useLocation();

  useEffect(() => {
    // Special case: #top = force absolute top (scrollY = 0)
    if (hash === "#top") {
      forceScrollToTop();
      return;
    }
    
    // Other hashes: try to scroll to element
    if (hash) {
      const timeoutId = setTimeout(() => {
        const el = document.querySelector(hash);
        if (el) {
          el.scrollIntoView({ behavior: "smooth", block: "start" });
        } else {
          forceScrollToTop();
        }
      }, 100);
      return () => clearTimeout(timeoutId);
    }
    
    // Default: scroll to top on route change
    forceScrollToTop();
  }, [pathname, hash]);

  return null;
}
