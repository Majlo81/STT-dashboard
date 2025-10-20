import pandas as pd
import yaml

# Load config
with open('config/default.yml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Read CSV
df = pd.read_csv(
    'data/raw/DATA.csv',
    sep=';',
    dtype=str,
    keep_default_na=False,
    encoding='utf-8-sig',
    nrows=50
)

print("Original columns (first 3):")
for i, col in enumerate(df.columns[:3]):
    print(f"  {i}: '{col}'")

# Apply column mapping
column_mapping = config['parsing']['column_mapping']
df_renamed = df.rename(columns=column_mapping)

print("\nAfter mapping (first 3):")
for i, col in enumerate(df_renamed.columns[:3]):
    print(f"  {i}: '{col}'")

# Check first column values
timestamp_col = df_renamed.columns[0]
print(f"\nFirst column: '{timestamp_col}'")
print(f"Non-null count: {df_renamed[timestamp_col].notna().sum()}")
print(f"Null count: {df_renamed[timestamp_col].isna().sum()}")

print(f"\nFirst 10 values of '{timestamp_col}':")
for i, val in enumerate(df_renamed[timestamp_col].head(10)):
    status = "FILLED" if val else "EMPTY"
    print(f"  Row {i}: {status} - '{val}'")
