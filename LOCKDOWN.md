# 🔒 LOCKDOWN DOKUMENTACIJA

## Status: AKTIVAN
**Datum aktivacije:** 2025-12-16
**Token:** BL_LOCK_2025_12_16

---

## ⛔ NE DIRAJ (ZABRANJENI FAJLOVI)

- `frontend/src/components/CouplesMassageCard.js`
- `frontend/src/pages/Massage.js`
- `frontend/src/pages/Contact.js` (booking submit, payload, pricing, discount)
- `frontend/src/components/BackendHealthCheck.js` (backend URL logika)

### Zabranjena logika:
- [PAROVI] prefiks
- duration validacija
- discounts/popusti
- price-lock
- service_code
- couples booking flow

---

## ✅ DOZVOLJENO

- SPA stranice/prikaz (UI)
- Tekstovi, slike
- Bilo šta van `/massage` i van couples booking flow

---

## 📌 PRAVILO ZA IZMENE

Izmene zabranjenih fajlova su moguće SAMO uz eksplicitno odobrenje:

```
APPROVED: [opis izmene]
```

Bez ovog odobrenja, NIKAKVE izmene nisu dozvoljene.

---

## 🔄 SAVE&FORK PROTOKOL

1. NE MENJAJ masaže
2. Ako se promeni preview domen → javi NOVI link
3. Ne radi CORS samostalno → samo prijavi
