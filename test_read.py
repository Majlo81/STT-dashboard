import pandas as pd
import yaml
from pathlib import Path

# Load config
with open('config/default.yml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Read CSV
df = pd.read_csv(
    'data/raw/DATA.csv',
    sep=';',
    dtype=str,
    keep_default_na=False,
    encoding='utf-8',
    nrows=5
)

print("Original columns:")
for col in df.columns:
    print(f"  - '{col}'")

# Apply column mapping
column_mapping = config['parsing']['column_mapping']
df_renamed = df.rename(columns=column_mapping)

print("\nAfter mapping:")
for col in df_renamed.columns:
    print(f"  - '{col}'")

print(f"\nFirst row:\n{df_renamed.iloc[0].to_dict()}")
