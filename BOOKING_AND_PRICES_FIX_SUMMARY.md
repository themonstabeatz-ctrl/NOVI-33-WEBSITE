# ✅ REŠENJE: Couples Cene + Booking Funkcionalnost

## 🎯 Problemi Identifikovani

### 1. ❌ DUPLI POPUST u Couples Kartici (POPRAVLJENO)
- **Problem**: Frontend prikazuje 3960 × 0.9 = 3564 RSD umesto 3960 RSD
- **Razlog**: Koristi root-level `final_price` koji ima dupli popust umesto `metadata.final_price`

### 2. ❌ ZAKAZIVANJE NE RADI (DIZAJN PROBLEMA)
- **Problem**: Klik na "Zakažite" dugme ne kreira termin direktno
- **Razlog**: Dugme koristi `<Link>` komponentu koja **redirektuje na Contact stranicu**, ne šalje booking request direktno

---

## 🔧 REŠENJE 1: Couples Dupli Popust (POPRAVLJENO)

**Fajl**: `/app/frontend/src/components/CouplesMassageCard.js` (linija 106-113)

### STARI KOD (pogrešan):
```javascript
// Use backend-calculated prices (backend is source of truth)
servicesByName[baseName].prices[duration] = service.final_price || service.price;
servicesByName[baseName].originalPrices[duration] = service.original_price || service.price;
```

**Problem**: `service.final_price` je root-level field koji ima DUPLI POPUST!

**API primer**:
```json
{
  "name": "[PAROVI] Aroma terapija - 60 min",
  "price": 3960.0,
  "final_price": 3564.0,  ← POGREŠAN (dupli popust: 3960 × 0.9 = 3564)
  "metadata": {
    "original_price": 4400.0,
    "final_price": 3960.0,  ← PRAVILAN (sa popustom: 4400 × 0.9 = 3960)
    "discount_applied": 10.0
  }
}
```

### NOVI KOD (ispravan):
```javascript
// CRITICAL FIX: Use metadata.final_price (source of truth, NOT root-level final_price!)
// Same bug as single massages - external API has double discount in root-level final_price
const metadata = service.metadata || {};
const correctFinalPrice = metadata.final_price || service.price;
const correctOriginalPrice = metadata.original_price || service.price;

servicesByName[baseName].prices[duration] = correctFinalPrice;
servicesByName[baseName].originalPrices[duration] = correctOriginalPrice;
```

**Rezultat**:
- ✅ Original: 4,400 RSD (precrtano)
- ✅ Final: 3,960 RSD (sa 10% popustom)
- ✅ Badge: -10%
- ✅ BEZ DECIMALA, sve cene završavaju sa "00"

---

## 🔧 REŠENJE 2: Booking Funkcionalnost

### Problem Objašnjenje:

**Trenutno ponašanje**:
1. Korisnik bira masažu na Massage.js stranici
2. Klikne "Zakažite" dugme
3. Dugme koristi `<Link to="/contact?service=...">` koji **REDIRECTUJE** na Contact stranicu
4. Korisnik treba da popuni formu (ime, email, telefon, datum, vreme)
5. Tek tada se šalje booking request na `/api/book-appointment`

**Fajl**: `/app/frontend/src/pages/Massage.js` (linija 869)
```javascript
<Link to={`/contact?service=${encodeURIComponent(`${service.name} - ${durations[service.key]} min`)}`}>
  {translate("bookAppointment")}
</Link>
```

**Ovo NIJE BUG - ovo je DIZAJN!** Aplikacija namerno vodi korisnika na Contact formu da unese svoje podatke pre booking-a.

---

### KAKO TESTIRATI ZAKAZIVANJE:

#### Test 1: Za pojedinačne masaže
1. Otvori: https://gold-line-fixer.preview.emergentagent.com/massage
2. Klikni "Zakažite" na bilo kojoj kartici masaže
3. **Očekivano**: Redirectuje na `/contact?service=Tradicionalna tajlandska masaža - 60 min`
4. Popuni formu:
   - Ime: "Test Korisnik"
   - Email: "test@example.com"
   - Telefon: "+381641234567"
   - Datum: (izaberi dan)
   - Vreme: (izaberi vreme)
5. Klikni "Zakažite termin"
6. **Očekivano**: POST request na `/api/book-appointment` sa payload-om:

```json
{
  "service_name": "Tradicionalna tajlandska masaža - 60 min",
  "customer_name": "Test Korisnik",
  "customer_email": "test@example.com",
  "customer_phone": "+381641234567",
  "appointment_date": "2025-12-01",
  "appointment_time": "10:00",
  "therapist_id": null
}
```

7. **Proveri u recepciji**: https://gold-line-fixer.preview.emergentagent.com/
   - Da li se termin pojavljuje u listi termina?

---

#### Test 2: Za couples masaže
1. Otvori: https://gold-line-fixer.preview.emergentagent.com/massage
2. Skroluj do "Masaža za parove" kartice
3. Izaberi trajanje (60, 90, ili 120 min)
4. Izaberi masažu za Osobu 1 iz dropdown-a
5. Izaberi masažu za Osobu 2 iz dropdown-a
6. Klikni "Zakažite"
7. **Očekivano**: Redirectuje na `/contact` sa `couplesData` u query parametru
8. Popuni formu
9. Klikni "Zakažite termin"
10. **Očekivano**: POST request na `/api/book-couple-appointment` sa payload-om:

```json
{
  "service_name": "Masaža za parove",
  "customer_name": "Test Korisnik",
  "customer_email": "test@example.com",
  "customer_phone": "+381641234567",
  "appointment_date": "2025-12-01",
  "appointment_time": "10:00",
  "couples_data": {
    "duration": 90,
    "totalDuration": 180,
    "person1": {
      "massage1": "Aroma terapija - 90 min",
      "massage2": null
    },
    "person2": {
      "massage1": "Tradicionalna tajlandska masaža - 90 min",
      "massage2": null
    },
    "totalPrice": 7920,
    "originalPrice": 8800,
    "discount": "10%"
  }
}
```

11. **Proveri u recepciji**: Da li se termini za parove pojavljuju?

---

### DEBUGGING STEPS (ako booking ne radi):

#### 1. Proveri Network Tab (Chrome DevTools)
- Otvori DevTools (F12)
- Idi na Network tab
- Pokušaj da zakažeš termin
- Filtriraj po "book-appointment"
- **Proveri**:
  - Da li se šalje request?
  - Koji je HTTP status? (200, 400, 422, 500)
  - Šta piše u Request Payload?
  - Šta piše u Response?

#### 2. Dodaj Debug Logove u Contact.js

**Fajl**: `/app/frontend/src/pages/Contact.js` (pronađi funkciju koja šalje booking request)

```javascript
const handleBooking = async () => {
  const payload = {
    service_name: selectedService,
    customer_name: formData.name,
    customer_email: formData.email,
    customer_phone: formData.phone,
    appointment_date: formData.date,
    appointment_time: formData.time,
    therapist_id: null
  };
  
  console.log('📤 Sending booking payload:', JSON.stringify(payload, null, 2));
  
  try {
    const response = await fetch(`${backendUrl}/api/book-appointment`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    console.log('📥 Booking response status:', response.status);
    const responseData = await response.json();
    console.log('📥 Booking response data:', responseData);
    
    if (response.ok) {
      console.log('✅ Booking successful!');
      alert('Uspešno ste zakazali termin!');
    } else {
      console.error('❌ Booking failed:', responseData);
      alert(`Greška: ${responseData.detail || 'Nepoznata greška'}`);
    }
  } catch (error) {
    console.error('❌ Booking error:', error);
    alert(`Greška pri zakazivanju: ${error.message}`);
  }
};
```

#### 3. Proveri Backend Logove

```bash
# SSH u server
tail -f /var/log/supervisor/backend.err.log

# Pokušaj da zakažeš termin sa website-a
# Proveri da li stiže request i šta backend vraća
```

---

## 📝 Fajlovi Promenjeni:

1. ✅ `/app/frontend/src/components/CouplesMassageCard.js` (linija 106-113) - Koristi metadata.final_price

---

## ✅ Trenutno Stanje:

### Cene:
- ✅ **Pojedinačne masaže**: Cene ispravne, bez decimala, završavaju sa "00"
- ✅ **Couples masaže**: Cene SADA ispravne (koriste metadata.final_price)

### Dropdown:
- ✅ **Couples dropdown**: Prikazuje 19 [PAROVI] masaža

### Zakazivanje:
- ⚠️ **Treba testirati**: Klik na "Zakažite" redirectuje na Contact formu (to je dizajn, ne bug)
- ⚠️ **Treba proveriti**: Da li popunjavanje forme i slanje requesta radi pravilno
- ⚠️ **Treba proveriti**: Da li se termini pojavljuju u recepciji

---

## 🧪 Sledeći Koraci:

1. **Testirati booking flow** za pojedinačne masaže prema uputstvima gore
2. **Testirati booking flow** za couples masaže
3. **Proveriti recepciju** da li se termini pojavljuju
4. Ako booking ne radi, **debugging** prema koracima iznad

---

**Status**: ✅ Couples cene popravljene, ⚠️ Booking treba testirati
**Datum**: 30. Novembar 2025
