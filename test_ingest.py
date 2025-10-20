import yaml
from pathlib import Path
from stta.io.reader import CSVReader
from stta.utils.logging import setup_logging

# Setup logging
setup_logging(log_file=Path("artifacts/test.log"), level="DEBUG")

# Load config
with open('config/default.yml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Load speaker mapping
with open('config/speakers.yml', 'r', encoding='utf-8') as f:
    speaker_config = yaml.safe_load(f)
    speaker_mapping = speaker_config.get('map', {})

# Create reader
reader = CSVReader(
    encodings=config['parsing']['encodings_try'],
    delimiter=config['parsing']['delimiter'],
    speaker_mapping=speaker_mapping
)

# Try to read the file
csv_file = Path('data/raw/DATA.csv')
print(f"Reading: {csv_file}")

try:
    calls_df, utterances_df = reader.read_csv_file(csv_file, config['parsing'])
    print(f"\nSUCCESS!")
    print(f"  Calls: {len(calls_df)} rows")
    print(f"  Utterances: {len(utterances_df)} rows")
    print(f"\nFirst call metadata:")
    print(calls_df.iloc[0].to_dict())
    print(f"\nUtterance columns: {utterances_df.columns.tolist()}")
    print(f"\nFirst 3 utterances:")
    print(utterances_df.head(3)[['utterance_index', 'speaker', 'start_sec', 'end_sec', 'duration_sec', 'word_count']].to_string())
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
