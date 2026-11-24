---
course: "Online Experiments and A/B Testing"
code: "DS-302"
version: "2027.2.0"
deck: "day4"
day: 4
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-302/slides/day4.html"
---

# Online Experiments and A/B Testing

## Day 4: Decide and review

From numbers to a decision: AI-feature tests, many segments, the recommendation and the review board

#### [day4#title] Decide and review

*SDAIA Academy · Online Experiments and A/B Testing*

Day 4: From numbers to a decision: AI-feature tests, many segments, the recommendation and the review board

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-302

#### [day4#agenda] Decide and review

*Today*

- **Session 1 · Testing AI features**: An AI feature adds latency, cost and new harms; the review board stops a test whose harm guardrail worsens
- **Session 2 · Many segments**: Twenty segments at 5% each will show false wins; control the family or the false discovery rate
- **Session 3 · Writing the recommendation**: One page: the decision, the effect with its interval, the guardrails, the risks, the rule that decided
- **Session 4 · The review board**: A board reads write-ups for faults before it reads their results, and decides launch, iterate or stop

#### [day4#review-day3] Which design measures the courier-priority rule as it would run for everyone?

*Review of Day 3*

**Question:** Joud wants the effect of giving priority to orders under a new dispatch rule, as it would be if every order in a city used it. Customer randomisation showed a 10.4-minute gain. Which design answers her question?

- A. Customer randomisation with twice the traffic
- B. Order randomisation within each customer
- C. A city-by-hour switchback, analysed over blocks
- D. Customer randomisation with a Bonferroni correction

### Session 1: Testing AI features

#### [day4#s1] Testing AI features

*Session 1*

- Analyse an AI-feature test with latency, cost and harm guardrails
- Detect novelty decay in a weekly effect
- Apply a decision rule in which harm overrides the primary metric

#### [day4#ai-features-differ] An AI feature brings three guardrails a button never needed

*What changes when the treatment is a model*

- **Latency.** A model answers in seconds, not milliseconds; the tail is where customers leave.
- **Cost.** Every call is paid for; cost per conversation is a metric with a limit.
- **Harm.** A fluent answer can be wrong: an ingredient that is not there, an allergen missed.

> **National reference.** The SDAIA Generative AI Guidelines list misinformation among the risks and ask for monitoring and human supervision of a deployed system.

#### [day4#luqma-test] T-401: Luqma replaces the help menu for half of Sufrah's customers

*Lab 4.1 · the case*

- 60,203 customers with Luqma, 59,797 with the old help menu, four weeks.
- Primary: orders per customer over the four weeks.
- Guardrails: p95 response time at most 5 s, cost per conversation at most 0.12 SAR, complaints at most +1.0 per 1,000 orders.
- **Harm guardrail:** wrong ingredient or allergen complaints at most +0.3 per 1,000 orders, judged on the upper bound.

- **The written rule.** Stop if the harm guardrail fails. Otherwise launch if the primary interval is above zero and every guardrail holds; iterate if a non-harm guardrail fails.

#### [day4#luqma-results] Customers order more, and wrong answers about food rise

*Lab 4.1, steps 1 to 3*

| Metric | Old help menu | Luqma | Against the plan |
| --- | --- | --- | --- |
| Orders per customer, 4 weeks | 5.08 | 5.19 (+2.1%) | difference +0.105, interval 0.034 to 0.176: above zero |
| p95 response time | 0.98 s | 3.94 s | holds (limit 5 s) |
| Cost per conversation | 0.00 SAR | 0.07 SAR | holds (limit 0.12) |
| Complaints per 1,000 orders | 5.58 | 6.03 | upper bound +0.83: holds |
| Wrong ingredient or allergen, per 1,000 | 1.34 | 2.15 | upper bound +1.02: **fails** (limit +0.3) |

#### [day4#novelty] The lift fades week by week: novelty, not a settled effect

*Lab 4.1, step 4*

| Item | Value |
| --- | --- |
| Week 1 | +5.8% |
| Week 2 | +2.5% |
| Week 3 | +0.5% |
| Week 4 | -0.5% |

> **What goes wrong.** Reporting the four-week average, +2.1%, as the long-run effect. Weeks 3 and 4 have intervals that include zero.

#### [day4#holdout-idea] A persistent holdout measures what the launches still deliver months later

*After the launch*

- At the start of a quarter, 10% of customers stay on the current app for six months.
- Every feature that wins its 14-day test ships to the other 90%.
- Each month: orders per customer, launched group against holdout, adjusted with the 28 days before the quarter (Lab 2.2).

- **What it answers.** The combined, settled effect of everything launched: after novelty fades, with the features competing for the same orders.

> **Sufrah's rules.** Share, length and metric fixed before the quarter. Nobody moves in or out. Harm fixes, such as an allergen checker, reach the holdout too.

#### [day4#holdout-read] Four test wins add up to +5.0%; the holdout settles below +2%

*One quarter of launches, read from the holdout*

| Feature, 14-day test | Lift |
| --- | --- |
| Spice-level labels | +2.0% |
| Delivery-time estimates | +1.1% |
| Saved baskets | +1.0% |
| Cuisine filters | +0.9% |
| Sum of the wins | +5.0% |

| Month | Launched over holdout | 95% interval |
| --- | --- | --- |
| 1 | +1.9% | 1.0 to 2.8 |
| 2 | +1.8% | 0.9 to 2.7 |
| 3 | +2.2% | 1.3 to 3.1 |
| 4 | +1.9% | 1.0 to 2.8 |
| 5 | +1.6% | 0.7 to 2.5 |
| 6 | +1.5% | 0.6 to 2.4 |

> **Decision.** Report +1.5% (0.6% to 2.4%) as what the quarter delivers, and plan on it, not on +5.0%. Each test answered its own 14-day question; none was wrong.

#### [day4#harm-overrides] The rule says stop, and it would say so with any lift

*Lab 4.1, step 5*

1. **1 · Harm guardrail** Fails: +0.81 per 1,000, upper bound +1.02
2. **2 · The rule** Stop, before reading the primary
3. **3 · What next** Fix the cause: capstone change C2 adds an allergen checker

> **Takeaway.** A harm guardrail is judged on its upper bound: the test must show the harm is below the limit, not merely fail to show it is above.

#### [day4#check-harm] The harm estimate is small. Is that enough?

*Checkpoint*

**Question:** A new AI menu search raises allergen complaints by +0.10 per 1,000 orders, 95% interval -0.20 to +0.40. The pre-registered limit is +0.30 on the upper bound. What does the rule say?

- A. It holds: the difference is not significantly above zero
- B. It fails: the upper bound, +0.40, is above the limit
- C. It holds: the estimate, +0.10, is below the limit
- D. It cannot be judged without a longer test

#### [day4#lab-4-1] The Luqma chat-assistant test

Lab 4.1 · 25 min

Analyse a chat-assistant test with latency, cost and complaint guardrails, check the lift week by week and apply the harm rule.

[D4_1_chat_assistant_test.ipynb](https://sdaiaacademy.github.io/ds-302/labs/D4_1_chat_assistant_test.ipynb)

- [ ] The primary metric with its interval (5 min)
- [ ] Latency and cost guardrails (5 min)
- [ ] Complaints and wrong-information complaints (6 min)
- [ ] The lift by week: novelty (5 min)
- [ ] The decision and its reason (4 min)
- [ ] ✱ Stretch: Find the city where the harm is largest and say what you would ask the Luqma team

### Session 2: Many segments

#### [day4#s2] Many segments

*Session 2*

- Compute how many false wins 20 uncorrected tests produce
- Apply Holm and Benjamini-Hochberg corrections
- Report the segments that survive and what that means for the decision

#### [day4#twenty-segments] Twenty cuisine segments, four of them "significant"

*Lab 4.2 · the case*

- T-205 added photos to menus. Overall: a small lift.
- The team cut the result by the cuisine of each customer's favourite restaurant: 20 segments.
- Below 0.05: Mandi (p = 0.00001), Coffee (0.001), Indian (0.040, a drop), Desserts (0.049).

**64%** of 20-test analyses with no effect anywhere show at least one p below 0.05; 1.0 false win on average

#### [day4#fwer-vs-fdr] Control the chance of any false win, or the share of false wins you report

*Two error rates to control*

- **Family-wise error: Bonferroni, Holm.** The chance of even one false win stays at 5%. Bonferroni tests each p against 0.05 / 20 = 0.0025; Holm steps down from the smallest p and never rejects less.
- **False discovery rate: Benjamini-Hochberg.** Among the segments you report, the expected share of false ones stays at 5%. Sort the p-values; keep the largest k with p(k) ≤ 0.05 k / 20.

> **On the platforms.** GrowthBook's documentation offers Holm-Bonferroni and Benjamini-Hochberg corrections for many metrics or many variations.

#### [day4#what-survives] Two segments survive every correction; two are chance

*Lab 4.2, steps 3 to 5*

| Segment | Difference | p | Bonferroni | Holm | Benjamini-Hochberg |
| --- | --- | --- | --- | --- | --- |
| Mandi | +0.449 | 0.00001 | kept | kept | kept |
| Coffee | +0.317 | 0.0010 | kept | kept | kept |
| Indian | -0.145 | 0.040 | dropped | dropped | dropped |
| Desserts | +0.137 | 0.049 | dropped | dropped | dropped |

> **What a survivor earns.** A new test, pre-registered on that segment. Not a launch.

#### [day4#check-segments] A segment with p = 0.01

*Checkpoint*

**Question:** Ruba cut a test into 20 city-and-platform segments. One, Abha on Android, has p = 0.01; the other nineteen are above 0.2. With Benjamini-Hochberg at 5%, what does she report?

- A. A win in Abha on Android, because 0.01 is below 0.05
- B. A win with a 1% chance of being false
- C. That segment analysis is never allowed
- D. No segment survives: 0.01 is above its threshold, 0.05 × 1 / 20 = 0.0025

#### [day4#lab-4-2] Twenty segment results, corrected

Lab 4.2 · 25 min

Correct 20 segment results for false discoveries and report what survives.

[D4_2_segment_fdr.ipynb](https://sdaiaacademy.github.io/ds-302/labs/D4_2_segment_fdr.ipynb)

- [ ] Twenty z-tests from the segment table (5 min)
- [ ] How many false wins by chance: simulate (5 min)
- [ ] Bonferroni and Holm (5 min)
- [ ] Benjamini-Hochberg (5 min)
- [ ] What survives, in two sentences (5 min)
- [ ] ✱ Stretch: Shrink the segment effects toward the overall effect and compare

### Session 3: Writing the recommendation

#### [day4#s3] Writing the recommendation

*Session 3*

- Compute every number the pre-registration asks for
- Apply the written decision rule without exception
- Write a one-page recommendation a decision maker can act on

#### [day4#one-page] One page, in the order the reader decides

*The recommendation*

1. **1 · Decision** Launch, iterate or stop, and why, in two sentences
2. **2 · Effect** With its interval, in units a manager uses
3. **3 · Guardrails** Each against its pre-registered limit
4. **4 · Risks, next step** What would change the decision; who does what

> **Takeaway.** The rule that decided is the pre-registered one, applied literally.

#### [day4#t101-numbers] T-101: a clear lift, and latency beyond the limit

*Lab 4.3, steps 2 and 3*

**+3.5%** orders per triggered customer, +0.226 (95% interval 0.179 to 0.273), adjusted with 28 pre-period days

| Guardrail | Value | Limit |
| --- | --- | --- |
| Search p95 latency, difference | +405 ms | at most 300: **fails** |
| Inference cost per 1,000 searches | 5.80 SAR | at most 8.0: holds |
| Complaints per 1,000, upper bound | +0.36 | at most 1.0: holds |
| Revenue, lower bound, relative | +1.6% | at least -1%: holds |

#### [day4#t101-decision] The rule says iterate: a non-harm guardrail failed

*Lab 4.3, step 4*

```python
# file: decide()
if primary["lo"] <= 0 or harm_failed:
    return "stop"
return "launch" if all_hold else "iterate"
```

- The primary interval is far above zero: not a stop.
- Latency is not the harm guardrail: not a stop.
- One guardrail failed: not a launch.
- Next step: cut p95 latency by at least 105 ms, then a 14-day confirmation.

> **What goes wrong.** "The lift is so large that 405 ms is fine." That argument belonged in the pre-registration; after the test it is a moved goalpost.

#### [day4#check-page] What goes first on the page?

*Checkpoint*

**Question:** Rawan's board reads one page per test. Ruba's draft for T-101 opens with the method, then the data, then the effect, and ends with the decision. What should she change?

- A. Put the decision and its reason first; the evidence follows
- B. Put the guardrail table first, because it decided
- C. Drop the interval and keep the point estimate
- D. Add a methods appendix to the page

#### [day4#lab-4-3] A one-page recommendation for T-101

Lab 4.3 · 25 min

Draft a one-page launch recommendation for the AI-ranked search test with effect, interval and guardrails, from its pre-registration.

[D4_3_launch_recommendation.ipynb](https://sdaiaacademy.github.io/ds-302/labs/D4_3_launch_recommendation.ipynb)

- [ ] Read the pre-registration (3 min)
- [ ] The primary effect, adjusted, with its interval (6 min)
- [ ] The four guardrails against their thresholds (6 min)
- [ ] Apply the decision rule (4 min)
- [ ] Write and save the one page (6 min)
- [ ] ✱ Stretch: Add the effect in Riyadh only and say why it does not change the decision

### Session 4: The review board

#### [day4#s4] The review board

*Session 4*

- Check a write-up for sample ratio mismatch, peeking and novelty
- Decide launch, iterate or stop with a stated reason
- Choose and scope the capstone change

#### [day4#board-checklist] Read for faults before you read the result

*The review board*

1. Did the split work? Sample ratio (Lab 1.2).
2. Is the analysis the pre-registered one, at the planned time? (Labs 1.4, 3.1)
3. Is the effect settled, or fading? (Lab 4.1; after launch, the holdout)
4. Did every guardrail hold, the harm guardrail above all? (Labs 1.3, 4.1)
5. Was a segment or a metric picked after the fact? (Lab 4.2)

> **Why this order.** A fault early in the list makes every later number suspect.

#### [day4#w1-w2] W1 fails on the split; W2 fails on the timing

*Lab 4.4, steps 2 and 3*

- **W1 · One-tap reorder banner.** +2.1%, interval 0.9% to 3.3%. Users 50,912 against 49,088: chi-square p = 8 × 10⁻⁹. **Iterate:** find the cause, rerun.
- **W2 · Dish of the day carousel.** Stopped on day 9 at z = 2.19; the planned boundary there was 3.47. The planned day-28 analysis: z = 0.27. **Stop:** no effect.

#### [day4#choose-capstone] Choose the capstone change, knowing what 28 days can detect

*Lab 4.4, step 5*

| Change | Customers | Detectable lift, raw | With pre-period |
| --- | --- | --- | --- |
| C1 · AI-written dish descriptions | 160,000 | 1.7% | 0.85% |
| C2 · Luqma with an allergen checker | 120,000 | 2.0% | 0.98% |
| C3 · AI-ranked restaurant list | 200,000 | 1.5% | 0.76% |

5% two-sided, 80% power, orders per customer over 28 days; the pre-period correlation is about 0.87.

#### [day4#check-board] A write-up with a fading lift

*Checkpoint*

**Question:** A write-up reports +3.0% over four weeks, interval 1.6% to 4.4%, and recommends launch. Its weekly lifts are 7.1%, 2.8%, 0.9% and 0.2%, each with a standard error of 0.8 points. What does the board decide?

- A. Launch: the four-week interval is above zero
- B. Stop: the result is novelty, so there is no effect
- C. Iterate: run longer, because the settled effect is not shown to be above zero
- D. Apply Benjamini-Hochberg to the four weeks

#### [day4#lab-4-4] Two write-ups, and the capstone change

Lab 4.4 · 25 min

Decide two seeded write-ups, score the review log against the reference decisions, and choose the capstone change.

[D4_4_review_board.ipynb](https://sdaiaacademy.github.io/ds-302/labs/D4_4_review_board.ipynb)

- [ ] The review checklist (3 min)
- [ ] W1: check, decide, log (6 min)
- [ ] W2: check, decide, log (6 min)
- [ ] Score the log (3 min)
- [ ] Choose the capstone change and its primary metric (7 min)
- [ ] ✱ Stretch: Decide W3, W4 and W5

#### [day4#wrap-up] Three things to keep

*Day 4*

- **Harm decides first.** Luqma's lift was real; the wrong-information guardrail stopped it.
- **Correct the cuts.** Of four "significant" segments, two survived.
- **Faults before results.** Sample ratio, timing, novelty, guardrails: then the effect.

#### [day4#next] Next: the capstone review board

*Capstone*

- Design and analyse your chosen change with `U.capstone_data()`
- Seven minutes to present, three for the board's questions
- The brief and the rubric are in `labs/capstone/README.md`
