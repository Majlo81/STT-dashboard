# STT Analytics Platform

**Phase 1:** Speech-to-Text Data Normalization & Core Metrics Dashboard

A deterministic, mathematically precise analytics platform for call transcript analysis. Built for local execution with no cloud dependencies.

---

## ✨ Features

### 🎯 Core Capabilities
- **Robust CSV Ingestion** – Handles multiple encodings (UTF-8, CP1250), semicolon-delimited format
- **Precise Time Calculations** – Sweep-line algorithm for exact speech/silence/overlap metrics
- **Speaker Analytics** – Raw and apportioned speaking time, turn-taking, interruptions
- **Interactive Dashboard** – Streamlit + Plotly visualizations with drill-down
- **PDF Export** – Professional reports with KPIs, charts, and data tables
- **Quality Metrics** – Validates timestamps, detects inconsistencies, flags anomalies

### 📊 Computed Metrics

**Call-Level:**
- Total duration, speech time, silence time, overlap time
- Utterance count, average length, word count distribution
- Turn-taking speed, interruption counts
- Gap statistics (median, P95, negative gaps)

**Speaker-Level:**
- Raw speaking time (with overlaps)
- Apportioned speaking time (fair overlap distribution)
- Turn count and average duration per turn
- Words per minute (WPM)
- Dialog balance (Gini coefficient)

**Quality:**
- Invalid timestamp ratio
- Unknown speaker ratio
- Empty segment ratio
- Metadata vs. computed timeline delta

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** ([download](https://www.python.org/downloads/))
- **Windows OS** (for oneclick.bat; Linux/Mac: use shell equivalent)

### Installation & Execution

1. **Clone or extract** this repository
2. **Place CSV files** in `data/raw/`
3. **Double-click** `oneclick.bat`

That's it! The script will:
- Create virtual environment
- Install dependencies
- Ingest and clean data
- Compute metrics
- Launch dashboard in browser

---

## 📁 Project Structure

```
windsurf-project/
├── stta/                          # Python package
│   ├── __init__.py
│   ├── cli.py                     # Typer CLI entry point
│   ├── config/                    # Configuration files
│   │   ├── default.yml            # Default settings
│   │   └── speakers.yml           # Speaker label mapping
│   ├── io/                        # Data ingestion
│   │   ├── reader.py              # Robust CSV reader
│   │   └── writer.py              # Parquet writer
│   ├── schemas/                   # Pandera validation schemas
│   │   ├── calls.py
│   │   └── utterances.py
│   ├── metrics/                   # Core metric computations
│   │   ├── timeline.py            # Sweep-line algorithm
│   │   ├── call_level.py
│   │   ├── speaker_level.py
│   │   ├── quality.py
│   │   └── registry.py            # Metric plugin system
│   ├── dashboard/                 # Streamlit UI
│   │   ├── app.py
│   │   └── components.py
│   ├── report/                    # PDF generation
│   │   └── pdf.py
│   └── utils/                     # Utilities
│       ├── timecode.py            # HH:MM:SS.mmm parser
│       ├── text.py
│       ├── logging.py
│       └── validation.py
├── data/
│   ├── raw/                       # Original CSV files (place here)
│   └── clean/                     # Parquet output
│       ├── calls.parquet
│       ├── utterances.parquet
│       └── *_metrics.parquet
├── artifacts/
│   ├── reports/                   # Generated PDF reports
│   ├── charts/                    # Exported chart images
│   └── run.log                    # Structured logs
├── tests/                         # Test suite
│   ├── data/                      # Golden test files
│   └── test_*.py
├── docs/                          # Extended documentation
├── requirements.txt               # Python dependencies
├── oneclick.bat                   # One-click launcher
├── PROGRESS.md                    # Development tracker
├── CHANGELOG.md                   # Version history
└── README.md                      # This file
```

---

## 📖 Usage

### Command-Line Interface

After activating the virtual environment:

```bash
# Ingest CSV files
python -m stta.cli ingest --input data/raw --output data/clean

# Compute metrics
python -m stta.cli compute --data data/clean

# Launch dashboard
streamlit run stta/dashboard/app.py -- --data data/clean

# Export PDF report for specific call
python -m stta.cli export-report --call-id CALL_001 --output artifacts/reports/
```

### Dashboard Features

- **Filters:** Call selection, speaker filter, time range
- **KPI Cards:** Duration, speech/silence ratio, overlap, turn-taking speed
- **Timeline (Gantt):** Visual representation of speaker turns and overlaps
- **Charts:** Speaking time distribution, gaps histogram, quality flags
- **Detail Table:** Sortable, filterable utterance list with download
- **Export:** Generate PDF report for selected call

---

## 🔧 Configuration

### `config/default.yml`

```yaml
paths:
  raw_dir: "data/raw"
  clean_dir: "data/clean"
  artifacts_dir: "artifacts"

parsing:
  delimiter: ";"
  encodings_try: ["utf-8-sig", "cp1250", "latin-1"]
  time_fields: ["start_time", "end_time"]
  text_field: "text"
  speaker_field: "speaker"
  call_id_field: "call_id"

validation:
  require_call_id: true

dashboard:
  default_view: "call"
```

### `config/speakers.yml`

Map raw speaker labels to standardized categories:

```yaml
map:
  "Agent": "AGENT"
  "A": "AGENT"
  "Operátor": "AGENT"
  "Customer": "CUSTOMER"
  "B": "CUSTOMER"
  "Zákazník": "CUSTOMER"
default: "UNKNOWN"
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=stta --cov-report=html

# Run specific test file
pytest tests/test_timeline.py

# Run property-based tests (Hypothesis)
pytest tests/test_sweepline_properties.py
```

### Golden Test Data

Located in `tests/data/`, these are minimal CSV files with known expected outputs for regression testing.

---

## 📐 Mathematical Precision

### Sweep-Line Algorithm

All time-based metrics use a deterministic **sweep-line algorithm** to compute:

- **Union of intervals** (total speech time L)
- **Intersection of intervals** (overlap time O)
- **Apportioned speaking time** (fair distribution: A_k)
- **Silence time** (S = T - L)

**Invariants tested:**
- `L + S = T` (total timeline)
- `O ≤ L` (overlap subset of speech)
- `Σ A_k = L` (apportioned sum equals total)

No approximations. No magic numbers.

---

## 🛠️ Troubleshooting

### "No module named 'stta'"
- Ensure virtual environment is activated: `.venv\Scripts\activate`
- Reinstall: `pip install -r requirements.txt`

### "No CSV files found"
- Place CSV files in `data/raw/`
- Check file extension is `.csv`

### Encoding errors
- Reader tries UTF-8-sig → CP1250 → Latin-1 in order
- Check `artifacts/run.log` for details

### Dashboard won't start
- Check port 8501 is not in use
- Try: `streamlit run stta/dashboard/app.py --server.port 8502`

---

## 🗺️ Roadmap

### Phase 1 (Current)
- ✅ Core data pipeline
- ✅ Precise time metrics
- ✅ Interactive dashboard
- ✅ PDF export

### Phase 2 (Planned)
- Sentiment analysis (local lexicon-based)
- Topic modeling (sklearn LDA/NMF)
- Knowledge graph (entity extraction)
- WER benchmarking (when reference transcripts available)
- API ingestion adapters

---

## 📄 License

Proprietary. Internal use only.

---

## 👥 Contact

For questions or issues, contact the development team.

---

## 📚 Documentation

Extended documentation available in `docs/`:
- Architecture deep-dive
- Metric formulas and derivations
- API integration guide (Phase 2)
- Performance optimization guide

---

**Built with:** Python, Pandas, Pyarrow, Pandera, Streamlit, Plotly, ReportLab  
**Philosophy:** Deterministic, auditable, mathematically precise analytics
