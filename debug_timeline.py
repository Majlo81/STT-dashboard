import pandas as pd

# Load data
utterances = pd.read_parquet('data/clean/utterances.parquet')

# Find calls with problematic time ranges
print("Analyzing all calls for time range issues...\n")

call_stats = []
for call_id in utterances['call_id'].unique()[:20]:  # Check first 20
    call_utts = utterances[utterances['call_id'] == call_id]
    valid_utts = call_utts[call_utts['valid_time']]
    
    if len(valid_utts) > 0:
        min_start = valid_utts['start_sec'].min()
        max_end = valid_utts['end_sec'].max()
        time_range = max_end - min_start
        
        call_stats.append({
            'call_id': call_id,
            'min_start': min_start,
            'max_end': max_end,
            'range': time_range,
            'valid_count': len(valid_utts)
        })

# Show calls sorted by min_start (most negative first)
df_stats = pd.DataFrame(call_stats).sort_values('min_start')
print("Calls with most negative/unusual start times:")
print(df_stats.head(10).to_string())

# Pick worst case
worst_call = df_stats.iloc[0]['call_id']
print(f"\n\nWorst case call: {worst_call}")
call_utts = utterances[utterances['call_id'] == worst_call]
valid_utts = call_utts[call_utts['valid_time']]

print(f"First 10 utterances:")
print(valid_utts[['start_sec', 'end_sec', 'duration_sec', 'speaker', 'text']].head(10).to_string())
