# 🔧 Fix pre Streamlit Cloud Deployment Error

## Problém

```
error: command 'cmake' failed: No such file or directory
Failed building wheel for pyarrow
```

## Príčina

Streamlit Cloud automaticky použil **Python 3.13**, ale `pyarrow 16.x` nemá pre-built wheel pre Python 3.13 a pokúšal sa ho kompilovať (bez úspechu).

## ✅ Riešenie (HOTFIX)

Spravil som **2 zmeny**:

### 1. Upgrade pyarrow verzie
**Súbor:** `requirements_streamlit.txt`
```diff
- pyarrow>=16.0.0,<17.0.0
+ pyarrow>=17.0.0,<19.0.0
```

PyArrow 17+ má podporu pre Python 3.13.

### 2. Lock Python version na 3.11
**Nový súbor:** `.python-version`
```
3.11
```

Streamlit Cloud tento súbor rešpektuje a použije Python 3.11 (stabilnejší).

---

## 🚀 Ako pokračovať

### Krok 1: Push zmeny na GitHub

```bash
git add .
git commit -m "Fix: Update pyarrow for Python 3.13 compatibility"
git push
```

### Krok 2: Streamlit Cloud auto-redeploy

Streamlit Cloud automaticky detekuje push a znovu deployne aplikáciu.

**ALEBO** klikni v Streamlit Cloud dashboarde:
- Reboot app
- Clear cache & Reboot

### Krok 3: Sleduj logs

Deployment by mal teraz prejsť:
```
✓ Installing dependencies... (pyarrow 17.x pre Python 3.11)
✓ Running streamlit_app.py...
✓ App is live!
```

---

## 📊 Overenie

Po úspešnom deployi:
1. Dashboard sa načíta s "DEMO MODE" bannerom
2. 500 demo calls zobrazených
3. Všetky features fungujú

---

## 🔍 Ak ešte stále nefunguje

### Check 1: Streamlit Cloud nastavenia
V "Advanced settings" app:
- Python version: **3.11** (alebo automaticky z `.python-version`)
- Requirements file: `requirements_streamlit.txt`

### Check 2: Manuálny fix pre dependencies

Ak ešte stále problém s pyarrow, pridaj do Streamlit Cloud "Advanced settings":

**Packages:**
```
pyarrow==18.0.0
```

### Check 3: Fallback na menší pyarrow

Ak nič nepomáha, zmeň v `requirements_streamlit.txt`:
```
pyarrow>=14.0.0,<15.0.0
```

PyArrow 14.x má najlepšiu kompatibilitu s rôznymi Python verziami.

---

## 💡 Vysvetlenie

**Prečo to zlyhalo:**
- Streamlit Cloud defaultne použil Python 3.13.8
- PyArrow 16.x nemá binary wheel pre Python 3.13
- Pokúsil sa kompilovať zo source
- Zlyhalo (chýba cmake build tool)

**Prečo fix funguje:**
- PyArrow 17+ má wheels pre Python 3.13
- `.python-version` vynúti Python 3.11 (má wheels pre všetky verzie)
- Dvojitá ochrana = deployment prejde

---

## 📁 Zmenené súbory

```
✅ requirements_streamlit.txt - Updated pyarrow to >=17.0.0
✅ .python-version - NEW file, forces Python 3.11
```

---

## 🎯 Next Steps po úspešnom deployi

1. **Testuj dashboard** - všetky features by mali fungovať s demo dátami
2. **Zdieľaj URL** - dashboard je verejný
3. **Voliteľne:** Neskôr môžeš nahrať reálne dáta do cloud storage

---

**Deployment by teraz mal prejsť bez problémov!** 🚀

Ak máš akékoľvek otázky, daj vedieť.
