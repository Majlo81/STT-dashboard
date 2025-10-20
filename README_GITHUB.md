# 🤖 STT Analytics Platform

**Advanced Speech-to-Text Analytics & Call Intelligence**  
*Powered by [Coworkers.ai](https://www.coworkers.ai/)*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

---

## 📊 Overview

STT Analytics Platform je pokročilý analytický nástroj pre analýzu call center konverzácií. Dashboard poskytuje komplexné metriky pre hodnotenie kvality hovorov, výkonu agentov a customer experience.

### ✨ Key Features

- **📈 Comprehensive Metrics** - 74+ metrík vrátane quality, language, a interaction patterns
- **🏆 Agent Leaderboard** - Performance ranking s composite scoring
- **🚨 Smart Alerts** - Automatická detekcia quality issues a anomálií
- **📄 PDF Reports** - Branded export reportov pre prezentácie
- **💬 Language Analytics** - Vocabulary richness, filler words detection
- **🔄 Interaction Patterns** - Turn-taking balance, interruption rates
- **🎨 Coworkers.ai Branding** - Professional UI s corporate colors

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Parquet data files (calls, utterances, metrics)

### Local Installation

```bash
# Clone repository
git clone https://github.com/Majlo81/STT-dashboard.git
cd STT-dashboard

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements_streamlit.txt

# Run dashboard
streamlit run streamlit_app.py
```

### Streamlit Cloud Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

---

## 📊 Dashboard Views

### 1. **Summary (All Calls)**
- Aggregated KPIs across all calls
- Trend analysis over time
- Distribution charts
- Language & interaction analytics

### 2. **Individual Call**
- Detailed call analysis
- Timeline Gantt chart
- Speaker metrics breakdown
- Quality indicators

### 3. **Agent Leaderboard** 
- Performance ranking (0-100 score)
- Top/bottom performers
- Team KPIs
- Training identification

### 4. **Alerts & Issues**
- Automated quality monitoring
- Critical call detection
- Alert severity levels
- Category-based filtering

### 5. **Export Report**
- Branded PDF generation
- Customizable sections
- One-click download
- Executive summaries

---

## 📈 Metrics Overview

### Call-Level Metrics (12)
- Duration, speech time, silence, overlaps
- Utterance counts, speaker switches
- Quality scores

### Speaker Metrics (14)
- Speaking time distribution
- Words per minute
- Turn counts
- Dialog balance (Gini coefficient)

### Text Analysis (12)
- Vocabulary richness
- Question/exclamation counts
- Sentence statistics
- Per-speaker analysis

### Filler Words (4)
- Czech filler detection (ehm, jako, prostě...)
- Overall & per-speaker rates
- Training indicators

### Interaction Patterns (14)
- Interruption rates
- Long pauses (>3s)
- Response delays
- Turn-taking balance
- Monologue detection

### Quality Metrics (18)
- Invalid timestamps
- Unknown speakers
- Empty text detection
- Composite quality score

**Total: 74 metrics!**

---

## 🏗️ Architecture

```
stta/
├── io/              # Data reading/writing (Parquet)
├── schemas/         # Pandera validation schemas
├── metrics/         # Metric calculation modules
│   ├── call_level.py
│   ├── speaker_level.py
│   ├── quality.py
│   ├── text_analysis.py
│   ├── interaction_patterns.py
│   └── registry.py
├── timeline/        # Timeline computation
├── dashboard/       # Streamlit dashboard
│   ├── app.py
│   ├── components.py
│   ├── leaderboard.py
│   ├── alerts.py
│   └── pdf_export.py
└── cli.py          # Command-line interface
```

---

## 🎨 Coworkers.ai Branding

### Color Palette
- **Cyan**: `#7DD3D3` - Primary
- **Magenta**: `#E6458B` - Accent
- **Navy**: `#1A2B3C` - Text
- **Gradients** - Backgrounds

All visualizations, UI elements, and PDF reports use consistent Coworkers.ai branding.

---

## 📊 Data Requirements

### Input Format
Dashboard expects Parquet files in `data/clean/`:

```
data/clean/
├── calls.parquet              # Call metadata
├── utterances.parquet         # Transcribed utterances
├── call_metrics.parquet       # Computed call metrics
├── speaker_metrics.parquet    # Computed speaker metrics
├── quality_metrics.parquet    # Quality indicators
├── text_statistics.parquet    # Text analysis
├── filler_words.parquet       # Filler word detection
└── interaction_metrics.parquet # Interaction patterns
```

### Data Generation

```bash
# Generate metrics from raw CSV
python -m stta.cli parse input.csv --output data/clean
python -m stta.cli compute --data data/clean
```

---

## 🔧 Configuration

### Streamlit Config
`.streamlit/config.toml` - Theme and server settings

### Alert Thresholds
Customize in `stta/dashboard/alerts.py`:
```python
thresholds = {
    'quality_score_min': 0.8,
    'filler_rate_max': 0.05,
    'agent_response_delay_max': 3.0,
    # ... etc
}
```

---

## 📚 Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) - Streamlit Cloud deployment guide
- [PROGRESS.md](PROGRESS.md) - Development progress log
- [METRICS_ROADMAP.md](METRICS_ROADMAP.md) - Future metrics roadmap

---

## 🧪 Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=stta tests/

# Verify metrics calculations
python verify_metrics.py
```

---

## 🤝 Contributing

This is a private/commercial project by Coworkers.ai.  
For questions or support, contact the development team.

---

## 📄 License

Proprietary - © 2025 Coworkers.ai

---

## 🎯 Use Cases

### Call Centre Management
- Daily quality monitoring
- Weekly performance reports
- Agent coaching identification

### Quality Assurance
- Spot checks with alerts
- Compliance monitoring
- Trend analysis

### Training & Development
- Performance benchmarking
- Best practice identification
- Improvement tracking

---

## 📞 Support

For technical support or feature requests:
- Email: support@coworkers.ai
- Web: https://www.coworkers.ai/

---

**Made with ❤️ by Coworkers.ai team**

🤖 *Transforming customer communication with AI*
