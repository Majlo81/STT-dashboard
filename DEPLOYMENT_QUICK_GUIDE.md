# 🚀 Quick Deployment Guide - 3 kroky!

## ✅ Čo je pripravené

Dashboard má teraz **inteligentný loading**:
- **Lokálne** (tvoj PC) → používa **reálne dáta** (8,200 calls)
- **Streamlit Cloud** → automaticky vygeneruje **demo dáta** (500 calls)

**Tvoj lokálny dashboard zostáva funkčný s reálnymi dátami!** ✓

---

## 🎯 Deployment v 3 krokoch

### Krok 1: Push na GitHub (5 min)

```bash
# Option A: Použiť helper script (ODPORÚČANÉ)
deploy_to_github.bat

# Option B: Manuálne
git init
git add .
git commit -m "STT Analytics Dashboard with demo data support"
git remote add origin https://github.com/Majlo81/STT-dashboard.git
git branch -M main
git push -u origin main
```

**Poznámky:**
- ✅ `.gitignore` už obsahuje `data/` - reálne dáta sa NEnahrávajú na GitHub
- ✅ Demo data sa vygenerujú automaticky na Streamlit Cloud
- ✅ Všetky potrebné súbory sú pripravené

---

### Krok 2: Streamlit Cloud Setup (3 min)

1. **Idi na:** https://share.streamlit.io
2. **Prihlás sa** s GitHub účtom
3. **Klikni "New app"**
4. **Vyplň:**
   ```
   Repository: Majlo81/STT-dashboard
   Branch: main
   Main file path: streamlit_app.py
   ```
5. **Advanced settings** (voliteľné):
   ```
   Python version: 3.10
   ```
6. **Klikni "Deploy!"**

---

### Krok 3: Počkaj na deployment (5-10 min)

Streamlit Cloud:
1. ⏳ Nainštaluje dependencies (~3 min)
2. ⏳ Spustí aplikáciu (~1 min)
3. ⏳ Vygeneruje demo data (~1 min)
4. ✅ **Dashboard je LIVE!**

Tvoja URL bude:
```
https://majlo81-stt-dashboard-streamlit-app-xxxxx.streamlit.app
```

---

## 🎨 Čo uvidíš na Streamlit Cloud

Dashboard s **DEMO MODE** bannerom:

```
⚠️ DEMO MODE - Using synthetic data for demonstration.
This dashboard is showing 500 generated calls with realistic metrics.
```

**Všetky features fungujú:**
- ✅ Summary view (500 demo calls)
- ✅ Agent Leaderboard
- ✅ Alerts & Issues
- ✅ PDF Export
- ✅ Všetky grafy a metriky
- ✅ Coworkers.ai branding

---

## 📊 Demo vs Real Data

| Feature | Lokálne (tvoj PC) | Streamlit Cloud |
|---------|-------------------|-----------------|
| **Data Source** | Reálne Parquet súbory | Vygenerované demo |
| **Number of Calls** | 8,200 | 500 |
| **Metrics** | Skutočné výpočty | Realistické hodnoty |
| **Individual Calls** | Všetky dostupné | Prvých 10 |
| **Performance** | Full speed | Cloud limits |
| **Banner** | Žiadny | "DEMO MODE" warning |

---

## 🔧 Riešenie problémov

### ❌ "Deploy failed"
**Kontroluj Streamlit logs:**
- Ensure `streamlit_app.py` exists in root
- Check `requirements_streamlit.txt` syntax
- Verify GitHub repo is accessible

### ❌ "Module not found"
**Fix:**
- Ensure `stta/` package je v GitHub repo
- Check import paths v `streamlit_app.py`

### ❌ "Demo data generation failed"
**Fix:**
- Check `stta/dashboard/demo_data.py` exists
- Verify numpy/pandas are in requirements

---

## ✅ Verifikácia úspešného deploymentu

Po deployi skontroluj:
- [ ] Dashboard sa načíta
- [ ] "DEMO MODE" banner je viditeľný
- [ ] Summary view zobrazuje 500 calls
- [ ] Grafy sa renderujú správne
- [ ] Všetky view modes fungujú
- [ ] PDF export funguje
- [ ] Branding Coworkers.ai je viditeľný

---

## 🎯 Zdieľanie

Po úspešnom deployi:
1. **Skopíruj URL** z Streamlit Cloud
2. **Zdieľaj** s tímom/klientmi
3. **Ukáž features:**
   - Agent Leaderboard
   - Smart Alerts
   - PDF Reports
   - Language Analytics

**Dashboard je public** (ak je repo public) - ktokoľvek s URL má prístup.

---

## 🚀 Ďalšie kroky (voliteľné)

### Private Deployment
- Streamlit Teams plan ($250/month)
- Private repos support
- More resources (RAM/CPU)

### Real Data on Cloud
Ak neskôr chceš reálne dáta na cloude:
1. Upload do Google Cloud Storage / AWS S3
2. Upraviť `load_data()` pre cloud loading
3. Použiť Streamlit Secrets pre credentials

---

## 📞 Support

Ak niečo nefunguje:
1. Skontroluj **Streamlit Cloud logs**
2. Testuj **lokálne**: `streamlit run streamlit_app.py`
3. Check **GitHub repo** - všetky súbory uploaded?

---

## 🎉 Hotovo!

**Gratulujem!** Máš teraz:
- ✅ Funkčný lokálny dashboard s **reálnymi dátami**
- ✅ Deployed dashboard s **demo dátami**
- ✅ URL na zdieľanie
- ✅ Professional Coworkers.ai branding

---

**Príkazy na zapamätanie:**

```bash
# Push zmeny na GitHub
git add .
git commit -m "Update"
git push

# Test lokálne (reálne dáta)
streamlit run stta/dashboard/app.py -- --data data/clean

# Test demo dát lokálne
streamlit run stta/dashboard/app.py -- --data nonexistent_folder
```

---

**Made with ❤️ by Coworkers.ai** 🤖
