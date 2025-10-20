# Quick Start Guide

## 🚀 5-Minute Setup

### 1. Prerequisites

- **Python 3.10+** installed
- **Windows** OS (for oneclick.bat)

### 2. Prepare Data

Place your CSV files in `data/raw/`:

```
windsurf-project/
  data/
    raw/
      call_001.csv
      call_002.csv
      ...
```

### 3. Run One-Click Launcher

```cmd
oneclick.bat
```

This will:
1. Create virtual environment
2. Install dependencies
3. Process CSV files
4. Launch dashboard in browser

### 4. Access Dashboard

Dashboard opens automatically at: `http://localhost:8501`

---

## 📊 Using the Dashboard

### Navigation

- **Sidebar**: Select call, filter speakers, adjust time range
- **Overview Tab**: KPIs, narrative summary, charts
- **Timeline Tab**: Gantt chart, gap distribution
- **Speakers Tab**: Per-speaker metrics, WPM comparison
- **Quality Tab**: Data validation metrics
- **Details Tab**: Full utterance table, CSV download

### Key Features

**KPI Cards**: Quick metrics overview  
**Timeline Gantt**: Visual speaker turns  
**Interactive Filters**: Dynamic data exploration  
**PDF Export**: Generate reports (coming in Sprint 2)

---

## 🔧 Manual Usage

### Step-by-Step Commands

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Ingest CSV files
python -m stta.cli ingest --input data/raw --output data/clean

# 4. Compute metrics
python -m stta.cli compute --data data/clean

# 5. Launch dashboard
streamlit run stta/dashboard/app.py -- --data data/clean
```

---

## 📝 CSV Format Requirements

### Expected Structure

**First Row (Metadata):**
```
call_id;direction;agent_id;call_duration;speaker;start_time;end_time;text
CALL_001;INBOUND;AG123;120.5;;;;;;
```

**Subsequent Rows (Utterances):**
```
;;;;;;Agent;0.0;3.5;Dobrý den...
;;;;;;Customer;4.0;8.2;Dobrý den...
```

### Required Fields

- `call_id`: Unique call identifier
- `speaker`: Speaker label (mapped via speakers.yml)
- `start_time`: Utterance start (supports HH:MM:SS.mmm)
- `end_time`: Utterance end
- `text`: Transcribed text

### Supported Formats

**Delimiter:** Semicolon (`;`)  
**Encoding:** UTF-8, CP1250, Latin-1 (auto-detected)  
**Time formats:** `SS`, `MM:SS`, `HH:MM:SS`, with optional `.mmm`

---

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage report
pytest --cov=stta --cov-report=html

# View coverage
start htmlcov/index.html
```

---

## ❓ Troubleshooting

### "No CSV files found"
→ Place CSV files in `data/raw/` directory

### Encoding errors
→ Check `artifacts/run.log` for details  
→ Supported: UTF-8-sig, CP1250, Latin-1

### Dashboard won't start
→ Check port 8501 is not in use  
→ Try: `streamlit run stta/dashboard/app.py --server.port 8502`

### Import errors
→ Ensure virtual environment is activated  
→ Reinstall: `pip install -r requirements.txt`

---

## 📚 Next Steps

1. **Explore Metrics**: Review `docs/METRICS_REFERENCE.md`
2. **Understand Architecture**: Read `docs/ARCHITECTURE.md`
3. **Customize Config**: Edit `config/default.yml` and `config/speakers.yml`
4. **Run Tests**: Execute `pytest` to verify setup

---

## 🎯 Phase 1 Features

✅ Robust CSV ingestion  
✅ Precise timeline calculations (sweep-line)  
✅ Call-level metrics  
✅ Speaker-level analytics  
✅ Quality validation  
✅ Interactive dashboard  
✅ Test suite  

🔜 Phase 2: AI features (sentiment, topics)  
🔜 Phase 3: Real-time processing, API
