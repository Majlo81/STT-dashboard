# STT Analytics Platform - Architecture

## Overview

This document describes the technical architecture of the STT Analytics Platform Phase 1.

## Design Principles

1. **Deterministic Processing** - All computations are reproducible and auditable
2. **Mathematical Precision** - No approximations in time calculations
3. **Local Execution** - No external API dependencies or cloud services
4. **Data Validation** - Strict schema enforcement with Pandera
5. **Extensibility** - Plugin-based metric registry for future enhancements

---

## System Architecture

```
┌─────────────────┐
│   CSV Files     │
│  (data/raw/)    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  CSV Reader     │
│  - Encoding     │
│  - Validation   │
│  - Normalization│
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Pandera Schema  │
│   Validation    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Parquet Storage │
│ (data/clean/)   │
│ - calls.parquet │
│ - utterances... │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Metric Registry │
│ - Timeline      │
│ - Call-level    │
│ - Speaker-level │
│ - Quality       │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Visualization   │
│ - Streamlit     │
│ - Plotly        │
│ - PDF Export    │
└─────────────────┘
```

---

## Module Breakdown

### `stta.io` - Data Ingestion

**Purpose:** Robust CSV reading with encoding detection

**Key Components:**
- `CSVReader` - Multi-encoding CSV parser
- `load_speaker_mapping()` - YAML config loader
- `write_parquet()` / `read_parquet()` - Parquet I/O

**Design Decisions:**
- Try encodings in deterministic order (UTF-8-sig → CP1250 → Latin-1)
- Never guess or auto-correct data
- Flag invalid data, don't drop it

### `stta.schemas` - Data Validation

**Purpose:** Enforce data contracts with Pandera

**Key Components:**
- `CallsSchema` - Schema for calls.parquet
- `UtterancesSchema` - Schema for utterances.parquet

**Design Decisions:**
- Use Pandera for DataFrame-level validation
- Allow nullable fields for optional metadata
- Validate ranges (e.g., times ≥ 0)

### `stta.metrics` - Metric Computation

**Purpose:** Precise calculation of call analytics

#### `timeline.py` - Sweep-Line Algorithm

**Algorithm:** Event-based interval processing

```python
events = [(start, +1, speaker), (end, -1, speaker), ...]
events.sort()

for each segment [t_i, t_{i+1}):
    count active speakers
    accumulate speech time (L)
    accumulate overlap time (O) if count ≥ 2
    distribute time fairly (apportioned)
```

**Guarantees:**
- `L + S = T` (speech + silence = total)
- `O ≤ L` (overlap ⊆ speech)
- `Σ A_k = L` (apportioned sum = speech)

#### `call_level.py` - Call Metrics

Computes:
- Duration, speech, silence, overlap
- Utterance statistics (avg, median, p95)
- Gaps between utterances
- Speaker switches
- Interruptions

#### `speaker_level.py` - Speaker Metrics

Computes:
- Raw speaking time (with overlaps counted)
- Apportioned speaking time (fair distribution)
- Turn count and duration
- Words per minute
- Gini coefficient (dialog balance)

#### `quality.py` - Quality Metrics

Computes:
- Invalid timestamp ratio
- Unknown speaker ratio
- Empty text ratio
- Metadata vs computed delta
- Overall quality score

#### `registry.py` - Metric Registry

Plugin system for extensibility:
```python
registry.register(
    name='metric_name',
    version='1.0.0',
    compute_func=func,
    inputs=['utterances_df'],
    outputs=['result']
)
```

### `stta.dashboard` - Visualization

**Technology:** Streamlit + Plotly

**Features:**
- Interactive filters (call, speaker, time range)
- KPI cards with metrics
- Timeline Gantt chart
- Speaking time distribution
- Quality dashboards
- Data table with download

**Design Decisions:**
- Use `@st.cache_data` for performance
- Lazy loading of Parquet files
- Client-side interactivity (no server state)

### `stta.report` - PDF Generation

**Technology:** ReportLab + kaleido

**Process:**
1. Export Plotly charts to PNG (kaleido)
2. Build PDF document (ReportLab)
3. Embed KPIs, charts, tables, narrative

**Design Decisions:**
- Static PDF (no interactivity)
- High-resolution charts (scale=2)
- Professional layout (A4, margins)

### `stta.cli` - Command-Line Interface

**Technology:** Typer + Rich

**Commands:**
- `ingest` - CSV → Parquet
- `compute` - Calculate metrics
- `dashboard` - Launch Streamlit
- `version` - Show version info

---

## Data Flow

```
CSV Files
   ↓
[ingest]
   ↓
calls.parquet + utterances.parquet
   ↓
[compute]
   ↓
call_metrics.parquet
speaker_metrics.parquet
quality_metrics.parquet
   ↓
[dashboard]
   ↓
Interactive UI + PDF Export
```

---

## Configuration System

### `config/default.yml`

Global settings:
- File paths
- CSV parsing options
- Validation rules
- Dashboard themes

### `config/speakers.yml`

Speaker label mapping:
```yaml
map:
  "Agent": "AGENT"
  "Zákazník": "CUSTOMER"
default: "UNKNOWN"
```

### Override Mechanism

1. Load `config/default.yml`
2. Merge `config/local.yml` (if exists)
3. Command-line args override config

---

## Storage Format

### Why Parquet?

- **Columnar** - Fast filtering and aggregation
- **Compressed** - 10-50x smaller than CSV
- **Typed** - Schema enforcement
- **Fast** - Direct memory mapping
- **Portable** - Works across platforms

### Schema Versioning

Each Parquet file includes metadata:
```python
{
    'schema_version': '1.0.0',
    'created_at': '2025-10-20T12:00:00',
    'row_count': '1234'
}
```

---

## Error Handling

### Philosophy

**Never guess, always flag**

Invalid data is marked but preserved:
```python
{
    'valid_time': False,
    'invalid_reason': 'nonpositive_duration'
}
```

### Logging Strategy

**Structured logging with loguru:**

```python
logger.info("Processing call", call_id=call_id)
logger.warning("Invalid timestamp", row=i, reason=reason)
logger.error("Failed to parse CSV", file=path, error=e)
```

Logs written to:
- Console (colored, formatted)
- `artifacts/run.log` (structured, rotated)

---

## Testing Strategy

### Unit Tests

- `test_timecode.py` - Time parsing
- `test_text.py` - Text utilities
- `test_timeline.py` - Sweep-line algorithm

### Property-Based Tests

Using Hypothesis:
```python
@given(intervals=st.lists(st.tuples(st.floats(), st.floats())))
def test_invariants(intervals):
    # Test L + S = T
    # Test O ≤ L
    # Test Σ A_k = L
```

### Golden Tests

Small CSV files with known expected outputs in `tests/data/`

### Integration Tests

End-to-end pipeline tests (future)

---

## Performance Considerations

### Optimization Targets

- Ingest: 1000 calls/minute
- Metrics: 100 calls/second
- Dashboard: < 2s load time

### Techniques

- **Vectorized operations** (Pandas/NumPy)
- **Lazy loading** (Streamlit cache)
- **Parquet partitioning** (future: by date)
- **Incremental processing** (future: only new files)

---

## Extensibility Points

### Phase 2: AI Features

Plugin-style additions without modifying core:

```python
# New metric plugin
@registry.register_metric
def sentiment_score(utterances_df):
    # Local sentiment analysis
    return scores
```

### API Ingestion

New input adapter:
```python
class APIReader(BaseReader):
    def read(self, endpoint) -> (calls_df, utterances_df):
        # Fetch from API
        # Normalize to same schema
        return calls_df, utterances_df
```

---

## Security Considerations

### Data Privacy

- **No cloud uploads** - All processing local
- **No API keys** - No external dependencies
- **No PII exposure** - Reports stay on disk

### Validation

- **Schema enforcement** - Pandera validates types
- **Input sanitization** - No SQL injection (no SQL)
- **File path validation** - No directory traversal

---

## Deployment

### Local Installation

```bash
# Clone repo
git clone <repo>

# Run one-click launcher
oneclick.bat
```

### Requirements

- Python 3.10+
- 4GB RAM minimum
- Windows (for .bat), Linux/Mac (adapt shell script)

### Troubleshooting

See `docs/TROUBLESHOOTING.md` (future)

---

## Future Architecture

### Phase 2 Additions

- **Sentiment module** (`stta.metrics.sentiment`)
- **Topic modeling** (`stta.metrics.topics`)
- **Knowledge graph** (`stta.graph`)
- **WER calculator** (`stta.metrics.wer`)

### Phase 3 Vision

- **Real-time processing** (streaming)
- **Multi-tenant** (database backend)
- **REST API** (FastAPI)
- **Web UI** (React)

---

## Version History

- **v0.1.0** - Initial implementation (Phase 1)
- **v0.2.0** - Planned: AI features (Phase 2)
- **v1.0.0** - Planned: Production-ready (Phase 3)
