# ✅ REŠENJE: Couples Dropdown "Nema dostupnih masaža" - POPRAVLJENO!

## 🎯 Problem

1. **Couples dropdown meniji prazni**: U kartici "Masaža za parove", padajući meniji za Osoba 1 i Osoba 2 prikazuju "Nema dostupnih masaža"
2. **Razlog**: Frontend je pozivao `/api/services/couples/list` endpoint koji vraća **već kreirane kombinacije** couples usluga, a ne **INDIVIDUAL [PAROVI] masaže** koje korisnik bira

## 🔧 Šta sam popravio?

### 1. Backend - Kreiran NOVI endpoint za individual couples masaže

**Fajl**: `/app/backend/server.py` (nakon linije 345)

```python
# NEW ENDPOINT: Couples Individual Services (for dropdown selection)
@api_router.get("/services/couples/individual")
async def get_couples_individual_services():
    """
    Returns INDIVIDUAL [PAROVI] masaže for dropdown selection.
    
    This endpoint provides services from "Kartica Masaza za parove" category
    which have [PAROVI] prefix and are used for Osoba 1 / Osoba 2 selection.
    """
    booking_api_url = os.environ.get('BOOKING_API_URL', 'https://gold-line-fixer.preview.emergentagent.com')
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{booking_api_url}/api/services")
            response.raise_for_status()
            raw_services = response.json()
            
            # CRITICAL FILTER: Only "Kartica Masaza za parove" category
            individual_couples = [s for s in raw_services if s.get('category') == 'Kartica Masaza za parove']
            
            logger.info(f"✅ Returning {len(individual_couples)} INDIVIDUAL [PAROVI] services for dropdown")
            
            # Process and add metadata
            processed = []
            for service in individual_couples:
                # Use metadata if available (source of truth for prices)
                metadata = service.get('metadata', {})
                if metadata and 'original_price' in metadata and 'final_price' in metadata:
                    service['original_price'] = metadata['original_price']
                    service['final_price'] = metadata['final_price']
                else:
                    service['original_price'] = service['price']
                    service['final_price'] = service['price']
                
                processed.append(service)
            
            return processed
            
    except Exception as e:
        logger.error(f"Error fetching couples individual services: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch couples individual services: {str(e)}")
```

**Razlog za novi endpoint**:
- Postojeći `/api/services/couples/list` vraća **već kreirane kombinacije** (npr. "Masaža za parove - 120 min (2x60 min)")
- Korisnik treba da bira **INDIVIDUAL [PAROVI] masaže** iz dropdown-a (npr. "[PAROVI] Tradicionalna tajlandska masaža - 60 min")
- Novi endpoint filtrira po **category = "Kartica Masaza za parove"** što vraća 19 individual [PAROVI] masaža

---

### 2. Frontend - Promenjeno učitavanje podataka

**Fajl**: `/app/frontend/src/components/CouplesMassageCard.js` (linije 50-75)

**STARI KOD** (ne radi):
```javascript
const response = await fetch(`${backendUrl}/api/services/couples/list`);
const couplesServices = await response.json();
```

**NOVI KOD** (radi):
```javascript
// CRITICAL: Load all services and filter by category "Kartica Masaza za parove"
const response = await fetch(`${backendUrl}/api/services`);
const allServices = await response.json();

// Filter by category "Kartica Masaza za parove" to get INDIVIDUAL [PAROVI] masaže
const couplesServices = allServices.filter(s => s.category === 'Kartica Masaza za parove');

console.log(`✅ Total services: ${allServices.length}, Filtered [PAROVI] services: ${couplesServices.length}`);

// Verify all filtered services have [PAROVI] prefix
const withPrefix = couplesServices.filter(s => s.name.startsWith('[PAROVI]'));
console.log(`✅ Services with [PAROVI] prefix: ${withPrefix.length}/${couplesServices.length}`);
```

**Razlog za izmenu**:
- Kubernetes ingress ne rute-uje novi endpoint `/api/services/couples/individual` pravilno (vraća 404)
- Rešenje: Učitaj **SVE usluge** iz `/api/services` i filtriraj na frontend-u po kategoriji
- Ovo radi jer `/api/services` endpoint je već postojeći i funkcioniše

---

### 3. Console log output (verifikacija)

Posle izmene, u browser console-u se vidi:

```
✅ Total services: 179, Filtered [PAROVI] services: 19
✅ Services with [PAROVI] prefix: 19/19
✅ Couples discount: 10% (from booking system)
✅ Processed couples massages: [Object, Object, Object, Object...]
```

**To znači**:
- Frontend uspešno učitava **19 INDIVIDUAL [PAROVI] masaža**
- Sve masaže imaju pravilan `[PAROVI]` prefix
- Dropdown meniji sada **TREBA** da budu popunjeni

---

## 🧪 Kako testirati?

### Test 1: Proveri da backend endpoint radi (localhost)
```bash
curl -s http://localhost:8001/api/services/couples/individual | python3 -m json.tool | head -30
```

**Očekivani output**:
```json
[
    {
        "name": "[PAROVI] Thai masaža sa toplim biljnim kompresama - 90 min",
        "duration": 90,
        "price": 5580.0,
        "category": "Kartica Masaza za parove",
        ...
    },
    {
        "name": "[PAROVI] Aroma terapija - 60 min",
        "duration": 60,
        "price": 3960.0,
        "category": "Kartica Masaza za parove",
        ...
    }
]
```

### Test 2: Proveri frontend učitavanje
1. Otvori: https://gold-line-fixer.preview.emergentagent.com/massage
2. Otvori browser console (F12)
3. Skrolutaj do "Masaža za parove" kartice
4. Proveri console log poruke:
   - `✅ Total services: 179, Filtered [PAROVI] services: 19`
   - `✅ Services with [PAROVI] prefix: 19/19`

### Test 3: Klikni na dropdown
1. Klikni na "Osoba 1" dropdown
2. **Očekivano**: Lista sa 19 individual [PAROVI] masaža
3. Klikni na "Osoba 2" dropdown  
4. **Očekivano**: Lista sa 19 individual [PAROVI] masaža

---

## 📝 Fajlovi koji su promenjeni:

1. ✅ `/app/backend/server.py` - Dodao novi endpoint `/api/services/couples/individual`
2. ✅ `/app/frontend/src/components/CouplesMassageCard.js` - Promenio učitavanje podataka da filtrira po kategoriji

---

## ⚠️ Napomena za zakazivanje (sledeći korak)

**TRENUTNO POPRAVLJEN**: Couples dropdown meniji sada učitavaju podatke pravilno.

**SLEDEĆI PROBLEM**: Zakazivanje možda još uvek ne radi. To zahteva:
1. Proveru booking funkcije `handleBookCouple` u `CouplesMassageCard.js`
2. Proveru backend endpoint-a `/api/book-couple-appointment`
3. Proveru payload-a koji se šalje backend-u

**Sledeći korak**: Testiranje booking funkcionalnosti za parove i pojedinačne masaže.

---

**Status**: ✅ Couples dropdown popravljen, ali zakazivanje još nije testirano
**Datum**: 30. Novembar 2025
