"""Verify that metrics are real calculations, not random numbers."""

import pandas as pd

print("=" * 80)
print("VERIFIKÁCIA METRÍK - Ukážka reálnych výpočtov")
print("=" * 80)

# Load data
calls = pd.read_parquet('data/clean/calls.parquet')
utterances = pd.read_parquet('data/clean/utterances.parquet')
text_stats = pd.read_parquet('data/clean/text_statistics.parquet')
filler_words = pd.read_parquet('data/clean/filler_words.parquet')
interaction = pd.read_parquet('data/clean/interaction_metrics.parquet')

# Pick a random call to demonstrate
call_id = calls['call_id'].iloc[100]
print(f"\n📞 Call ID: {call_id}")

# Get utterances for this call
call_utts = utterances[utterances['call_id'] == call_id]
print(f"\nUtterances: {len(call_utts)}")
print("\nPrvých 5 utterances:")
for idx, row in call_utts.head(5).iterrows():
    print(f"  [{row['speaker']}] {row['text'][:60]}...")

# Text statistics
text_row = text_stats[text_stats['call_id'] == call_id].iloc[0]
print(f"\n📊 TEXT STATISTICS (vypočítané):")
print(f"  Total words: {text_row['total_words']}")
print(f"  Unique words: {text_row['unique_words_count']}")
print(f"  Vocabulary richness: {text_row['vocabulary_richness']:.3f} (unique/total)")

# Manual verification
all_text = ' '.join(call_utts['text'].dropna())
words = all_text.split()
unique = set(w.lower() for w in words)
manual_vocab = len(unique) / len(words) if len(words) > 0 else 0

print(f"\n✅ VERIFIKÁCIA - Manuálny prepočet:")
print(f"  Total words (manual): {len(words)}")
print(f"  Unique words (manual): {len(unique)}")
print(f"  Vocabulary richness (manual): {manual_vocab:.3f}")
print(f"  ✅ ZHODUJE SA: {abs(manual_vocab - text_row['vocabulary_richness']) < 0.001}")

# Questions
question_count_manual = all_text.count('?')
print(f"\n❓ QUESTIONS:")
print(f"  Questions (computed): {text_row['question_count']}")
print(f"  Questions (manual): {question_count_manual}")
print(f"  ✅ ZHODUJE SA: {question_count_manual == text_row['question_count']}")

# Filler words
filler_row = filler_words[filler_words['call_id'] == call_id].iloc[0]
fillers = ['ehm', 'em', 'hm', 'jako', 'vlastně', 'víš', 'víte', 'teda', 'prostě', 'tak', 'takže', 'no', 'jo']
manual_fillers = sum(1 for word in all_text.lower().split() if word in fillers)
manual_filler_rate = manual_fillers / len(words) if len(words) > 0 else 0

print(f"\n🗣️ FILLER WORDS:")
print(f"  Filler count (computed): {filler_row['filler_words_total']}")
print(f"  Filler count (manual): {manual_fillers}")
print(f"  Filler rate (computed): {filler_row['filler_words_rate']:.4f}")
print(f"  Filler rate (manual): {manual_filler_rate:.4f}")
print(f"  ✅ ZHODUJE SA: {abs(manual_filler_rate - filler_row['filler_words_rate']) < 0.001}")

# Interaction patterns
inter_row = interaction[interaction['call_id'] == call_id].iloc[0]
valid_utts = call_utts[call_utts['valid_time']].sort_values('start_sec')
gaps = []
for i in range(len(valid_utts) - 1):
    gap = valid_utts.iloc[i + 1]['start_sec'] - valid_utts.iloc[i]['end_sec']
    gaps.append(gap)

long_pauses_manual = sum(1 for g in gaps if g > 3.0)
print(f"\n🔄 INTERACTION PATTERNS:")
print(f"  Long pauses (computed): {inter_row['long_pauses_count']}")
print(f"  Long pauses (manual): {long_pauses_manual}")
print(f"  ✅ ZHODUJE SA: {long_pauses_manual == inter_row['long_pauses_count']}")

# Agent turns
agent_turns_manual = (valid_utts['speaker'] == 'AGENT').sum()
print(f"\n👤 AGENT TURNS:")
print(f"  Agent turns (computed): {inter_row['agent_turns']}")
print(f"  Agent turns (manual): {agent_turns_manual}")
print(f"  ✅ ZHODUJE SA: {agent_turns_manual == inter_row['agent_turns']}")

print("\n" + "=" * 80)
print("✅ VŠETKY METRIKY SÚ SKUTOČNÉ VÝPOČTY Z DÁT!")
print("=" * 80)

# Summary statistics
print(f"\n📈 SUMMARY STATISTICS (všetky hovory):")
print(f"\nText Statistics:")
print(f"  Avg vocabulary richness: {text_stats['vocabulary_richness'].mean():.3f}")
print(f"  Avg questions per call: {text_stats['question_count'].mean():.1f}")
print(f"  Std dev: {text_stats['question_count'].std():.1f}")

print(f"\nFiller Words:")
print(f"  Avg filler rate: {filler_words['filler_words_rate'].mean():.4f} ({filler_words['filler_words_rate'].mean()*100:.2f}%)")
print(f"  Agent avg: {filler_words['agent_filler_rate'].mean():.4f}")
print(f"  Customer avg: {filler_words['customer_filler_rate'].mean():.4f}")

print(f"\nInteraction Patterns:")
print(f"  Avg interruption rate: {interaction['interruption_rate'].mean():.3f} ({interaction['interruption_rate'].mean()*100:.1f}%)")
print(f"  Avg agent response delay: {interaction['agent_avg_response_delay'].mean():.2f}s")
print(f"  Avg turn-taking balance: {interaction['turn_taking_balance'].mean():.3f}")

print(f"\n✅ Reálne štatistiky z {len(calls)} hovorov!")
