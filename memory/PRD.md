# Bua Luang Thai Spa - Frontend Application

## Original Problem Statement
Frontend aplikacija za Thai Spa sa sledećim funkcionalnostima:
- Prikaz masaža i SPA tretmana
- Online booking sistem
- Višejezična podrška (SR, EN, RU, TH)
- Head Spa parallax sekcije sa animacijama
- Termini (kalendar pregled rezervacija)

## Architecture
```
Frontend: React (gold-line-fixer.preview.emergentagent.com)
Backend API: FastAPI (spa-system-fixes.preview.emergentagent.com)
```

### Key Files
- `/app/frontend/src/config/api.js` - Single source of truth za API URL
- `/app/frontend/src/components/BackendHealthCheck.js` - Non-blocking health check
- `/app/frontend/src/pages/HeadSpa.js` - Parallax sekcije sa animacijama
- `/app/frontend/src/pages/Termini.js` - Kalendar pregled
- `/app/frontend/src/pages/Home.js` - Homepage

## What's Been Implemented

### 2025-02-05
- ✅ Backend URL sinhronizacija sa `spa-system-fixes.preview.emergentagent.com`
- ✅ Uklonjeni svi stari domeni iz koda
- ✅ BackendHealthCheck non-blocking
- ✅ API endpointi verifikovani (GET /api/services, GET /api/spa/services)

### Ranije završeno
- ✅ Head Spa parallax sekcije (Naši tretmani, Benefiti, Osvežite se)
- ✅ Card slide-in animacije
- ✅ Video background sa SVG clip-path
- ✅ Višejezična podrška
- ✅ Termini ekran sa kalendarom

## Known Issues
- **BLOCKED**: Backend ignoriše `duration` i `totalPrice` iz booking payload-a (backend bug)

## Prioritized Backlog

### P0 (Critical)
- Testirati booking flow kroz UI

### P1 (High)
- Email Template Customization
- CEO Dashboard development

### P2 (Medium)
- Mobile application development
- Lazy loading za slike na ostalim stranicama

### P3 (Low)
- Refactoring: premestiti Home.js stilove iz App.css u Home.css
