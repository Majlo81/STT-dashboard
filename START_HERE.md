# 🎉 STT Analytics Platform - START HERE

## Welcome!

This is a **complete, production-ready** Speech-to-Text analytics platform built according to your detailed specification.

---

## ⚡ Quick Start (3 Steps)

### 1️⃣ Add Your Data

Place your CSV files here:
```
data/raw/
  ├── call_001.csv
  ├── call_002.csv
  └── ...
```

### 2️⃣ Run One-Click Launcher

```cmd
oneclick.bat
```

That's it! The dashboard will open in your browser automatically.

### 3️⃣ Explore

Navigate through 5 tabs:
- **Overview** - KPIs and summary
- **Timeline** - Gantt chart of speaker turns
- **Speakers** - Per-speaker analytics
- **Quality** - Data validation
- **Details** - Full utterance table

---

## 📚 Documentation Map

### New Users
1. **README.md** - Complete project overview
2. **QUICKSTART.md** - Detailed 5-minute setup
3. **PROJECT_STATUS.md** - What's been built

### Developers
1. **docs/ARCHITECTURE.md** - System design
2. **docs/METRICS_REFERENCE.md** - All formulas
3. **IMPLEMENTATION_SUMMARY.md** - Technical details

### Reference
- **PROJECT_TREE.txt** - File structure
- **CHANGELOG.md** - Version history
- **TESTING.md** - Test procedures

---

## ✅ What's Included

### Core Features
✅ **Robust CSV Ingestion**
- Multi-encoding support (UTF-8, CP1250, Latin-1)
- Automatic speaker normalization
- Time format parsing (HH:MM:SS.mmm)

✅ **Precise Metrics** (40+)
- Sweep-line algorithm (exact calculations)
- Call-level: duration, speech, silence, overlap
- Speaker-level: turns, WPM, dialog balance
- Quality: validation and health checks

✅ **Interactive Dashboard**
- 5 specialized tabs
- Real-time filtering
- Visual storytelling
- Export to CSV/PDF

✅ **One-Click Deployment**
- Auto-install dependencies
- No manual configuration
- Browser auto-launch

### Technical Excellence
✅ Mathematical precision (no approximations)
✅ Deterministic processing (reproducible)
✅ Extensible architecture (plugin metrics)
✅ Comprehensive tests
✅ Full documentation

---

## 🎯 Key Files

| File | Purpose |
|------|---------|
| `oneclick.bat` | **Launch everything** |
| `README.md` | Main documentation |
| `config/speakers.yml` | Speaker label mapping |
| `config/default.yml` | Global settings |

---

## 📊 Sample Output

After running `oneclick.bat`, you'll get:

**Clean Data** (`data/clean/`)
- `calls.parquet` - Call metadata
- `utterances.parquet` - All utterances
- `call_metrics.parquet` - 17 metrics per call
- `speaker_metrics.parquet` - 10 metrics per speaker
- `quality_metrics.parquet` - 14 quality metrics

**Dashboard** (browser)
- Interactive visualizations
- Filterable by call, speaker, time
- Export capabilities

**Logs** (`artifacts/run.log`)
- Structured execution logs
- Error tracking

---

## 🔧 Commands

```bash
# Full pipeline (recommended)
oneclick.bat

# Individual steps
python -m stta.cli ingest --input data/raw --output data/clean
python -m stta.cli compute --data data/clean
streamlit run stta/dashboard/app.py -- --data data/clean

# Testing
pytest
pytest --cov=stta --cov-report=html

# Help
python -m stta.cli --help
```

---

## 💡 Tips

### CSV Format
- **Delimiter:** Semicolon (`;`)
- **First row:** Call metadata
- **Other rows:** Utterances
- **Required fields:** call_id, speaker, start_time, end_time, text

### Speaker Mapping
Edit `config/speakers.yml`:
```yaml
map:
  "Agent": "AGENT"
  "Zákazník": "CUSTOMER"
default: "UNKNOWN"
```

### Troubleshooting
- Check `artifacts/run.log` for errors
- See `QUICKSTART.md` for common issues
- Test data: Use `tests/data/sample_call.csv`

---

## 📈 What's Next

### Immediate
1. ✅ Core implementation complete
2. ⏳ Test with your real data
3. 🔜 Report any bugs

### Coming Soon (Phase 2)
- Sentiment analysis (local, no APIs)
- Topic modeling (LDA/NMF)
- Knowledge graph
- WER benchmarking

---

## 🏆 Highlights

### Mathematical Rigor
- **Sweep-line algorithm** for exact time calculations
- **Invariants validated**: L+S=T, O≤L, ΣA_k=L
- **No approximations** or magic numbers

### Production Quality
- **40+ metrics** across 3 categories
- **Comprehensive tests** with invariant checks
- **Error handling** with detailed logging
- **Schema validation** with Pandera

### User Experience
- **One-click setup** - zero configuration
- **Interactive dashboard** - 5 specialized tabs
- **Visual storytelling** - automated narratives
- **Export ready** - CSV and PDF

---

## 📞 Support

- **Documentation:** See `README.md` and `docs/`
- **Tests:** Run `pytest` to verify setup
- **Logs:** Check `artifacts/run.log`

---

## 🎯 Success Criteria

✅ All Phase 1 features implemented  
✅ Mathematical precision maintained  
✅ Extensible architecture  
✅ Fully documented  
✅ Ready for production testing  

**Status:** Phase 1 **COMPLETE** ✅

---

**Now run `oneclick.bat` and see it in action!** 🚀

---

Built with: Python, Pandas, Streamlit, Plotly, ReportLab  
Philosophy: Deterministic, auditable, mathematically precise
