/**
 * 📛 DISCOUNT BADGE COMPONENT
 * 
 * Prikazuje sliku badge-a za popust (-5%, -10%, -15%)
 * Koristi slike iz assets/discount/ foldera
 */

import React from 'react';
import discount5 from '../assets/discount/discount-5.png';
import discount10 from '../assets/discount/discount-10.png';
import discount15 from '../assets/discount/discount-15.png';

// Map discount percent to image
const DISCOUNT_BADGE_MAP = {
  5: discount5,
  10: discount10,
  15: discount15,
};

/**
 * DiscountBadge - prikazuje sliku badge-a za popust
 * @param {number} percent - procenat popusta (5, 10, ili 15)
 * @param {number} size - visina slike u px (default 32)
 * @param {object} style - dodatni stil
 */
export function DiscountBadge({ percent, size = 32, style = {} }) {
  const roundedPercent = Math.round(Number(percent || 0));
  const img = DISCOUNT_BADGE_MAP[roundedPercent];
  
  // Ako nemamo sliku za taj procenat, prikaži tekst badge
  if (!img) {
    if (roundedPercent <= 0) return null;
    
    return (
      <span 
        className="discount-badge-text"
        style={{
          background: 'linear-gradient(135deg, #22c55e, #16a34a)',
          color: 'white',
          padding: '4px 8px',
          borderRadius: '4px',
          fontWeight: 'bold',
          fontSize: '0.75rem',
          ...style
        }}
      >
        -{roundedPercent}%
      </span>
    );
  }
  
  return (
    <img 
      src={img} 
      alt={`-${roundedPercent}%`}
      className="discount-badge-img"
      style={{ 
        height: size, 
        width: 'auto',
        objectFit: 'contain',
        ...style 
      }}
    />
  );
}

/**
 * DiscountBadgeSmall - manja verzija za inline prikaz
 */
export function DiscountBadgeSmall({ percent, style = {} }) {
  return <DiscountBadge percent={percent} size={24} style={style} />;
}

/**
 * DiscountBadgeLarge - veća verzija za prominence prikaz
 */
export function DiscountBadgeLarge({ percent, style = {} }) {
  return <DiscountBadge percent={percent} size={48} style={style} />;
}

export default DiscountBadge;
