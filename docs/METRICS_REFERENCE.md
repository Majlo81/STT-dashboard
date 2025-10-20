# Metrics Reference Guide

Comprehensive documentation of all metrics computed by the STT Analytics Platform.

---

## Mathematical Notation

For a call with N utterances:

- **Interval** `[s_i, e_i)` = utterance i from start to end (half-open)
- **Speaker** `k` ∈ {AGENT, CUSTOMER, OTHER, UNKNOWN}
- **Timeline** `T` = max(e_i) - min(s_i)
- **Valid utterances** = subset with `valid_time = True`

---

## Timeline Metrics (Sweep-Line)

### Total Duration (T)

**Formula:** `T = max(end_sec) - min(start_sec)`

**Unit:** seconds

**Interpretation:** Actual time span covered by utterances (may differ from metadata duration)

**Example:** 
- First utterance starts at 0.0s
- Last utterance ends at 120.5s
- T = 120.5s

---

### Speech Time (L)

**Formula:** Union of all intervals

```
L = ∫ 1{at least one speaker active at time t} dt
```

**Algorithm:** Sweep-line computes exact union

**Unit:** seconds

**Interpretation:** Total time with active speech (gaps excluded, overlaps counted once)

**Invariant:** `L + S = T`

---

### Silence Time (S)

**Formula:** `S = T - L`

**Unit:** seconds

**Interpretation:** Time without any active speech

**Note:** Computed residually, guaranteed non-negative

---

### Overlap Time (O)

**Formula:** Time with ≥2 speakers simultaneously

```
O = ∫ 1{at least two speakers active at time t} dt
```

**Unit:** seconds

**Interpretation:** Multi-talk, interruptions, cross-talk

**Invariant:** `O ≤ L`

---

### Silence Ratio

**Formula:** `silence_ratio = S / T`

**Unit:** ratio [0, 1]

**Interpretation:** Proportion of timeline that is silent

---

### Overlap Ratio

**Formula:** `overlap_ratio = O / T`

**Unit:** ratio [0, 1]

**Interpretation:** Proportion of timeline with simultaneous speech

---

### Speech-to-Silence Ratio

**Formula:** `speech_to_silence = L / S`

**Unit:** ratio [0, ∞]

**Interpretation:** How much more speech than silence

**Special case:** If S = 0, returns `inf`

---

## Speaking Time Metrics

### Raw Speaking Time (R_k)

**Formula:** Sum of durations for speaker k

```
R_k = Σ (e_i - s_i) for all i where speaker_i = k
```

**Unit:** seconds

**Interpretation:** Total time speaker k was talking (overlaps double-counted)

**Note:** `Σ R_k ≥ L` because overlaps counted multiple times

---

### Apportioned Speaking Time (A_k)

**Formula:** Fair distribution of overlaps

```
A_k = ∫ 1{speaker k active} / {count of active speakers} dt
```

**Algorithm:** Sweep-line distributes overlap time evenly

**Unit:** seconds

**Interpretation:** Fair speaking time (overlaps shared)

**Invariant:** `Σ A_k = L` (exactly)

**Example:**
- Segment [0, 5): only AGENT → AGENT gets 5.0s
- Segment [5, 7): AGENT + CUSTOMER → each gets 1.0s
- Segment [7, 10): only CUSTOMER → CUSTOMER gets 3.0s
- Result: AGENT = 6.0s, CUSTOMER = 4.0s, Total = 10.0s

---

## Turn Metrics

### Turn Definition

A **turn** is a maximal sequence of consecutive utterances by the same speaker, regardless of gaps.

**Example:**
```
AGENT:    [0, 5)
AGENT:    [6, 8)   <- same turn (gap doesn't break it)
CUSTOMER: [9, 12)  <- new turn
```

---

### Turn Count

**Formula:** Count of maximal same-speaker blocks

**Unit:** count

**Interpretation:** Number of times a speaker held the floor

---

### Speaker Switches

**Formula:** `switches = turn_count - 1`

**Unit:** count

**Interpretation:** Number of turn changes

---

### Switches Per Minute

**Formula:** `switches_per_min = switches / (T / 60)`

**Unit:** switches/minute

**Interpretation:** Conversation pace (higher = more back-and-forth)

---

### Average Turn Duration

**Formula:** `avg_turn_duration = A_k / turn_count_k`

**Unit:** seconds

**Interpretation:** How long each speaker typically holds floor

---

## Interruption Metrics

### Interruption Definition

An **interruption** occurs when:
1. Speaker Y starts before speaker X finishes
2. X ≠ Y (different speakers)

**Detection:**
```
if next_start < current_end AND next_speaker ≠ current_speaker:
    interruption by next_speaker
```

---

### Interruption Count

**Total:** Count across all speakers

**By Speaker:** Count of times each speaker interrupted

**Unit:** count

**Interpretation:** Conversation dynamics, assertiveness

---

## Utterance Metrics

### Utterance Count

**Formula:** `N = count of rows`

**Valid count:** `N_valid = count where valid_time = True`

**Unit:** count

---

### Average Utterance Duration

**Formula:** `mean(duration_sec)` for valid utterances

**Unit:** seconds

**Also computed:** median, P95

---

### Average Utterance Words

**Formula:** `mean(word_count)` for valid utterances

**Unit:** words

**Also computed:** median, total

---

## Gap Metrics

### Gap Definition

For consecutive utterances i and i+1:

```
gap = start_{i+1} - end_i
```

**Positive gap** = silence between utterances  
**Negative gap** = overlap (next starts before current ends)

---

### Gap Statistics

**Average Gap:** `mean(gaps)`

**Median Gap:** `median(gaps)`

**P95 Gap:** `percentile(gaps, 95)`

**Unit:** seconds

**Interpretation:** 
- Large positive gaps = long pauses
- Many negative gaps = frequent overlaps

---

### Negative Gap Count

**Formula:** `count(gap < 0)`

**Unit:** count

**Interpretation:** How often overlaps occur

---

## Speaker-Level Metrics

### Words Per Minute (WPM)

**Formula:** `WPM_k = (total_words_k / A_k) * 60`

**Unit:** words/minute

**Interpretation:** Speech rate (uses apportioned time for fairness)

**Typical values:**
- Slow: 100-120 WPM
- Normal: 120-150 WPM
- Fast: 150-180 WPM

---

### Longest Monologue

**Formula:** `max(turn_duration_k)`

**Unit:** seconds

**Interpretation:** Longest uninterrupted speaking period

---

### Dialog Balance (Gini)

**Formula:** Gini coefficient on apportioned times

```
G = (2 * Σ(i * A_i)) / (n * Σ(A_i)) - (n+1)/n
```

where A_i are sorted apportioned times

**Unit:** ratio [0, 1]

**Interpretation:**
- G = 0: perfect balance (equal speaking time)
- G = 1: total imbalance (one speaker dominates)

**Typical values:**
- Balanced: < 0.3
- Moderate: 0.3 - 0.5
- Imbalanced: > 0.5

---

## Quality Metrics

### Invalid Time Ratio

**Formula:** `invalid_time_ratio = count(valid_time = False) / N`

**Unit:** ratio [0, 1]

**Interpretation:** Data quality indicator

**Causes:**
- Missing timestamps
- Negative durations
- Parse errors

---

### Unknown Speaker Ratio

**Formula:** `unknown_speaker_ratio = count(speaker = UNKNOWN) / N`

**Unit:** ratio [0, 1]

**Interpretation:** Speaker labeling quality

---

### Empty Text Ratio

**Formula:** `empty_text_ratio = count(text.strip() = '') / N`

**Unit:** ratio [0, 1]

**Interpretation:** Transcription completeness

---

### Quality Score

**Formula:** Weighted average

```
quality_score = 
    0.5 * (1 - invalid_time_ratio) +
    0.3 * (1 - unknown_speaker_ratio) +
    0.2 * (1 - empty_text_ratio)
```

**Unit:** ratio [0, 1]

**Interpretation:**
- 0.9 - 1.0: Excellent
- 0.7 - 0.9: Good
- 0.5 - 0.7: Fair
- < 0.5: Poor

---

### Metadata Timeline Delta

**Formula:** `|call_duration_meta - T|`

**Unit:** seconds

**Interpretation:** Consistency check between metadata and computed

**Note:** Only computed if metadata duration exists

---

## Metric Dependencies

```
Timeline Stats (sweep-line)
    ├─> T, L, O, S
    ├─> Apportioned times (A_k)
    └─> Raw speaking times (R_k)

Call Metrics
    ├─> Timeline Stats (input)
    ├─> Gaps (computed from sorted utterances)
    ├─> Turns (computed from speaker sequence)
    └─> Interruptions (overlap + speaker change)

Speaker Metrics
    ├─> Timeline Stats (input)
    ├─> Turns (computed from speaker sequence)
    └─> WPM (words / apportioned time)

Quality Metrics
    ├─> Timeline Stats (input)
    └─> Metadata comparison
```

---

## Computation Order

1. **Load utterances** → sort by time
2. **Compute timeline** (sweep-line) → T, L, O, S, A_k, R_k
3. **Compute gaps** → gap statistics
4. **Compute turns** → turn count, switches
5. **Compute interruptions** → interruption counts
6. **Compute call metrics** → aggregate everything
7. **Compute speaker metrics** → per-speaker stats
8. **Compute quality** → validation metrics

---

## Phase 2: Planned Metrics

### Sentiment Score

**Per utterance:** [-1, 1] negative to positive

**Aggregated:** Mean per speaker, per call

### Topic Distribution

**Per call:** Probability distribution over topics

**Method:** LDA or NMF (local, no API)

### Entity Extraction

**Entities:** People, organizations, products, order IDs

**Graph:** Entity relationships

### WER (Word Error Rate)

**Formula:** `WER = (S + D + I) / N`

where:
- S = substitutions
- D = deletions
- I = insertions
- N = reference word count

**Note:** Requires reference transcripts
