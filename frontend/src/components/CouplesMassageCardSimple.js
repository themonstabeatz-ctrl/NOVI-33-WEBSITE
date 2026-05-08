import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Link } from "react-router-dom";

// ✅ HELPER: Format RSD - "9.200 RSD"
const formatRSD = (n) => {
  const num = Number(n || 0);
  return `${num.toLocaleString("sr-RS")} RSD`;
};

const CouplesMassageCardSimple = ({ translate }) => {
  // ✅ Fixed prices - NE RAČUNAMO popuste, samo prikazujemo fiksne vrednosti
  // Backend ili recepcija definiše cene, frontend samo prikazuje
  const DURATION = 60;
  const TOTAL_DURATION = 120; // 2 persons x 60 min
  
  // ✅ Cene kao što bi ih backend vratio
  const original_price = 8800; // 2 x 4400 RSD
  const final_price = 7920;    // Već izračunato (sa popustom)
  const discount_percent = 10;
  const has_discount = true;

  return (
    <Card 
      className="massage-card couples-card-content" 
      style={{ 
        position: 'relative', 
        minHeight: '400px',
        display: 'flex', 
        flexDirection: 'column'
      }}
    >
      <CardHeader style={{ position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <CardTitle className="massage-name">{translate("sportsMassage")}</CardTitle>
          
          {/* Discount Badge */}
          {has_discount && (
            <img 
              src="/discount-10.png" 
              alt={`-${discount_percent}%`}
              style={{ 
                width: '54px',
                height: '54px', 
                objectFit: 'contain',
                marginRight: '1rem'
              }}
            />
          )}
        </div>
      </CardHeader>
      
      <CardContent style={{ 
        position: 'relative', 
        zIndex: 1, 
        paddingTop: '0.5rem', 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'space-between'
      }}>
        <div>
          <p style={{
            color: '#d4af37',
            fontSize: '1rem',
            marginBottom: '1rem',
            lineHeight: '1.6'
          }}>
            {translate("couplesMassageSimpleDesc") || "Tradicionalna tajlandska masaža za dvoje - 60 minuta po osobi"}
          </p>
          
          <div style={{
            backgroundColor: 'rgba(212, 175, 55, 0.1)',
            border: '1px solid #d4af37',
            borderRadius: '8px',
            padding: '1rem',
            marginBottom: '1.5rem'
          }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              marginBottom: '0.5rem',
              color: '#d4af37'
            }}>
              <span>{translate("person1") || "Osoba 1"}:</span>
              <span>60 min</span>
            </div>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              color: '#d4af37'
            }}>
              <span>{translate("person2") || "Osoba 2"}:</span>
              <span>60 min</span>
            </div>
            <div style={{
              marginTop: '0.75rem',
              paddingTop: '0.75rem',
              borderTop: '1px solid rgba(212, 175, 55, 0.3)',
              display: 'flex',
              justifyContent: 'space-between',
              fontWeight: 'bold',
              fontSize: '1.1rem',
              color: '#d4af37'
            }}>
              <span>{translate("totalDuration") || "Ukupno"}:</span>
              <span>{TOTAL_DURATION} min</span>
            </div>
          </div>
        </div>

        {/* ✅ Price Block - prikazuje popust ako postoji */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-end',
          marginBottom: '1rem',
          paddingRight: '0.5rem'
        }}>
          {has_discount && final_price < original_price ? (
            <>
              {/* Original Price (strikethrough) */}
              <div style={{
                color: '#888',
                fontSize: '1.2rem',
                textDecoration: 'line-through',
                opacity: 0.7,
                marginBottom: '0.25rem'
              }}>
                {formatRSD(original_price)}
              </div>
              
              {/* Final Price */}
              <div style={{
                color: '#d4af37',
                fontWeight: 'bold',
                fontSize: '2.2rem',
                textShadow: '0 2px 4px rgba(0, 0, 0, 0.5)',
                letterSpacing: '1px',
                whiteSpace: 'nowrap'
              }}>
                {formatRSD(final_price)}
              </div>
              
              {/* Discount info */}
              <div style={{
                color: '#4ade80',
                fontSize: '0.85rem',
                marginTop: '0.25rem'
              }}>
                Popust: -{discount_percent}%
              </div>
            </>
          ) : (
            <div style={{
              color: '#d4af37',
              fontWeight: 'bold',
              fontSize: '2.2rem',
              textShadow: '0 2px 4px rgba(0, 0, 0, 0.5)',
              letterSpacing: '1px',
              whiteSpace: 'nowrap'
            }}>
              {formatRSD(original_price)}
            </div>
          )}
        </div>

        <Button 
          className="book-button w-full"
          asChild
        >
          <Link 
            to={`/contact?service=${encodeURIComponent(`${translate('couplesMassage')} - ${TOTAL_DURATION} min`)}&couplesData=${encodeURIComponent(JSON.stringify({
              duration: DURATION,
              totalDuration: TOTAL_DURATION,
              person1: {
                massage: 'Tradicionalna tajlandska masaža',
                duration: DURATION
              },
              person2: {
                massage: 'Tradicionalna tajlandska masaža',
                duration: DURATION
              },
              totalPrice: final_price,
              originalPrice: original_price,
              discount_percent: discount_percent,
              has_discount: has_discount
            }))}`}
          >
            {translate('bookNowBtn') || 'ZAKAŽITE'}
          </Link>
        </Button>
      </CardContent>
    </Card>
  );
};

export default CouplesMassageCardSimple;
