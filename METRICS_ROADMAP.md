# Návrh ďalších metrík pre STT Analytics Platform

## 🎯 Základné metriky (Priority 1)

### 1. **Sentiment Analysis Metriky**
**Prečo:** Pochopenie nálady zákazníkov a agentov

**Metriky:**
- `sentiment_score`: Skóre sentimentu (-1 až +1)
- `sentiment_category`: Negatívny / Neutrálny / Pozitívny
- `sentiment_change`: Zmena sentimentu počas hovoru
- `customer_satisfaction_estimate`: Odhadované skóre spokojnosti zákazníka

**Implementácia:**
- Použiť Czech sentiment model (e.g., `Czech-BERT-sentiment`)
- Analyzovať každú utterance
- Agregované skóre pre hovor

---

### 2. **Compliance & Quality Metriky**
**Prečo:** Dodržiavanie skriptov a štandardov

**Metriky:**
- `greeting_present`: Prítomnosť pozdravu (True/False)
- `closing_present`: Prítomnosť rozlúčky (True/False)
- `script_compliance_score`: Dodržanie skriptu (0-1)
- `politeness_score`: Úroveň zdvorilosti
- `professionalism_score`: Profesionalita komunikácie

**Implementácia:**
- Regex patterns pre pozdravy/rozlúčky
- Keyword matching pre script compliance
- NLP model pre zdvorilosť

---

### 3. **Intent & Topic Detection**
**Prečo:** Pochopenie dôvodov hovorov

**Metriky:**
- `primary_intent`: Hlavný dôvod hovoru
- `intent_confidence`: Istota detekcie intentu
- `topics_discussed`: Zoznam diskutovaných tém
- `issue_resolution_status`: Vyriešený / Nevyriešený
- `escalation_required`: Potreba eskalácie

**Kategórie intentov (pre call center):**
- Reklamácia
- Objednávka
- Dotaz na produkt
- Technická podpora
- Zmena údajov
- Storno

---

### 4. **Agent Performance Metriky**
**Prečo:** Hodnotenie výkonu agentov

**Metriky:**
- `response_time_avg`: Priemerný čas reakcie agenta
- `active_listening_score`: Skóre aktívneho počúvania
- `empathy_score`: Empatia v komunikácii
- `problem_solving_score`: Schopnosť riešiť problémy
- `agent_confidence_score`: Istota agenta v odpovediach

**Indikátory:**
- Počet prerusení zákazníka
- Dĺžka pauz pred odpoveďou
- Počet "ehm", "aha", fillerov
- Používanie zákazníkovho mena

---

### 5. **Call Outcome Metriky**
**Prečo:** Meranie úspešnosti hovorov

**Metriky:**
- `call_success_score`: Úspešnosť hovoru (0-1)
- `next_action_scheduled`: Naplánovaná ďalšia akcia
- `callback_required`: Potreba spätného volania
- `first_call_resolution`: Vyriešené pri prvom volaní
- `customer_effort_score`: Náročnosť pre zákazníka

---

## 📊 Pokročilé metriky (Priority 2)

### 6. **Conversation Flow Metriky**
- `turn_taking_balance`: Vyváženie otázok/odpovedí
- `conversation_coherence`: Súdržnosť konverzácie
- `topic_changes_count`: Počet zmien tém
- `backtrack_count`: Počet návratov k predošlým témam

---

### 7. **Language Quality Metriky**
- `grammar_errors_count`: Počet gramatických chýb
- `vocabulary_richness`: Bohatosť slovníka
- `jargon_usage`: Používanie odborných termínov
- `filler_words_rate`: Frekvencia vypĺňacích slov

---

### 8. **Customer Experience Metriky**
- `hold_time_total`: Celkový čas čakania
- `transfer_count`: Počet presmerovani
- `repeat_call_indicator`: Indikátor opakovaného volania
- `issue_complexity_score`: Komplexnosť problému

---

### 9. **Efficiency Metriky**
- `words_per_minute_agent`: Tempo reči agenta
- `words_per_minute_customer`: Tempo reči zákazníka
- `dead_air_time`: Čas bez komunikácie
- `talk_to_listen_ratio`: Pomer hovoru vs počúvania

---

### 10. **Acoustic Features** (ak máme audio)
- `speech_rate_variance`: Variabilita tempa reči
- `pitch_variance`: Variabilita výšky hlasu
- `energy_variance`: Variabilita energie hlasu
- `stress_indicators`: Indikátory stresu v hlase

---

## 🔧 Technická implementácia

### Fáza 1: NLP-based metriky (2-3 týždne)
1. Sentiment analysis
2. Intent detection
3. Keyword extraction
4. Basic compliance checks

### Fáza 2: Rule-based metriky (1-2 týždne)
1. Greeting/closing detection
2. Script compliance
3. Filler words counting
4. Response time calculation

### Fáza 3: ML-based metriky (3-4 týždne)
1. Customer satisfaction prediction
2. Call outcome prediction
3. Topic modeling
4. Agent performance scoring

---

## 📈 Dashboard rozšírenia

### Nové sekcie:
1. **Sentiment Dashboard**
   - Sentiment trend over time
   - Sentiment distribution
   - Customer vs Agent sentiment

2. **Compliance Dashboard**
   - Script compliance rates
   - Greeting/closing adherence
   - Policy violations

3. **Agent Performance Dashboard**
   - Agent leaderboard
   - Performance trends
   - Training recommendations

4. **Call Outcome Dashboard**
   - Resolution rates
   - FCR (First Call Resolution)
   - Escalation tracking

5. **Customer Journey**
   - Call history per customer
   - Issue recurrence
   - CSAT trends

---

## 🎯 Quick Wins (môžeme pridať hneď)

### 1. **Basic Text Statistics**
```python
# Už máme dáta, stačí vypočítať:
- unique_words_count: Počet unikátnych slov
- question_count: Počet otázok (? v texte)
- exclamation_count: Počet výkričníkov
- average_sentence_length: Priemerná dĺžka vety
```

### 2. **Time-based patterns**
```python
# Z existujúcich časových dát:
- peak_call_hours: Najčastejšie hodiny hovorov
- average_wait_time: Priemerný čas čakania
- response_delay_stats: Štatistiky oneskorení odpovedí
```

### 3. **Interaction patterns**
```python
# Z utterances:
- interruption_rate: Frekvencia prerušení
- long_pauses_count: Počet dlhých pauz
- monologue_segments: Segmenty monológu (bez odpovede)
```

---

## 💡 Odporúčania

### Pre ďalší vývoj:
1. **Začnite s Quick Wins** - jednoduché metriky z existujúcich dát
2. **Sentiment Analysis** - vysoká pridaná hodnota, stredná náročnosť
3. **Compliance checks** - dôležité pre call centrá
4. **Agent Performance** - cenné pre manažment

### Priority pre Coworkers.ai:
- **AI Assistant Performance**: Metriky špecifické pre AI agentov
- **Handoff Quality**: Kedy a ako dobre AI predáva ľudskému agentovi
- **Automation Rate**: Koľko hovorov zvládne AI vs ľudí
- **Cost Savings**: Finančné úspory z automatizácie

---

## 🚀 Implementačný plán

### Sprint 2 (1-2 týždne):
- ✅ Branding update (hotové)
- [ ] Quick wins metriky
- [ ] Basic sentiment analysis
- [ ] Greeting/closing detection

### Sprint 3 (2-3 týždne):
- [ ] Intent detection
- [ ] Compliance dashboard
- [ ] Agent performance základy

### Sprint 4 (3-4 týždne):
- [ ] ML-based predictions
- [ ] Customer journey tracking
- [ ] Advanced analytics

---

**Máš nejaké špecifické požiadavky alebo use case pre ktorý potrebuješ prioritizovať určité metriky?**
