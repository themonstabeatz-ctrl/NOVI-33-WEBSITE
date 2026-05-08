/**
 * ✅ SHARED PRICE BLOCK COMPONENT
 * 
 * Pravilo: Frontend SAMO prikazuje ono što dobije od backend-a
 * ❌ Frontend NIKAD ne računa % niti price*(1-discount)
 * 
 * Očekivana NORMALIZOVANA polja:
 * - original_price
 * - final_price  
 * - discount_percent
 * - has_discount
 */

import React from 'react';

// ✅ Format RSD - "9.200 RSD"
export function formatRSD(n) {
  const num = Number(n || 0);
  return `${num.toLocaleString("sr-RS")} RSD`;
}

/**
 * ✅ PriceBlock - prikazuje popust ako postoji
 * Koristi SAMO backend podatke, NEMA kalkulacija
 */
export function PriceBlock({ 
  original_price, 
  final_price, 
  discount_percent, 
  has_discount,
  style = {},
  showBadge = true,
  size = 'normal' // 'small' | 'normal' | 'large'
}) {
  const original = Number(original_price || 0);
  const final = Number(final_price || original);
  const discountPct = Number(discount_percent || 0);

  // ✅ Prikaz popusta SAMO ako backend kaže da postoji
  const showDiscount = Boolean(has_discount) 
    && Number.isFinite(original) 
    && Number.isFinite(final) 
    && final < original;

  // Size styles
  const sizeStyles = {
    small: { original: '0.85rem', final: '1rem', badge: '0.7rem' },
    normal: { original: '0.9rem', final: '1.1rem', badge: '0.75rem' },
    large: { original: '1.1rem', final: '1.5rem', badge: '0.85rem' },
  };
  const sizes = sizeStyles[size] || sizeStyles.normal;

  if (!showDiscount) {
    // ✅ Nema popusta - prikaži originalnu cenu
    return (
      <div className="price-block" style={style}>
        <div 
          className="price" 
          style={{ 
            fontWeight: 700,
            color: '#d4af37',
            fontSize: sizes.final
          }}
        >
          {formatRSD(original || final)}
        </div>
      </div>
    );
  }

  // ✅ Ima popust - prikaži obe cene i badge
  return (
    <div className="price-block" style={style}>
      {/* Original price (strikethrough) */}
      <div 
        className="old-price" 
        style={{ 
          textDecoration: "line-through", 
          opacity: 0.7,
          color: '#888',
          fontSize: sizes.original,
          marginBottom: '0.15rem'
        }}
      >
        {formatRSD(original)}
      </div>
      
      {/* Final price + discount badge */}
      <div 
        className="discount-row" 
        style={{ 
          fontWeight: 700,
          color: '#d4af37',
          fontSize: sizes.final,
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}
      >
        {formatRSD(final)}
        {showBadge && discountPct > 0 && (
          <span 
            className="discount-badge"
            style={{ 
              fontSize: sizes.badge, 
              color: '#4ade80',
              fontWeight: 600
            }}
          >
            -{discountPct}%
          </span>
        )}
      </div>
    </div>
  );
}

/**
 * ✅ Inline PriceBlock za manje prostore (SPA zone itd.)
 */
export function InlinePriceBlock({ 
  original_price, 
  final_price, 
  discount_percent, 
  has_discount,
  prefix = ''
}) {
  const original = Number(original_price || 0);
  const final = Number(final_price || original);
  const discountPct = Number(discount_percent || 0);

  const showDiscount = Boolean(has_discount) 
    && Number.isFinite(original) 
    && Number.isFinite(final) 
    && final < original;

  if (!showDiscount) {
    return (
      <span style={{ color: '#d4af37', fontWeight: 600 }}>
        {prefix}{formatRSD(original || final)}
      </span>
    );
  }

  return (
    <span style={{ color: '#d4af37' }}>
      {prefix}
      <span style={{ textDecoration: 'line-through', opacity: 0.6, marginRight: '0.5rem' }}>
        {formatRSD(original)}
      </span>
      <span style={{ fontWeight: 600 }}>
        {formatRSD(final)}
      </span>
      <span style={{ fontSize: '0.8em', color: '#4ade80', marginLeft: '0.25rem' }}>
        (-{discountPct}%)
      </span>
    </span>
  );
}

export default PriceBlock;
