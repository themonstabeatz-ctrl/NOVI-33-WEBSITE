# 🔒 STABLE CODE PROTECTION DOCUMENT
## Bua Luang Thai Spa - Frontend Stability Guidelines

**Created**: 30. Novembar 2025  
**Snapshot**: BuaLuang-FRONTEND-STABLE-01  
**Git Commit**: f69cc31

---

## 📸 BACKUP/SNAPSHOT Information

### How to Restore This Snapshot:
```bash
cd /app
git checkout f69cc31
sudo supervisorctl restart frontend
```

### What This Snapshot Includes:
✅ Working price display (original + discount, NO DECIMALS)  
✅ Working couples massage dropdowns (Osoba 1 / Osoba 2)  
✅ Working booking redirect (Massage → Contact)  
✅ Working form submission with correct backend URL  
✅ Verified backend integration  

---

## 🚫 PROTECTED FILES - DO NOT MODIFY WITHOUT EXPLICIT PERMISSION

### 1. `/app/frontend/src/pages/Massage.js`
**Protected Sections**:
- **Line ~66**: `apiServices` state declaration (dynamic data fetching)
- **Line ~314**: `handleBookClick` function (booking button click handler)
- **Line ~818**: Price display JSX (original price strikethrough + final price)

**Why Protected**: Price display logic is verified and working correctly. Uses `metadata.final_price` to avoid double discount bug.

**Comments Added**: 
```javascript
// 🔒 DO NOT MODIFY — STABLE VERIFIED LOGIC (Bua Luang - SNAPSHOT: BuaLuang-FRONTEND-STABLE-01)
```

---

### 2. `/app/frontend/src/components/CouplesMassageCard.js`
**Protected Sections**:
- **Line ~7**: Component declaration and props
- **Line ~107**: Price calculation logic using `metadata.final_price`
- **Line ~414**: `handleBookClick` function for couples booking

**Why Protected**: Couples massage price calculation and dropdown logic is verified. Uses correct metadata to avoid double discount.

**Comments Added**: 
```javascript
// 🔒 DO NOT MODIFY — STABLE VERIFIED LOGIC (Bua Luang - SNAPSHOT: BuaLuang-FRONTEND-STABLE-01)
```

---

### 3. `/app/frontend/src/pages/Contact.js`
**Protected Sections**:
- **Line ~322**: `handleSubmit` function (entire function body)
- Payload formation logic
- POST request to `/api/book-appointment`
- Error handling and success message display

**Why Protected**: Booking submission logic is verified and working. Communicates correctly with backend proxy.

**Comments Added**: 
```javascript
// 🔒 DO NOT MODIFY — STABLE VERIFIED BOOKING LOGIC (Bua Luang - SNAPSHOT: BuaLuang-FRONTEND-STABLE-01)
// This handleSubmit function works correctly with backend /api/book-appointment
```

---

### 4. `/app/frontend/.env`
**Protected Configuration**:
```bash
# 🔒 DO NOT MODIFY — STABLE VERIFIED CONFIGURATION
REACT_APP_BACKEND_URL=https://wavy-parallax-hero.preview.emergentagent.com
```

**Why Protected**: This URL is the CORRECT backend proxy server. Changing it will break all API communication.

**DO NOT CHANGE TO**: `https://wavy-parallax-hero.preview.emergentagent.com` (that's the admin dashboard, not public API)

---

## ✅ VERIFIED WORKING FEATURES (DO NOT BREAK THESE)

1. **Price Display**:
   - All prices end with ",00" (NO DECIMALS)
   - Original price (strikethrough) shown when there's discount
   - Final price (red, bold) uses `metadata.final_price` from API
   - NO frontend calculations - backend is source of truth

2. **Couples Massage**:
   - Dropdown meniji populated with 19 [PAROVI] massage options
   - Price calculation uses `metadata.final_price` (NOT root-level)
   - Discount badge shows correct percentage
   - "Zakažite" button navigates to Contact with couples data

3. **Booking Flow**:
   - Click "Zakažite" on any massage card → redirects to `/contact?service=...`
   - Contact form receives service parameter
   - Form validation works (checks for required fields)
   - `handleSubmit` sends POST to `/api/book-appointment` on correct backend

4. **Backend Integration**:
   - Frontend → Backend Proxy (`fixprice-bug.preview.emergentagent.com`)
   - Backend Proxy → Recepcija (`therapist-scheduler.preview.emergentagent.com`)
   - NO 404 errors on booking endpoints
   - Correct payload structure sent to backend

---

## 🔄 WORKFLOW FOR FUTURE CHANGES

### Before Making ANY Changes to Protected Files:

1. **Create a new Git branch**:
   ```bash
   cd /app
   git checkout -b feature/your-feature-name
   ```

2. **Make changes on the branch** (NOT on main)

3. **Test thoroughly**:
   - Check price display still works
   - Check booking flow still works
   - Check for console errors
   - Test on actual website

4. **Get explicit approval** from user before merging

5. **If approved**, merge to main:
   ```bash
   git checkout main
   git merge feature/your-feature-name
   ```

6. **If NOT approved**, discard changes:
   ```bash
   git checkout main
   git branch -D feature/your-feature-name
   ```

---

## 📋 CHECKLIST: How to Verify Stability After Any Change

Run these tests to ensure nothing broke:

- [ ] Navigate to `/massage` - all cards load with correct prices
- [ ] Check prices end with ",00" (no decimals)
- [ ] Click "Zakažite" on regular massage - redirects to `/contact`
- [ ] Scroll to "Masaža za parove" - dropdowns populate with massages
- [ ] Select Osoba 1 and Osoba 2 - button becomes enabled
- [ ] Click "Zakažite" for couples - redirects to `/contact` with couples data
- [ ] On Contact page - fill form and click submit
- [ ] Check console - POST goes to `fixprice-bug.preview.emergentagent.com/api/book-appointment`
- [ ] NO "Link is not defined" errors in console
- [ ] NO "response.clone()" errors in console
- [ ] NO 404 errors to wrong backend

If ANY of these checks fail → **IMMEDIATELY REVERT**:
```bash
git checkout f69cc31
sudo supervisorctl restart frontend
```

---

## 🆘 EMERGENCY ROLLBACK PROCEDURE

If something breaks after a change:

```bash
# 1. Stop frontend
sudo supervisorctl stop frontend

# 2. Restore stable snapshot
cd /app
git reset --hard f69cc31

# 3. Restart frontend
sudo supervisorctl start frontend

# 4. Verify it's working
curl -s https://wavy-parallax-hero.preview.emergentagent.com/ | grep -q "Bua Luang" && echo "✅ Website is up"
```

---

## 📞 CONTACT FOR PERMISSIONS

**DO NOT modify protected sections without explicit written permission from user.**

If you need to make changes to protected code:
1. Explain WHY the change is necessary
2. Show WHAT you plan to change (code diff)
3. Explain HOW you'll test it
4. Wait for explicit approval
5. Only then proceed with changes

---

**Remember**: It's better to ask for permission and be safe, than to break working features and need emergency rollback! 🔒
