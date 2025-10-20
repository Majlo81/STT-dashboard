# Changelog

All notable changes to STT Analytics Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Project initialization
- Directory structure
- Configuration system
- Documentation

---

## [0.1.0] - 2025-10-20

### ✅ Released - Sprint 0 Complete

#### Infrastructure
- [x] Project directory structure
- [x] requirements.txt with pinned dependencies
- [x] oneclick.bat Windows launcher
- [x] README.md comprehensive documentation
- [x] PROGRESS.md tracker
- [x] .gitignore configuration
- [x] Configuration files (default.yml, speakers.yml)
- [x] Package structure (stta/)
- [x] Pandera schemas

#### Core Pipeline
- [x] Robust CSV reader with encoding detection
- [x] Timecode parser (HH:MM:SS.mmm support)
- [x] Speaker label normalization
- [x] Sweep-line timeline calculator
- [x] Call-level metrics (17 metrics)
- [x] Speaker-level metrics (10 per speaker)
- [x] Quality metrics (14 metrics)
- [x] Metric registry system
- [x] CLI commands (ingest, compute, dashboard, version)

#### Visualization
- [x] Streamlit dashboard (5 tabs)
- [x] Plotly visualizations
- [x] KPI cards
- [x] Interactive filters (call, speaker, time range)
- [x] PDF export foundation (ReportLab + kaleido)
- [x] Storytelling templates
- [x] Timeline Gantt chart
- [x] Speaking time charts
- [x] Gaps histogram
- [x] Quality dashboards

#### Testing
- [x] Unit tests (timecode, text, timeline)
- [x] Test infrastructure (pytest, coverage)
- [x] Sample test data (2 CSV files)
- [ ] Hypothesis property-based tests (planned)
- [ ] Integration tests (planned)

#### Documentation
- [x] README.md (comprehensive)
- [x] QUICKSTART.md (5-minute setup)
- [x] ARCHITECTURE.md (system design)
- [x] METRICS_REFERENCE.md (all formulas)
- [x] IMPLEMENTATION_SUMMARY.md
- [x] PROJECT_STATUS.md
- [x] PROJECT_TREE.txt
- [x] TESTING.md
- [x] PROGRESS.md
- [x] CHANGELOG.md

---

## Version Notes

### Schema Version: 1.0.0
- Initial data schema for calls and utterances
- Parquet metadata includes `schema_version` field

### Breaking Changes
None (initial release)

### Deprecations
None (initial release)

---

## Roadmap

### Phase 1 (v0.1.0 - v0.3.0) - Current
Focus: Core pipeline and dashboard

### Phase 2 (v0.4.0+) - Planned
Focus: AI/ML features (sentiment, topics, entities)

### Phase 3 (v1.0.0+) - Future
Focus: API ingestion, real-time processing
