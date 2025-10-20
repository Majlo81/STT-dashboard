# Bug Fixes - Session 2025-10-20

## Critical Issues Fixed (Session 2 & 3)

### 🎨 Dashboard UX Issues (Session 3)

**Problem 1:** Timeline shows nonsensical time axis (e.g., `-175935:41` to `06:00:01`)

**Root Cause:** Plotly `timeline` expects datetime objects, not float seconds. Float values were interpreted as Unix timestamps (seconds since 1970-01-01), causing bizarre dates.

**Solution:** Convert float seconds to datetime objects for proper visualization
```python
from datetime import datetime, timedelta

base_time = datetime(2025, 1, 1, 0, 0, 0)
min_start = valid_utts['start_sec'].min()

# Normalize and convert to datetime
valid_utts['start_dt'] = valid_utts['start_sec'].apply(
    lambda x: base_time + timedelta(seconds=float(x - min_start))
)
valid_utts['end_dt'] = valid_utts['end_sec'].apply(
    lambda x: base_time + timedelta(seconds=float(x - min_start))
)

# Format x-axis
fig.update_xaxes(
    tickformat='%M:%S',  # MM:SS format
    title_text="Time from call start (MM:SS)"
)
```

**Result:** ✅ Timeline now correctly shows time in MM:SS format from call start

---

**Problem 2:** No overview for 8,200 calls - filtering one by one is unusable

**Solution:** Added Summary View with:
- KPI cards (total calls, duration, utterances, words, quality)
- Trends over time (calls per day, hourly distribution)
- Metrics distributions (duration, speech ratio)
- Top/Bottom calls (longest, most utterances)
- Quality overview (invalid timestamps, empty text, unknown speakers)
- Date range filter

**Result:** ✅ Now have both Summary (all calls) and Individual Call views

---

### 🐛 Column Name Mismatches

**Problems:**
- Used `utterance_count` but actual column is `total_utterances`
- Used `speaking_time_ratio` but actual column is `speech_ratio`
- Used `invalid_timestamps` but actual column is `invalid_time_count`
- Used `unknown_speakers` but actual column is `unknown_speaker_count`

**Solution:** Fixed all column references to match actual schema

---

## Critical Issues Fixed (Session 2)

### 🚨 MAJOR: Only 1 call detected instead of 8,200

**Problem:** CSV contains 8,200 calls but system detected only 1

**Root Causes:**
1. CSV format misunderstanding - assumed single call per file
2. Empty string `''` vs `NaN` detection failed
3. Column "Aktivity / Přepis hovoru / Aktivity" contained customer_id, not call_id

**Solution:** 
- Added multi-call CSV detection based on timestamp column
- Fixed empty value detection (`df[col] != ''` instead of `notna()`)
- Implemented call boundary detection (rows with timestamp = new call)
- Generated unique call_id using hash of timestamp + agent + customer + index

**Result:** ✅ Now correctly processes 8,200 calls

---

### 🐛 Schema validation error: call_start_meta type mismatch

**Problem:** Schema expected `float64` but code generated `datetime64`

**Solution:** Updated `CallsSchema` to accept `Optional[Series[datetime]]` for `call_start_meta`

---

## Issues Encountered and Resolved (Session 1)

### 1. ❌ ModuleNotFoundError: No module named 'typer'
**Problem:** Virtual environment existed but dependencies weren't installed

**Root Cause:** `oneclick.bat` skipped dependency installation when `.venv` folder existed

**Solution:** Modified `oneclick.bat` to check if key packages are installed before skipping installation
```batch
python -c "import typer" 2>nul
if errorlevel 1 (
    pip install -r requirements.txt --quiet
)
```

---

### 2. ❌ numpy 1.26.4 compilation error (Python 3.13)
**Problem:** `numpy>=1.26.0,<2.0.0` doesn't have pre-built wheels for Python 3.13.9

**Error:**
```
Preparing metadata (pyproject.toml) ... error
subprocess-exited-with-error
```

**Solution:** Updated `requirements.txt` to use numpy 2.x which has Python 3.13 wheels
```python
numpy>=2.0.0,<3.0.0  # Changed from 1.26.0
```

---

### 3. ❌ pyarrow 16.1.0 compilation error (Python 3.13)
**Problem:** PyArrow tried to compile from source (requires cmake, MSVC)

**Solution:** Installed latest pyarrow (21.0.0) which has pre-built wheels for Python 3.13
```bash
pip install numpy pandas pyarrow streamlit plotly --no-cache-dir
```

---

### 4. ❌ ValueError: No objects to concatenate
**Problem:** All CSV files failed to process, resulting in empty DataFrames

**Root Cause:** Multiple cascading issues (see below)

---

### 5. ❌ Column name mismatch (Czech vs English)
**Problem:** CSV has Czech column names but code expects English names

**CSV Structure:**
```
Aktivity / Přepis hovoru / Aktivity → call_id
Aktivity / Přepis hovoru / Text → text
Aktivity / Přepis hovoru / Typ → speaker
Aktivity / Přepis hovoru / Začátek v → start_time
Aktivity / Přepis hovoru / Konec v → end_time
```

**Solution:** Added `column_mapping` to `config/default.yml`
```yaml
column_mapping:
  "Aktivity / Přepis hovoru / Aktivity": "call_id"
  "Aktivity / Přepis hovoru / Text": "text"
  "Aktivity / Přepis hovoru / Typ": "speaker"
  # ... etc
```

Modified `reader.py` to apply mapping:
```python
column_mapping = config.get('column_mapping', {})
if column_mapping:
    df_raw = df_raw.rename(columns=column_mapping)
```

---

### 6. ❌ Speaker label mismatch (Czech labels)
**Problem:** CSV has "customer" and "operator" (Czech context) but no mapping existed

**Solution:** Added Czech labels to `config/speakers.yml`
```yaml
map:
  "customer": "CUSTOMER"  # Added
  "operator": "AGENT"     # Added
  "zákazník": "CUSTOMER"
  "operátor": "AGENT"
```

---

### 7. ❌ ValueError: 'data\raw\DATA.csv' is not in the subpath of cwd
**Problem:** `source_file.relative_to(Path.cwd())` failed when path is already relative

**Error:**
```python
ValueError: 'data\\raw\\DATA.csv' is not in the subpath of 'C:\\Users\\...'
```

**Solution:** Added try-except to handle both relative and absolute paths
```python
try:
    source_file_str = str(source_file.relative_to(Path.cwd()))
except ValueError:
    source_file_str = str(source_file.resolve())
```

---

### 8. ❌ Wrong CSV format assumption
**Problem:** Code expected two-tier format (first row = metadata, rest = utterances) but CSV is flat (all rows are utterances)

**Solution:** Added format detection in `reader.py`
```python
# Detect flat format: call_id appears in multiple rows
is_flat_format = (
    call_id_field in df_raw.columns and
    df_raw[call_id_field].notna().sum() > 1
)

if is_flat_format:
    # All rows are utterances
    utterances_df = self._extract_utterances(df_raw, call_id, config)
```

---

## Results After Fixes

✅ **Successfully processed:**
- 1 CSV file (DATA.csv, 12.3 MB)
- 124,179 rows read
- 75,489 utterances with valid timestamps
- 1 call metadata record

✅ **Generated parquet files:**
- `calls.parquet` (6.5 KB)
- `utterances.parquet` (6.6 MB) 
- `call_metrics.parquet` (18 KB)
- `speaker_metrics.parquet` (10.5 KB)
- `quality_metrics.parquet` (13 KB)

✅ **Dashboard running:** http://localhost:8501

---

## Lessons Learned

1. **Always test with real data early** - Many assumptions about CSV structure were incorrect
2. **Python 3.13 compatibility** - Very new, not all packages have pre-built wheels
3. **Path handling on Windows** - Use `resolve()` or handle `ValueError` from `relative_to()`
4. **CSV format flexibility** - Need to support multiple structures, not just one
5. **Encoding matters** - UTF-8-sig worked better than CP1250 for this Czech CSV

---

## Configuration Updates

### requirements.txt
- ✅ Updated numpy to 2.x for Python 3.13 compatibility
- ✅ All packages now install cleanly without compilation

### config/default.yml
- ✅ Added `column_mapping` section for Czech CSV support
- ✅ Supports flexible column naming

### config/speakers.yml  
- ✅ Added Czech speaker labels (customer, operator, zákazník, operátor)
- ✅ More robust fallback to UNKNOWN

### stta/io/reader.py
- ✅ Added column mapping support
- ✅ Added flat CSV format detection
- ✅ Fixed path handling (relative_to ValueError)
- ✅ More robust error handling

### oneclick.bat
- ✅ Added dependency check before skipping installation
- ✅ Prevents "ModuleNotFoundError" on existing venvs

---

## Testing Performed

1. ✅ `oneclick.bat` - Full pipeline execution
2. ✅ `test_ingest.py` - CSV reading and parsing
3. ✅ `test_read.py` - Column mapping verification
4. ✅ Manual dependency installation
5. ✅ Dashboard launch and accessibility

---

## Next Steps

1. Review dashboard UI with real data
2. Validate metric calculations
3. Test with multiple CSV files
4. Performance benchmarking
5. Add more comprehensive tests
