# Testing Guide

## Quick Start

```bash
# Run all tests
pytest

# With coverage
pytest --cov=stta --cov-report=html

# Specific test file
pytest tests/test_timeline.py
```

## Test Categories

- **Unit Tests**: Individual functions
- **Integration Tests**: Full pipeline
- **Property Tests**: Hypothesis-based invariants

## Sample Data

Test data located in `tests/data/`:
- `sample_call.csv` - Basic call
- `sample_call_with_overlap.csv` - Overlapping speech
