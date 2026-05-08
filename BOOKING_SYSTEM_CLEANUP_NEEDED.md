# 🔧 BOOKING SISTEM - POTREBNO ČIŠĆENJE DUPLIKATA

## 📋 Problem
U booking sistemu postoje **duplirane usluge** za "Masaža za parove". To uzrokuje konfuziju i greške pri booking-u.

---

## 🗑️ SERVISI ZA BRISANJE (Duplikati)

Molim vas da izbrišete sledeće servise iz booking sistema jer su **duplikati**:

### 1. Duplikat 120 min usluga
```
IZBRISATI:
- ID: 431be4cd-ca33-4a38-a72c-65c42eefe99d
  Naziv: "Masaža za parove - 120 min (2x60 min) "
  Razlog: Duplikat - zadržati samo "Masaža za parove - 120 min" sa ID: 3ea2757e-2fa5-4db4-a52e-9db09f573265

- ID: 2da2b983-7e11-4ac2-9af0-e43a13a6b315
  Naziv: "Masaža za parove - 120 min (2x60 min)"
  Razlog: Duplikat
```

### 2. Duplikat 180 min usluga
```
IZBRISATI:
- ID: 5d5c0454-6ccd-4394-97ff-6ac556803ce9
  Naziv: "Masaža za parove - 180 min (2x90 min)"
  Razlog: Duplikat - zadržati samo jedan sa ID: 5a13321f-a9e5-427f-b8ff-beb66e0ec43f

- ID: 751f33aa-434f-4772-97c5-de6e7f80af14
  Naziv: "Masaža za parove - 180 min (2x90 min)"
  Razlog: Duplikat
```

### 3. Duplikat 240 min usluga
```
IZBRISATI:
- ID: ff75a8da-77fc-42a5-a6c3-aff88b95289c
  Naziv: "Masaža za parove - 240 min (2x60 ili 120 min)"
  Razlog: Duplikat - zadržati samo jedan sa ID: 0228f878-a453-46ea-b797-9d66003ccb43
```

---

## ✅ SERVISI ZA ZADRŽATI (Ispravni)

Ovo su **ispravni servisi** koji treba da ostanu:

```
✅ Masaža za parove - 60 min
   ID: 5e593ab1-4f97-4398-979b-528f92c77bf7

✅ Masaža za parove - 90 min
   ID: 8fb44950-8ec6-40a2-90d5-567a00cc7c30

✅ Masaža za parove - 120 min
   ID: 3ea2757e-2fa5-4db4-a52e-9db09f573265

✅ Masaža za parove - 180 min (2x90 min)
   ID: 5a13321f-a9e5-427f-b8ff-beb66e0ec43f

✅ Masaža za parove - 240 min (2x60 ili 120 min)
   ID: 0228f878-a453-46ea-b797-9d66003ccb43
```

---

## 📝 INSTRUKCIJE ZA BRISANJE

### Način 1: Preko Booking Sistema UI
1. Otvori **Booking Sistem → Usluge**
2. Pronađi svaki servis sa navedenim ID-jem
3. Klikni na "Obriši" ili "Delete"
4. Potvrdi brisanje

### Način 2: Preko API-ja (Za Agenta)
```bash
# Brisanje preko API-ja
curl -X DELETE https://gold-line-fixer.preview.emergentagent.com/api/services/{SERVICE_ID}

# Primer za prvi duplikat:
curl -X DELETE https://gold-line-fixer.preview.emergentagent.com/api/services/431be4cd-ca33-4a38-a72c-65c42eefe99d
```

---

## ⚠️ VAŽNO

Nakon brisanja duplikata:
1. **Web sajt će automatski koristiti ispravne ID-jeve** (već ažurirano u Contact.js)
2. **Nema potrebe za dodatnim promenama** na web sajtu
3. Booking za "Masaža za parove - 120 min" će raditi ispravno

---

## 🎯 REZIME

**Ukupno za brisanje:** 5 duplikata
**Zadržati:** 5 ispravnih servisa

Nakon ovog čišćenja, sve "Masaža za parove" rezervacije će raditi bez grešaka!
