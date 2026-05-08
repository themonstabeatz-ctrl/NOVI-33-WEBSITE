# 🗺️ Sitemap Route Mapping - www.bualuangthaispa.rs

## ⚠️ VAŽNA NAPOMENA

Novi sitemap.xml sadrži rute koje se **razlikuju** od trenutnih React ruta u aplikaciji.

---

## 📊 Mapiranje Ruta

### Srpski (SR)
| Sitemap URL | Trenutna React Ruta | Status | Potrebna Akcija |
|-------------|---------------------|--------|------------------|
| `/` | `/` (Home) | ✅ OK | Nema |
| `/usluge` | `/massage` + `/spa` | ⚠️ RAZLIČITO | Potreban redirect ili nova ruta |
| `/cenovnik` | Nema | ❌ NE POSTOJI | Kreirati novu stranicu |
| `/rezervacije` | `/contact` (booking form) | ⚠️ RAZLIČITO | Redirect ili rename |
| `/vauceri` | Nema | ❌ NE POSTOJI | Kreirati novu stranicu |
| `/kontakt` | `/contact` | ⚠️ RAZLIČITO | Redirect `/kontakt` → `/contact` |

### Engleski (EN)
| Sitemap URL | Potrebna React Ruta | Status |
|-------------|---------------------|--------|
| `/en` | `/en` ili `/` (sa lang param) | ❌ NE POSTOJI |
| `/en/services` | `/en/services` | ❌ NE POSTOJI |
| `/en/pricing` | `/en/pricing` | ❌ NE POSTOJI |
| `/en/booking` | `/en/booking` | ❌ NE POSTOJI |
| `/en/vouchers` | `/en/vouchers` | ❌ NE POSTOJI |
| `/en/contact` | `/en/contact` | ❌ NE POSTOJI |

---

## 🔧 Preporučena Rešenja

### Opcija 1: Ažurirati React Router (Preporučeno za SEO)
Kreirajte nove rute koje odgovaraju sitemap-u:

```javascript
// App.js ili routes configuration
<Routes>
  {/* Srpski */}
  <Route path="/" element={<Home />} />
  <Route path="/usluge" element={<Services />} />  {/* Nova stranica */}
  <Route path="/cenovnik" element={<Pricing />} /> {/* Nova stranica */}
  <Route path="/rezervacije" element={<Booking />} /> {/* Contact form */}
  <Route path="/vauceri" element={<Vouchers />} /> {/* Nova stranica */}
  <Route path="/kontakt" element={<Contact />} />
  
  {/* Engleski */}
  <Route path="/en" element={<Home lang="en" />} />
  <Route path="/en/services" element={<Services lang="en" />} />
  <Route path="/en/pricing" element={<Pricing lang="en" />} />
  <Route path="/en/booking" element={<Booking lang="en" />} />
  <Route path="/en/vouchers" element={<Vouchers lang="en" />} />
  <Route path="/en/contact" element={<Contact lang="en" />} />
  
  {/* Stare rute - redirects */}
  <Route path="/massage" element={<Navigate to="/usluge" replace />} />
  <Route path="/spa" element={<Navigate to="/usluge" replace />} />
  <Route path="/contact" element={<Navigate to="/kontakt" replace />} />
</Routes>
```

### Opcija 2: Dodati Redirects u .htaccess
Ako ne želite da menjate React rute, dodajte redirects:

```apache
# .htaccess redirects
RewriteRule ^usluge$ /massage [R=301,L]
RewriteRule ^cenovnik$ /spa [R=301,L]
RewriteRule ^rezervacije$ /contact [R=301,L]
RewriteRule ^kontakt$ /contact [R=301,L]
```

### Opcija 3: Ažurirati Sitemap na Trenutne Rute (Najlakše)
Vratiti sitemap.xml na trenutne React rute:

```xml
<url><loc>https://www.bualuangthaispa.rs/</loc></url>
<url><loc>https://www.bualuangthaispa.rs/massage</loc></url>
<url><loc>https://www.bualuangthaispa.rs/spa</loc></url>
<url><loc>https://www.bualuangthaispa.rs/contact</loc></url>
<url><loc>https://www.bualuangthaispa.rs/about</loc></url>
<url><loc>https://www.bualuangthaispa.rs/gallery</loc></url>
```

---

## 🎯 Šta Preporučujem?

### Za Postojeću Aplikaciju (Trenutno stanje):
**Preporuka: Opcija 3** - Vratiti sitemap na trenutne rute
- ✅ Nema breaking changes
- ✅ Funkcioniše odmah
- ✅ Sve stranice već postoje

### Za Novu Verziju Sajta:
**Preporuka: Opcija 1** - Kreirati nove stranice
- ✅ Bolje za SEO (srpske reči u URL-u)
- ✅ Čistija struktura
- ⚠️ Zahteva razvoj novih stranica

---

## 📝 Novi Stranice Koje Treba Kreirati

### 1. **/usluge** (Services)
**Sadržaj:**
- Lista svih masaža (iz /massage)
- Lista svih SPA tretmana (iz /spa)
- Kombinovana stranica ili navigacija ka obe sekcije

### 2. **/cenovnik** (Pricing)
**Sadržaj:**
- Tabela svih usluga sa cenama
- PDF download cenovnika
- Call-to-action za rezervaciju

### 3. **/vauceri** (Vouchers)
**Sadržaj:**
- Informacije o poklon vaučerima
- Forma za kupovinu vaučera
- Različiti paketi (60min, 90min, 120min)
- Online plaćanje ili uputstva

### 4. **/kontakt** vs **/contact**
**Odluka:**
- Zadržati `/contact` i dodati redirect sa `/kontakt`
- Ili preimenovati u `/kontakt` i dodati redirect sa `/contact`

### 5. **/rezervacije** vs **/contact**
**Odluka:**
- Kreirati dedikovan `/rezervacije` samo za booking form
- Ili redirect `/rezervacije` → `/contact`

---

## 🌍 Multi-Language Routing

### Trenutno Stanje:
- Language switcher u header-u
- Sav sadržaj na istim rutama (/ , /massage, /spa, itd.)
- Jezik se menja preko context API

### Novo Stanje (prema sitemap-u):
- Potreban `/en` prefix za engleski
- Duplirane rute za svaki jezik
- URL određuje jezik

**Implementacija:**
```javascript
// LanguageProvider
const LanguageProvider = ({ children }) => {
  const location = useLocation();
  const isEnglish = location.pathname.startsWith('/en');
  const [language, setLanguage] = useState(isEnglish ? 'en' : 'sr');
  
  // Auto-detect language from URL
  useEffect(() => {
    if (location.pathname.startsWith('/en')) {
      setLanguage('en');
    } else {
      setLanguage('sr');
    }
  }, [location]);
  
  return (
    <LanguageContext.Provider value={{ language, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};
```

---

## ✅ Action Items

Pre deploymenta, odlučite:

- [ ] Da li želite nove stranice (`/usluge`, `/cenovnik`, `/vauceri`)?
- [ ] Da li želite `/en` prefix za engleski jezik?
- [ ] Da li želite redirects ili nove rute?
- [ ] Da li želite ažurirati sitemap na trenutne rute?

**Trenutno:** Sitemap ima nove rute koje **NE POSTOJE** u aplikaciji.

**Potrebna odluka:** Ili kreirati nove stranice, ili ažurirati sitemap.

---

**Datum:** 12. Novembar 2025  
**Status:** ⚠️ SITEMAP I APLIKACIJA NISU USKLAĐENI
