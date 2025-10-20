# 🚀 STT Analytics Dashboard - Streamlit Cloud Deployment

## 📋 Pred deploymentom

### 1. Priprav dáta
Dashboard potrebuje tieto Parquet súbory v `data/clean/`:
- `calls.parquet`
- `utterances.parquet`
- `call_metrics.parquet`
- `speaker_metrics.parquet`
- `quality_metrics.parquet`
- `text_statistics.parquet`
- `filler_words.parquet`
- `interaction_metrics.parquet`

**DÔLEŽITÉ:** Streamlit Cloud má limit veľkosti súborov (500 MB). Ak sú tvoje dáta väčšie, musíš použiť cloud storage (AWS S3, Google Cloud Storage, atď.)

### 2. Push na GitHub
```bash
# V projekt root directory
git init
git add .
git commit -m "Initial commit - STT Analytics Dashboard"
git remote add origin https://github.com/Majlo81/STT-dashboard.git
git branch -M main
git push -u origin main
```

---

## 🌐 Streamlit Cloud Deployment

### Krok 1: Prihlás sa na Streamlit Cloud
1. Idi na [share.streamlit.io](https://share.streamlit.io)
2. Prihlás sa s GitHub účtom

### Krok 2: Vytvor novú aplikáciu
1. Klikni **"New app"**
2. Vyber:
   - **Repository:** `Majlo81/STT-dashboard`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
3. Klikni **"Deploy!"**

### Krok 3: Pokročilé nastavenia (voliteľné)
V "Advanced settings":
- **Python version:** 3.10 alebo 3.11
- **Requirements file:** `requirements_streamlit.txt`

---

## 📁 Alternatíva: Dáta v Cloud Storage

Ak sú dáta príliš veľké pre GitHub:

### Option 1: Google Cloud Storage

```python
# V stta/dashboard/app.py upraviť load_data():

import pandas as pd
from google.cloud import storage

def load_data_from_gcs(bucket_name: str, prefix: str):
    """Load data from Google Cloud Storage"""
    # Setup GCS client (vyžaduje credentials)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # Read parquet files
    calls_df = pd.read_parquet(f"gs://{bucket_name}/{prefix}/calls.parquet")
    # ... atď
```

### Option 2: AWS S3

```python
import pandas as pd
import boto3

def load_data_from_s3(bucket_name: str, prefix: str):
    """Load data from AWS S3"""
    # Read directly from S3
    calls_df = pd.read_parquet(f"s3://{bucket_name}/{prefix}/calls.parquet")
    # ... atď
```

### Option 3: Streamlit Secrets (malé dáta)
Pre menšie datasety môžeš použiť Streamlit Secrets:

1. V Streamlit Cloud app settings → Secrets
2. Pridaj URL na dáta:
```toml
[data]
bucket = "your-bucket-name"
prefix = "data/clean"
```

3. V kóde:
```python
import streamlit as st
bucket = st.secrets["data"]["bucket"]
```

---

## 🔧 Riešenie problémov

### ❌ "FileNotFoundError: data/clean/calls.parquet"
**Riešenie:** Dáta nie sú v repo. Použi cloud storage (viď vyššie).

### ❌ "ModuleNotFoundError: No module named 'stta'"
**Riešenie:** Uisti sa že:
1. `streamlit_app.py` je v root directory
2. `stta/` package je v repo
3. `requirements_streamlit.txt` obsahuje všetky dependencies

### ❌ "Repository too large"
**Riešenie:** 
1. Odstráň veľké súbory z repo
2. Použi `.gitignore` pre `data/` folder
3. Použi cloud storage pre dáta

### ❌ "Resource limits exceeded"
**Riešenie:**
- Streamlit Cloud má limit 1GB RAM
- Optimalizuj loading (load len potrebné columns)
- Použij sampling pre veľké datasety

---

## 📊 Demo verzia (bez reálnych dát)

Ak chceš deployovať demo bez reálnych dát:

```python
# Vytvor demo data generator
def generate_demo_data():
    """Generate synthetic demo data"""
    import pandas as pd
    import numpy as np
    
    # Generate 100 demo calls
    calls = pd.DataFrame({
        'call_id': [f'call_{i:04d}' for i in range(100)],
        'call_start_meta': pd.date_range('2024-01-01', periods=100, freq='H')
    })
    
    # ... generate other demo dataframes
    return calls, utterances, ...
```

---

## 🔐 Security Best Practices

1. **Nikdy necommituj:**
   - API keys
   - Passwords
   - Osobné dáta zákazníkov
   - Cloud credentials

2. **Použij Streamlit Secrets pre:**
   - Cloud storage credentials
   - Database connection strings
   - API keys

3. **Privacy:**
   - Anonymizuj citlivé dáta pred upload
   - Použij hashing pre call_ids
   - Odstráň text utterances ak obsahujú osobné info

---

## ✅ Checklist pred deploymentom

- [ ] `streamlit_app.py` v root directory
- [ ] `requirements_streamlit.txt` aktuálny
- [ ] `.streamlit/config.toml` s Coworkers.ai témou
- [ ] `.gitignore` nastavený (exclude `data/`, `.venv/`, `*.pyc`)
- [ ] README.md s popisom projektu
- [ ] Dáta buď:
  - [ ] V repo (ak < 100 MB)
  - [ ] V cloud storage (ak > 100 MB)
  - [ ] Demo data generator
- [ ] GitHub repo je public alebo Streamlit má prístup
- [ ] Testované lokálne: `streamlit run streamlit_app.py`

---

## 🎯 Po úspešnom deployi

Streamlit ti vygeneruje URL ako:
```
https://majlo81-stt-dashboard-streamlit-app-xxxxx.streamlit.app
```

**Zdieľanie:**
- URL je public (ak je repo public)
- Pre private app potrebuješ Streamlit paid plan
- Môžeš pridať password protection v kóde

---

## 📞 Support

Ak máš problémy:
1. Skontroluj Streamlit Cloud logs
2. Testuj lokálne: `streamlit run streamlit_app.py`
3. Skontroluj [Streamlit Community Forum](https://discuss.streamlit.io/)

---

**Powered by Coworkers.ai** 🤖
