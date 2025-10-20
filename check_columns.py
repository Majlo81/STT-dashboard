import pandas as pd

df = pd.read_parquet('data/clean/call_metrics.parquet')
print("call_metrics columns:")
for col in df.columns:
    print(f"  - {col}")

print("\nquality_metrics columns:")
df2 = pd.read_parquet('data/clean/quality_metrics.parquet')
for col in df2.columns:
    print(f"  - {col}")
