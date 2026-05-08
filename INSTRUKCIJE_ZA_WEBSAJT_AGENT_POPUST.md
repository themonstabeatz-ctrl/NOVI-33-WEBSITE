# 📋 DETALJNE INSTRUKCIJE - Popust Za Couple Masažu

## 🎯 ŠTA TREBA URADITI:

Websajt trenutno **NE ŠALJE POPUST** kada korisnik rezerviše couple masažu.

---

## ✅ BRZO REŠENJE (Opcija A):

Pronađite liniju:
```javascript
discount_couples_massage: 0
```

Promenite u:
```javascript
discount_couples_massage: 15.0
```

---

## 🚀 PRAVO REŠENJE (Opcija B - Dinamički):

### Dodajte funkciju za proveru popusta:

```javascript
async function getCoupleDiscountPercentage() {
  try {
    const response = await fetch('https://spabooking.emergent.host/api/services');
    const services = await response.json();
    
    const serviceWithDiscount = services.find(service => {
      const hasCoupleName = service.name && service.name.toLowerCase().includes('parove');
      const hasDiscount = service.discount_percentage > 0;
      return hasCoupleName && hasDiscount;
    });
    
    return serviceWithDiscount ? serviceWithDiscount.discount_percentage : 0;
  } catch (error) {
    return 0;
  }
}
```

### Koristite u booking funkciji:

```javascript
async function bookCoupleAppointment(formData) {
  const activeDiscount = await getCoupleDiscountPercentage();
  
  const bookingData = {
    client_first_name: formData.firstName,
    client_last_name: formData.lastName,
    client_phone: formData.phone,
    client_email: formData.email,
    start_time: formatToISO(formData.date, formData.time),
    duration_type: getDurationType(formData.selectedService),
    person1_services: [formData.person1ServiceId],
    person2_services: [formData.person2ServiceId],
    discount_couples_massage: activeDiscount
  };
  
  const response = await fetch(
    'https://spabooking.emergent.host/api/book-couple-appointment',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(bookingData)
    }
  );
  
  return await response.json();
}
```

---

## 🧪 TESTIRANJE:

1. Otvorite browser console (F12)
2. Napravite rezervaciju za couple masažu
3. Proverite console logs
4. Ulogujte se na: https://spabooking.emergent.host
5. Proverite Dashboard - treba da vidite: 7,480 RSD (sa 15%)

---

## 📊 OČEKIVANE CENE:

| Trajanje | Original | Sa 15% popustom |
|----------|----------|-----------------|
| 2x60 min | 8,800 RSD | 7,480 RSD |
| 2x90 min | 11,200 RSD | 9,520 RSD |
| 2x120 min | 13,600 RSD | 11,560 RSD |

---

## ⚠️ ČESTE GREŠKE:

1. Pogrešan tip: `"15"` umesto `15.0`
2. Ne šalje se: Nedostaje u payload-u
3. Null/undefined vrednost

---

## 📞 DEBUG:

Dodajte console.log:
```javascript
console.log('DISCOUNT:', bookingData.discount_couples_massage);
```

Proverite Network tab (F12):
- Pronađi `book-couple-appointment` request
- Proveri Payload: `discount_couples_massage: 15.0`

---

Za detaljnije instrukcije, pogledajte: BRZO_RESENJE_POPUST.txt
