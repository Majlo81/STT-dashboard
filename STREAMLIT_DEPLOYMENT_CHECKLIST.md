# ✅ Streamlit Cloud Deployment - Checklist

## Pred Deploymentom

### 1. GitHub Repository
- [ ] Repository vytvorený: `https://github.com/Majlo81/STT-dashboard`
- [ ] Repository je **public** (alebo máš Streamlit Teams plan)
- [ ] Git je nainštalovaný lokálne

### 2. Súbory v Projekte
- [ ] `streamlit_app.py` - entry point (✅ vytvorené)
- [ ] `requirements_streamlit.txt` - dependencies (✅ vytvorené)
- [ ] `.streamlit/config.toml` - theme config (✅ vytvorené)
- [ ] `README.md` - GitHub README (skopíruj z README_GITHUB.md)
- [ ] `.gitignore` - exclude data/, .venv/, *.pyc

### 3. Dáta
**KRITICKÉ:** Streamlit Cloud má limit:
- Max file size: 500 MB
- Max repo size: 1 GB

**Tvoje možnosti:**

#### Option A: Dáta v GitHub (ak < 100 MB)
```bash
# Skontroluj veľkosť
dir data\clean

# Ak je OK, zahrnúť v git:
# Odstráň data/ z .gitignore
# git add data/
# git commit -m "Add data files"
```

#### Option B: Cloud Storage (ODPORÚČANÉ pre veľké dáta)
- [ ] Dáta nahrané do cloud storage (GCS, S3, Azure)
- [ ] Upravený `stta/dashboard/app.py` pre cloud loading
- [ ] Credentials v Streamlit Secrets

#### Option C: Demo Data (na testovanie)
- [ ] Vytvor sample data generator
- [ ] Test s 100-500 calls

---

## Deployment Kroky

### Krok 1: Push na GitHub

```bash
# Spusti helper script
deploy_to_github.bat

# ALEBO manuálne:
git init
git add .
git commit -m "Initial commit - STT Dashboard"
git remote add origin https://github.com/Majlo81/STT-dashboard.git
git branch -M main
git push -u origin main
```

- [ ] Push úspešný
- [ ] Súbory viditeľné na GitHub

### Krok 2: Streamlit Cloud Setup

1. **Idi na:** https://share.streamlit.io
   - [ ] Prihlásený s GitHub účtom

2. **Click "New app"**
   - [ ] Repository: `Majlo81/STT-dashboard`
   - [ ] Branch: `main`
   - [ ] Main file path: `streamlit_app.py`

3. **Advanced settings:**
   - [ ] Python version: `3.10` alebo `3.11`
   - [ ] Requirements file: `requirements_streamlit.txt` (default je requirements.txt)

4. **Click "Deploy!"**
   - [ ] Deployment started

### Krok 3: Monitorovanie Deploymentu

Sleduj build log:
- [ ] Installing dependencies... ✓
- [ ] Running streamlit_app.py... ✓
- [ ] App is live! ✓

**Časové odhady:**
- Dependencies install: 2-5 min
- First load: 1-2 min
- **Total: ~5-10 min**

### Krok 4: Riešenie Chýb

#### ❌ "FileNotFoundError: data/clean/calls.parquet"
```
Problém: Dáta nie sú v repo
Riešenie: Použi cloud storage ALEBO demo data
```

#### ❌ "No module named 'stta'"
```
Problém: Package path issue
Riešenie: Uisti sa že streamlit_app.py je v root
```

#### ❌ "Resource limits exceeded"
```
Problém: Príliš veľa dát pre 1GB RAM limit
Riešenie: 
1. Optimalizuj loading (len potrebné columns)
2. Implementuj data sampling
3. Použi Streamlit Teams (viac RAM)
```

---

## Po Úspešnom Deployi

### Tvoja URL:
```
https://majlo81-stt-dashboard-streamlit-app-xxxxx.streamlit.app
```

### Verifikácia:
- [ ] Dashboard sa načíta
- [ ] Summary view funguje
- [ ] Grafy sa zobrazujú
- [ ] Dáta sú správne

### Zdieľanie:
- [ ] Skopíruj URL
- [ ] Otestuj na inom zariadení
- [ ] Zdieľaj s tímom

---

## Cloud Storage Setup (ak potrebné)

### Google Cloud Storage

1. **Upload dát:**
```bash
gsutil cp -r data/clean gs://your-bucket/stt-data/
```

2. **Upraviť app.py:**
```python
# Na začiatku load_data()
import os
if os.getenv('STREAMLIT_CLOUD'):
    # Cloud mode - load from GCS
    data_dir = "gs://your-bucket/stt-data/"
else:
    # Local mode
    data_dir = Path("data/clean")
```

3. **Streamlit Secrets:**
V Streamlit Cloud → App settings → Secrets:
```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project"
private_key_id = "xxx"
private_key = "xxx"
client_email = "xxx"
```

---

## Testing Checklist

Pred finálnym deploymentom:

### Lokálne testovanie:
```bash
streamlit run streamlit_app.py
```

- [ ] Dashboard sa spustí
- [ ] Všetky views fungujú
- [ ] No errors v konzole
- [ ] Charts sa renderujú

### GitHub check:
- [ ] Všetky súbory uploaded
- [ ] .gitignore funguje (data/ excluded)
- [ ] README.md zobrazuje sa správne

---

## Quick Commands

```bash
# Test lokálne
streamlit run streamlit_app.py

# Check súborov pre git
git status

# Push zmeny
git add .
git commit -m "Update"
git push

# Check repo veľkosť
git count-objects -vH

# Remove large files z history
git filter-branch --tree-filter 'rm -rf data/' HEAD
```

---

## Support Resources

- **Streamlit Docs:** https://docs.streamlit.io/deploy/streamlit-community-cloud
- **Community Forum:** https://discuss.streamlit.io/
- **GitHub Issues:** https://github.com/Majlo81/STT-dashboard/issues

---

## Notes

**Dôležité:**
- First deployment trvá 5-10 min
- Re-deploy je rýchlejší (~2 min)
- Streamlit Cloud auto-redeploy pri git push
- Logs sú dostupné v Streamlit Cloud dashboard

**Limitations (Free Tier):**
- 1GB RAM
- 1 CPU
- Public apps only
- 3 apps limit

**Ak potrebuješ viac:**
- Streamlit Teams: $250/month
- Private apps, more resources, custom domains

---

✅ **Po dokončení checklist môžeš deployovať!**
