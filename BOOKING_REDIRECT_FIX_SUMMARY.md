# ✅ REŠENJE: Booking Dugme "Zakažite" - Redirect na Contact Formu

## 🎯 Problem
Klik na dugme "Zakažite" vizuelno reaguje ALI **NE REDIRECTUJE** na Contact formu.

## 🔧 Rešenje - Zamena `<Link>` sa `useNavigate` + `onClick`

---

### 1. `/app/frontend/src/pages/Massage.js` - Single Masaže

#### Import izmena (linija 7):
**STARI KOD**:
```javascript
import { Link } from "react-router-dom";
```

**NOVI KOD**:
```javascript
import { useNavigate } from "react-router-dom";
```

---

#### Dodao `navigate` hook (linija 13-14):
**NOVI KOD**:
```javascript
const Massage = () => {
  const { translate } = useLanguage();
  const navigate = useNavigate();  // ← DODATO!
  const [scrollY, setScrollY] = useState(0);
```

---

#### Dodao `handleBookClick` funkciju (posle linije 308):
**NOVI KOD**:
```javascript
// Handle booking button click - navigate to Contact form
const handleBookClick = (serviceName, durationMinutes) => {
  const serviceWithDuration = `${serviceName} - ${durationMinutes} min`;
  const params = new URLSearchParams({
    service: serviceWithDuration,
  });
  
  console.log('📍 Navigating to /contact with params:', params.toString());
  console.log('📍 Full service name:', serviceWithDuration);
  
  navigate(`/contact?${params.toString()}`);
};
```

---

#### Zamenio dugme (linija 882-886):
**STARI KOD**:
```javascript
<Button asChild className="book-button w-full">
  <Link to={`/contact?service=${encodeURIComponent(`${service.name} - ${durations[service.key]} min`)}`}>
    {translate("bookAppointment")}
  </Link>
</Button>
```

**NOVI KOD**:
```javascript
<Button 
  className="book-button w-full" 
  onClick={() => handleBookClick(service.name, durations[service.key])}
>
  {translate("bookAppointment")}
</Button>
```

---

### 2. `/app/frontend/src/components/CouplesMassageCard.js` - Couples Masaže

#### Import izmena (linija 5):
**STARI KOD**:
```javascript
import { Link } from "react-router-dom";
```

**NOVI KOD**:
```javascript
import { useNavigate } from "react-router-dom";
```

---

#### Dodao `navigate` hook (linija 16):
**NOVI KOD**:
```javascript
const CouplesMassageCard = ({ 
  translate, 
  durations, 
  updateDuration,
  couplesSelections,
  setCouplesSelections,
  dropdownOpen,
  setDropdownOpen
}) => {
  
  const navigate = useNavigate();  // ← DODATO!
  
  const [availableMassages, setAvailableMassages] = React.useState([]);
```

---

#### Dodao `handleBookClick` funkciju (posle linije 411):
**NOVI KOD**:
```javascript
// Handle booking button click - navigate to Contact form with couples data
const handleBookClick = () => {
  const couplesData = {
    duration: durations.sports,
    totalDuration: calculateTotalDuration(),
    person1: {
      massage1: couplesSelections.person1Massage1,
      massage2: couplesSelections.person1Massage2
    },
    person2: {
      massage1: couplesSelections.person2Massage1,
      massage2: couplesSelections.person2Massage2
    },
    totalPrice: calculateCouplesPrice(),
    originalPrice: calculateOriginalPrice(),
    discount: `${couplesDiscount}%`,
    discountPercent: couplesDiscount
  };
  
  const params = new URLSearchParams({
    service: translate('couplesMassage'),
    couplesData: JSON.stringify(couplesData)
  });
  
  console.log('📍 Navigating to /contact for COUPLES with params:', params.toString());
  console.log('📍 Couples data:', couplesData);
  
  navigate(`/contact?${params.toString()}`);
};
```

---

#### Zamenio dugme (linija 921-941):
**STARI KOD**:
```javascript
{isSelectionComplete() ? (
  <Button asChild className="book-button w-full">
    <Link to={`/contact?service=${encodeURIComponent(translate('couplesMassage'))}&couplesData=${encodeURIComponent(JSON.stringify({
      duration: durations.sports,
      totalDuration: calculateTotalDuration(),
      person1: {
        massage1: couplesSelections.person1Massage1,
        massage2: couplesSelections.person1Massage2
      },
      person2: {
        massage1: couplesSelections.person2Massage1,
        massage2: couplesSelections.person2Massage2
      },
      totalPrice: calculateCouplesPrice(),
      originalPrice: calculateOriginalPrice(),
      discount: `${couplesDiscount}%`,
      discountPercent: couplesDiscount
    }))}`}>
      {translate('bookNowBtn')}
    </Link>
  </Button>
) : (
  <Button disabled className="book-button w-full" style={{ opacity: 0.5, cursor: 'not-allowed' }}>
    {translate('bookNowBtn')}
  </Button>
)}
```

**NOVI KOD**:
```javascript
{isSelectionComplete() ? (
  <Button 
    className="book-button w-full" 
    onClick={handleBookClick}
  >
    {translate('bookNowBtn')}
  </Button>
) : (
  <Button disabled className="book-button w-full" style={{ opacity: 0.5, cursor: 'not-allowed' }}>
    {translate('bookNowBtn')}
  </Button>
)}
```

---

### 3. Contact.js - Booking Request Handler

**Fajl**: `/app/frontend/src/pages/Contact.js` (linija 808-836)

**Ovo JE VEĆ ISPRAVNO IMPLEMENTIRANO** - POST request se šalje ka `/api/book-appointment`:

```javascript
const finalEndpoint = `${backendUrl}${bookingEndpoint}`;

console.log('📤 Sending booking request to:', finalEndpoint);
const response = await fetch(finalEndpoint, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(appointmentData)
});

console.log('📥 Response status:', response.status);

if (!response.ok) {
  const errorText = await response.text();
  console.error('❌ Booking API error:', response.status, errorText);
  throw new Error(`Booking failed: ${response.status} - ${errorText}`);
}

const responseData = await response.json();
console.log('✅ Booking successful:', responseData);
```

---

## 🧪 Kako Testirati Nakon Izmene?

### Test 1: Single Masaže
1. **Otvori**: https://wavy-parallax-hero.preview.emergentagent.com/massage
2. **Otvori Chrome DevTools** (F12) → Console tab
3. **Klikni** "Zakažite" na bilo kojoj kartici
4. **Proveri Console log**:
   ```
   📍 Navigating to /contact with params: service=Tradicionalna tajlandska masaža - 60 min
   📍 Full service name: Tradicionalna tajlandska masaža - 60 min
   ```
5. **Očekivano**: Browser se redirectuje na `/contact?service=...`
6. **Popuni formu** i klikni "Zakažite termin"
7. **Proveri Network tab** - trebao bi da vidiš POST request na `/api/book-appointment`

---

### Test 2: Couples Masaže
1. **Skroluj** do "Masaža za parove" kartice
2. **Izaberi** masaže za Osobu 1 i Osobu 2
3. **Klikni** "Zakažite"
4. **Proveri Console log**:
   ```
   📍 Navigating to /contact for COUPLES with params: service=...&couplesData=...
   📍 Couples data: { duration: 90, totalDuration: 180, ... }
   ```
5. **Očekivano**: Redirect na `/contact` sa couples podacima
6. **Popuni formu** i klikni "Zakažite termin"
7. **Proveri Network tab** - POST request na `/api/book-couple-appointment`

---

## ⚠️ VAŽNO: Browser Cache Problem

**PROBLEM**: Posle izmene, browser može keširat stari JavaScript kod sa `Link` komponentom.

**SIMPTOM**: Console prikazuje:
```
PAGE ERROR: Link is not defined
```

**REŠENJE**:
1. **Hard Refresh**: Ctrl + Shift + R (Windows) ili Cmd + Shift + R (Mac)
2. **Clear Cache**: Chrome DevTools → Application → Clear Storage → Clear site data
3. **Incognito Mode**: Otvori stranicu u Incognito/Private browsing mode

---

## 📝 Fajlovi Promenjeni:

1. ✅ `/app/frontend/src/pages/Massage.js` - Dodao useNavigate, handleBookClick, zamenio Link sa Button
2. ✅ `/app/frontend/src/components/CouplesMassageCard.js` - Dodao useNavigate, handleBookClick, zamenio Link sa Button
3. ✅ `/app/backend/.env` - Ispravljen BOOKING_API_URL (ranije)
4. ✅ `/app/frontend/.env` - Ispravljen REACT_APP_BACKEND_URL (ranije)

---

## ✅ Trenutno Stanje:

- ✅ **Cene ispravne** (single i couples, bez decimala)
- ✅ **Couples dropdown** popunjen sa [PAROVI] masažama
- ✅ **Booking redirect** implementiran (potreban hard refresh)
- ⚠️ **Testiranje potrebno**: Nakon hard refresh-a, proveri da li redirect i booking rade

---

**Status**: ✅ Kod popravljen, potreban hard refresh browser-a
**Datum**: 30. Novembar 2025
