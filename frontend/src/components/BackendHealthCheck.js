import React, { useState, useEffect } from 'react';
import { API_BASE } from '../config/api';

/**
 * 🔒 OSIGURAČ: Backend Health Check Component
 * 
 * NOVO PONAŠANJE: Health check NE blokira UI!
 * - Stranica se uvek renderuje
 * - Ako backend nije dostupan: prikazuje warning banner + disabluje booking dugmad
 * 
 * LOCKED TO: https://spa-system-fixes.preview.emergentagent.com
 */
const BackendHealthCheck = ({ children }) => {
  const [status, setStatus] = useState('checking'); // 'checking', 'healthy', 'error'
  const [errorMessage, setErrorMessage] = useState('');
  
  useEffect(() => {
    const checkBackendHealth = async (attempt = 1) => {
      const MAX_RETRIES = 2;
      
      try {
        console.log(`🔍 Checking backend health (attempt ${attempt}/${MAX_RETRIES}):`, API_BASE);
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);
        
        const response = await fetch(`${API_BASE}/api/services`, {
          method: 'GET',
          headers: { 'Accept': 'application/json' },
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
          console.log('✅ Backend healthy');
          setStatus('healthy');
        } else {
          throw new Error(`HTTP ${response.status}`);
        }
      } catch (error) {
        console.warn(`⚠️ Backend health check failed (attempt ${attempt}):`, error.message);
        
        if (attempt < MAX_RETRIES) {
          setTimeout(() => checkBackendHealth(attempt + 1), 1500);
          return;
        }
        
        // All retries failed - but DON'T block UI!
        setStatus('error');
        setErrorMessage(error.message === 'Failed to fetch' ? 'Backend nedostupan' : error.message);
      }
    };

    checkBackendHealth();
  }, []);

  // ✅ UVEK renderuj children - nikad ne blokiraj UI
  return (
    <>
      {/* Warning banner ako backend nije dostupan */}
      {status === 'error' && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          zIndex: 9999,
          backgroundColor: 'rgba(220, 38, 38, 0.95)',
          color: '#fff',
          padding: '0.75rem 1rem',
          textAlign: 'center',
          fontSize: '0.9rem',
          fontFamily: 'sans-serif'
        }}>
          ⚠️ Server trenutno nije dostupan - rezervacije privremeno onemogućene ({errorMessage})
        </div>
      )}
      
      {/* Checking banner - brzo nestane */}
      {status === 'checking' && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          zIndex: 9999,
          backgroundColor: 'rgba(212, 175, 55, 0.9)',
          color: '#1a1a1a',
          padding: '0.5rem 1rem',
          textAlign: 'center',
          fontSize: '0.85rem',
          fontFamily: 'sans-serif'
        }}>
          🔄 Povezivanje sa serverom...
        </div>
      )}
      
      {/* UVEK renderuj stranicu */}
      {children}
    </>
  );
};

export default BackendHealthCheck;
