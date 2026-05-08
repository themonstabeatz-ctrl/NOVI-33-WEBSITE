# 📝 SEO Placeholders & TODO Lista

## ⚠️ Potrebno Dodati Pre Deploymenta

### 1. **Google Maps CID** (Customer ID)
**Lokacija:** `/app/frontend/public/index.html` - Schema.org JSON-LD

**Trenutno stanje:**
```json
"sameAs": [
  "https://www.instagram.com/bualuang_thai_spa"
]
```

**Potrebno dodati:**
```json
"sameAs": [
  "https://maps.google.com/?cid=YOUR_GOOGLE_MAPS_CID",
  "https://www.instagram.com/bualuang_thai_spa",
  "https://www.facebook.com/YOUR_FACEBOOK_PAGE"
]
```

**Kako dobiti Google Maps CID:**
1. Idite na Google My Business: https://business.google.com
2. Kreirajte ili verifikujte business listing
3. Otvorite business profil na Google Maps
4. CID je veliki broj u URL-u nakon `?cid=`

**Primer:**
`https://maps.google.com/?cid=1234567890123456789`

---

### 2. **Facebook Stranica**
**Lokacija:** Schema.org JSON-LD (sameAs array)

**Potrebno:**
- Kreirati Facebook Business Page
- Dodati URL u Schema markup

**Format:**
`https://www.facebook.com/bualuangthaispa` (ili kako god se zove stranica)

---

### 3. **OG Cover Image** (og-cover.jpg)
**Lokacija:** `/app/frontend/public/og-cover.jpg`

**Trenutno stanje:** ❌ NE POSTOJI

**Potrebno:**
- Kreirati sliku 1200x630 pixels
- Format: JPG ili PNG
- Preporučen sadržaj:
  - Logo "Bua Luang Thai Spa"
  - Pozadinska slika spa ambijenta
  - Tekst: "Thai Masaže & Luksuzni SPA"
  - Lokacija: "Zemun, Beograd"

**Postaviti na:**
- `/app/frontend/public/og-cover.jpg`

**Alternativno:** Ako želite da zadržite postojeću sliku, promenite u `index.html`:
```html
<!-- Umesto -->
<meta property="og:image" content="https://www.bualuangthaispa.rs/og-cover.jpg" />

<!-- Vratite na -->
<meta property="og:image" content="https://www.bualuangthaispa.rs/og-image.jpg" />
```

---

### 4. **Logo PNG**
**Lokacija:** `/app/frontend/public/logo.png`

**Potrebno:**
- Transparentan PNG logo (512x512px ili veći)
- Postaviti u public folder
- Koristiti u Schema.org markup-u

---

### 5. **Google Analytics Tracking ID**
**Lokacija:** `/app/frontend/public/index.html`

**Potrebno dodati:**
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

**Kako dobiti:**
1. Idite na https://analytics.google.com
2. Kreirajte GA4 property
3. Kopirajte Measurement ID (počinje sa G-)
4. Zamenite `G-XXXXXXXXXX` sa vašim ID-jem

---

### 6. **Google Search Console Verification**
**Potrebno dodati u `<head>` sekciju:**
```html
<meta name="google-site-verification" content="YOUR_VERIFICATION_CODE" />
```

**Kako dobiti:**
1. Idite na https://search.google.com/search-console
2. Dodajte property: www.bualuangthaispa.rs
3. Izaberite "HTML tag" metod verifikacije
4. Kopirajte content value
5. Dodajte u index.html

---

### 7. **Dodatne Social Media Stranice**
Ako imate dodatne profile, dodajte u Schema.org `sameAs` array:

```json
"sameAs": [
  "https://maps.google.com/?cid=YOUR_CID",
  "https://www.instagram.com/bualuang_thai_spa",
  "https://www.facebook.com/YOUR_PAGE",
  "https://www.tiktok.com/@YOUR_PROFILE",
  "https://www.linkedin.com/company/YOUR_COMPANY"
]
```

---

## ✅ Checklist Pre Deploymenta

- [ ] Google Maps CID dodat u Schema.org
- [ ] Facebook stranica kreirana i linkovana
- [ ] `og-cover.jpg` kreiran i postavljen (1200x630px)
- [ ] `logo.png` postavljen u public folder (512x512px)
- [ ] Google Analytics tracking ID dodat
- [ ] Google Search Console verifikacija
- [ ] Sve social media profile ažurirani u Schema.org
- [ ] SSL sertifikat instaliran
- [ ] Domain DNS podešen na hosting
- [ ] robots.txt i sitemap.xml dostupni na root-u

---

## 📋 Post-Deployment Verifikacija

Nakon postavljanja sajta na www.bualuangthaispa.rs:

### 1. Testirajte Schema Markup
**URL:** https://validator.schema.org/
- Unesite: www.bualuangthaispa.rs
- Proverite da li nema grešaka
- Verifikujte da se prikazuju svi podaci

### 2. Testirajte Rich Results
**URL:** https://search.google.com/test/rich-results
- Unesite: www.bualuangthaispa.rs
- Proverite da li su "DaySpa", "Offer", i "OpeningHours" validni

### 3. Testirajte OG Tags
**URL:** https://www.opengraph.xyz/
- Unesite: www.bualuangthaispa.rs
- Proverite preview kako izgleda na Facebooku/Instagramu

### 4. Testirajte Sitemap
- Otvorite: https://www.bualuangthaispa.rs/sitemap.xml
- Verifikujte da se učitava ispravno
- Submitujte u Google Search Console

---

## 🔗 Korisni Linkovi

- **Schema Validator:** https://validator.schema.org/
- **Rich Results Test:** https://search.google.com/test/rich-results
- **OG Debugger:** https://www.opengraph.xyz/
- **Google My Business:** https://business.google.com
- **Google Analytics:** https://analytics.google.com
- **Search Console:** https://search.google.com/search-console
- **PageSpeed Insights:** https://pagespeed.web.dev/

---

**Datum kreiranja:** 12. Novembar 2025  
**Status:** 🟡 ČEKA DOPUNU PLACEHOLDER VREDNOSTI
