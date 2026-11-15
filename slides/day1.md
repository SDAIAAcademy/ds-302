---
course: "Online Experiments and A/B Testing"
code: "DS-302"
version: "2027.1.0"
deck: "day1"
day: 1
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-302/slides/day1.html"
---

# Online Experiments and A/B Testing

## Day 1: Trustworthy experiments

Before any interval: who was assigned, who was exposed, and whether the split can be trusted

#### [day1#title] Trustworthy experiments

*SDAIA Academy · Online Experiments and A/B Testing*

Day 1: Before any interval: who was assigned, who was exposed, and whether the split can be trusted

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-302

#### [day1#agenda] Trustworthy experiments

*Today*

- **Session 1 · Assignment, exposure and triggering**: Who was randomised, who saw the change, and why the triggered effect is the one to estimate
- **Session 2 · Sample ratio mismatch and A/A tests**: A split that is not what was planned voids the result; A/A tests show the false-win rate the analysis really has
- **Session 3 · Metrics for AI features**: A primary metric that measures the goal, and guardrails for what an AI feature adds: latency, cost and harm
- **Session 4 · Power for heavy-tailed metrics**: Sample size from the formula and from simulation on the real distribution, for the population that is triggered

#### [day1#setup-check] One notebook proves your machine is ready

*Before the first lab*

```bash
# file: labs/
uv sync
uv run jupyter lab
# then run 00_setup_check.ipynb
```

In Colab, open the notebook from the course page: its first cell clones the repository and installs the libraries.

- **Nothing to download**: no model, no dataset. The Sufrah data is generated on your machine with fixed seeds.
- **No key**: no lab calls a hosted model; the chat-assistant test of Day 4 is analysed from its logs.
- **Quick mode**: `SUFRAH_QUICK=1` uses 30,000 customers in place of 200,000. The slides quote full mode.

#### [day1#meet-sufrah] Sufrah tests everything, and now it tests AI features

*The case study*

- **The marketplace.** A fictional food-delivery app in six Saudi cities: 200,000 active customers, restaurants, and couriers shared by everyone.
- **Two AI features.** AI-ranked search (test T-101) and Luqma, an in-app chat assistant (T-401). Each adds latency, cost and new ways to harm.
- **The people.** Rawan Al-Mubarak chairs the review board. Yazeed Al-Hamdan owns search. Joud Al-Fahad runs couriers. Waleed Al-Sharif protects data. You are Ruba Kamal, the analyst.

All data is synthetic, generated with fixed seeds: about two million orders over 28 pre-period and 28 test days.

### Session 1: Assignment, exposure and triggering

#### [day1#s1] Assignment, exposure and triggering

*Session 1*

- Separate assignment, exposure and the trigger condition in an event log
- Compute a triggered effect and the diluted overall effect from it
- Explain why counterfactual logging keeps the control group comparable

#### [day1#three-events] Every test log records three different events

*Assignment is not exposure*

1. **1 · Eligible** Active in the last 90 days: all 200,000 customers
2. **2 · Assigned** Day 0: a variant for each customer, 50/50
3. **3 · Exposed** At the first search: the only moment the ranking can matter

> **Triggering.** Analyse the customers whose exposure condition held, in both arms. The others can only add noise.

#### [day1#counterfactual-logging] Log the trigger in control, where nothing visible happens

*The control group must be triggered too*

- **Wrong.** Triggered treatment customers compared with all control customers. The groups differ in who they are: searchers order more.
- **Right.** Control logs "would have seen the AI ranking" at the same moment. Both arms are cut by the same rule, so randomisation still holds inside the cut.

> **The trigger must not depend on the treatment.** A search happens before the ranking is shown, so the rule is safe. "Clicked a result" would not be.

#### [day1#exposure-sql] Exposure is one left join and a minimum

*Lab 1.1, step 2*

```sql
-- file: exposure.sql
select a.customer_id, a.variant, f.exposed_day
from assignments a
left join (select customer_id, min(day) as exposed_day
           from searches where day >= 0
           group by customer_id) f
  on f.customer_id = a.customer_id
```

- **Left join**: a customer who never searched stays, with a NULL exposure day.
- The same pattern counts orders per customer: `coalesce(o.orders, 0)` keeps the customers who did not order.

#### [day1#diluted-vs-triggered] The triggered lift is nearly twice the diluted one

*Measured in Lab 1.1, full mode*

| Population | Customers | Orders per customer, difference | 95% interval | Relative |
| --- | --- | --- | --- | --- |
| All assigned (diluted) | 200,000 | +0.104 | +0.049 to +0.159 | +2.0% |
| Triggered | 85,080 | +0.253 | +0.163 to +0.343 | +3.9% |

> **Dilution.** Overall difference ≈ triggered difference × trigger rate: 0.253 × 0.425 = 0.108, against 0.104 measured.

#### [day1#dilution-formula] Untriggered customers add variance and no signal

*Why dilution costs power*

- The effect shrinks by the trigger rate, here 0.425.
- The noise does not shrink: 57% of the customers still vary.
- Dividing the effect by 0.425 multiplies the customers needed by 1 / 0.425² ≈ 5.5; the assigned population is only 1 / 0.425 ≈ 2.4 times the triggered one.

**5.5 vs 3.7** standard errors from zero: triggered against diluted (Lab 1.1)

#### [day1#check-trigger] Which comparison estimates the effect of AI ranking?

*Checkpoint*

**Question:** T-101 assigned 200,000 customers; 85,080 searched. You want the effect of the new ranking on the people it can reach. Which comparison do you report?

- A. Treatment customers who searched against all control customers
- B. Customers who searched in treatment against customers who searched in control
- C. All treatment customers against all control customers, because it uses more data
- D. Each searcher's orders before and after the first search

#### [day1#lab-1-1] Triggered and diluted effects in SQL

Lab 1.1 · 25 min

Trace assignment and exposure in SQL and compare the triggered effect with the diluted overall effect, on the event stream of the AI-ranked search test.

[D1_1_triggered_exposure.ipynb](https://sdaiaacademy.github.io/ds-302/labs/D1_1_triggered_exposure.ipynb)

- [ ] Read the four tables and their keys (4 min)
- [ ] Join assignments to the first search: who was exposed, when (6 min)
- [ ] Orders per customer, all assigned against triggered, in SQL (6 min)
- [ ] Two effects with intervals, and the dilution formula (6 min)
- [ ] Check: exposure is balanced between the arms (3 min)
- [ ] ✱ Stretch: Count only orders after exposure and say what changes

### Session 2: Sample ratio mismatch and A/A tests

#### [day1#s2] Sample ratio mismatch and A/A tests

*Session 2*

- Test a split against its plan with a chi-square test
- Locate the cause of a mismatch by segment
- Measure a false-positive rate with A/A reshuffles of real data

#### [day1#srm-what] A split that differs from its plan voids the result

*The first check on every test*

- Planned 50/50; observed 50,221 control and 49,028 treatment in T-203.
- A chi-square test against the plan: p = 0.00015.
- The users who went missing were not missing at random, so the remaining arms are no longer comparable.

**49.4%** treatment share in T-203: small to the eye, decisive to the test

> **Never read the metrics of a test that fails this check.** Find the cause first.

#### [day1#srm-causes] Most mismatches come from what happens after assignment

*Where mismatches come from*

- **Lost.** The treatment crashes or loads slower on one build, so its users never log an exposure.
- **Filtered.** A bot filter or a data-quality rule removes more users from one arm.
- **Redirected.** A treatment that redirects or reloads assigns some users twice or not at all.

Diagnose by splitting the counts by every dimension that could lose users unevenly: platform, build, day, browser.

#### [day1#srm-by-build] One Android build loses one treatment user in seven

*Lab 1.2, step 3*

| Item | Value |
| --- | --- |
| iOS 17.2 | 50.3% |
| iOS 17.3 | 50.1% |
| Android 7.3 | 50.6% |
| Android 7.4 | 46.4% |
| Web | 49.3% |

Treatment share of T-203 users by app build, 14 days.

#### [day1#aa-tests] Reshuffle real data to measure the false-win rate you really have

*A/A tests*

1. Take 28 days of pre-period revenue per customer.
2. Split the customers at random into two halves.
3. Run the analysis you plan to use. Record p.
4. Repeat 500 times. Count p below 0.05.

**5.8%** false wins over 500 reshuffles (expected 5% ± 1.9)

- The customer-level Welch test is calibrated on Sufrah's heavy-tailed revenue.

#### [day1#novelty] A new feature can win because it is new

*A trust problem in time*

- **Novelty**: customers try the change because it is different; the lift fades.
- **Primacy**: customers used to the old version resist; the lift grows.
- Check the effect by week since first exposure, not only in total.

- **Day 4.** Luqma, the chat assistant, lifts orders by 5.8% in week one and by nothing measurable in week four. Lab 4.1 measures it.

#### [day1#check-srm] The result looks good, the split does not

*Checkpoint*

**Question:** A 50/50 test shows +3% orders with p = 0.002. Its sample ratio check gives p = 0.0004: the treatment arm has 1.2% fewer users than planned. What do you do?

- A. Report the lift: the arms are large and the gap is only 1.2%
- B. Reweight the treatment arm up to 50% and report the adjusted lift
- C. Report no result, find where users are lost, fix it and rerun
- D. Correct both p-values for multiple testing and report what survives

#### [day1#lab-1-2] Sample ratio and A/A checks

Lab 1.2 · 25 min

Run A/A and sample ratio checks on three tests and name the faulty one, then find the segment that causes the mismatch.

[D1_2_srm_aa_checks.ipynb](https://sdaiaacademy.github.io/ds-302/labs/D1_2_srm_aa_checks.ipynb)

- [ ] Users per arm for three tests (3 min)
- [ ] A chi-square sample ratio test for each (5 min)
- [ ] Find the platform and build that lose users (6 min)
- [ ] A/A: 500 reshuffles of the pre-period, the false-win rate (7 min)
- [ ] Name the faulty test and its cause in one line (4 min)
- [ ] ✱ Stretch: Run the A/A at the order level and explain the higher rate

### Session 3: Metrics for AI features

#### [day1#s3] Metrics for AI features

*Session 3*

- Choose a primary metric that the change can move and that matters to the decision
- Set latency, cost and harm guardrails with thresholds from baseline data
- Decide which event data a test may use under purpose limitation and data classification

#### [day1#primary-vs-guardrail] One primary metric decides; guardrails can only veto

*Metric roles*

| Role | Question it answers | T-101 example |
| --- | --- | --- |
| **Primary** | Did the change do what it is for? | Orders per triggered customer, 28 days |
| **Guardrail** | Did it break something we will not trade? | Search latency, model cost, complaints |
| **Diagnostic** | Why did it move? | Clicks on the first result, searches per session |

> **A guardrail is not a second primary.** A guardrail that "improved" does not rescue a primary that did not move.

#### [day1#ai-adds-three] A model call adds latency, cost and new harms

*What an AI feature adds*

- **Latency.** Every search waits for the model. Measure the tail: p95, not the mean.
- **Cost.** A price per call, paid on every search, forever. Measure per 1,000 searches.
- **Harm.** Wrong or unavailable items ranked first, unsafe answers, unfair exposure. Measure complaints and flags.

The SDAIA Generative AI Guidelines ask that the risks of a generative feature be assessed and monitored; a harm guardrail is how a test does it.

#### [day1#ramp-baselines] The ramp shows latency and cost at once, not the effect

*Lab 1.3, step 1: the 7-day ramp*

|  | p50 latency | p95 latency | Cost per 1,000 searches |
| --- | --- | --- | --- |
| Keyword ranking | 379 ms | 676 ms | SAR 0.2 |
| AI ranking | 543 ms | 1,095 ms | SAR 5.8 |

5% of searches on the AI ranking for seven days: about 6,000 searches. Too few to see a 2% change in orders; plenty to see a 400 ms tail.

#### [day1#guardrail-spec] A guardrail is a metric, a direction and a number, written before the test

*Writing a guardrail*

```json
// file: T101_metric_spec.json
{"metric": "search latency p95 (ms), treatment minus control",
 "kind": "latency", "direction": "at most", "threshold": 300},
{"metric": "inference cost per 1,000 searches (SAR)",
 "kind": "cost", "direction": "at most", "threshold": 8.0},
{"metric": "complaints per 1,000 orders, upper 95% bound of the difference",
 "kind": "harm", "direction": "at most", "threshold": 1.0, "harm": true}
```

> **Harm guardrails use the interval.** The upper bound must stay under the line: "no evidence of harm" is not enough.

#### [day1#purpose-limitation] A test may read only the data its purpose needs

*Lab 1.3, step 4*

- The **Personal Data Protection Law** lets a controller process personal data for the purposes it was collected for, and asks that it be limited to the minimum necessary.
- The **NDMO Data Classification Policy** has four levels: Top Secret, Secret, Restricted, Public. The level sets how data is protected, not whether this use is allowed.

| Field | Use in T-101? |
| --- | --- |
| complaint category | yes |
| complaint text | no: the category suffices |
| exact delivery coordinates | no: city suffices |
| allergy profile | no: health data |

#### [day1#check-metrics] The primary wins, a guardrail fails

*Checkpoint*

**Question:** The AI ranking lifts orders by 3.9% (interval well above zero). Its p95 latency is 420 ms worse; the pre-registered limit was 300 ms. What does the spec say?

- A. Not a launch as is: the latency guardrail fails, so the decision rule applies
- B. Launch: a 3.9% lift is worth more than 120 ms
- C. Raise the latency limit to 450 ms and launch
- D. Report latency as a side note to the primary result

#### [day1#lab-1-3] A metric spec for AI-ranked search

Lab 1.3 · 25 min

Define a primary metric and latency, cost and harm guardrails for the AI-ranked search test from its ramp data, and decide which fields the analysis may use.

[D1_3_ai_search_metrics.ipynb](https://sdaiaacademy.github.io/ds-302/labs/D1_3_ai_search_metrics.ipynb)

- [ ] Baselines from the ramp: latency, cost, conversion, complaints (6 min)
- [ ] The primary metric and its unit (4 min)
- [ ] Three guardrails with thresholds and directions (6 min)
- [ ] The data inventory: which fields the test may use (6 min)
- [ ] Save the metric spec (3 min)
- [ ] ✱ Stretch: Add a guardrail that protects small restaurants and say how you would measure it

### Session 4: Power for heavy-tailed metrics

#### [day1#s4] Power for heavy-tailed metrics

*Session 4*

- Compute a sample size with the two-sample formula
- Estimate power by simulation from historical data
- Explain when the formula and the simulation disagree for a heavy-tailed metric

#### [day1#power-recap] Sample size grows with the variance and with one over the effect squared

*From the pre-work*

```python
# file: formula
n_per_arm = 2 * (z_0.975 + z_0.80)**2 * sd**2 / delta**2
          = 2 * 7.85 * sd**2 / delta**2
```

- Halve the effect: four times the customers.
- Halve the standard deviation: a quarter of them.
- Day 2 is about the second line.

#### [day1#heavy-tail] Revenue per customer has a long tail of group orders

*Lab 1.4, step 1*

- **511** mean SAR, 28 days, customers who search
- **295** median SAR
- **9.4%** of revenue from the top 1% of customers

Standard deviation 747 SAR, largest customer 31,104 SAR: catering and group orders, about one order in a hundred.

#### [day1#power-by-simulation] Simulate the test you will run on the data you have

*Power by simulation*

```python
# file: Lab 1.4 · sim_power
for _ in range(sims):
    c = rng.choice(values, n)                  # control arm from history
    t = rng.choice(values, n) * (1 + lift)     # treatment arm, lifted
    hits += ttest_ind(t, c, equal_var=False).pvalue < 0.05
power = hits / sims
```

- Keeps the real distribution, tail included.
- Works for any analysis: capping, triggering, a sequential plan, a ratio metric.

#### [day1#formula-vs-sim] At 84,000 per arm the formula and the simulation agree

*Lab 1.4, full mode, 400 simulations*

| Customers per arm | Simulated power | Formula |
| --- | --- | --- |
| 20,924 | 0.31 | 0.29 |
| 41,849 | 0.57 | 0.51 |
| 83,699 | 0.77 | 0.80 |
| 104,623 | 0.85 | 0.88 |

> **What the formula hides.** Its standard deviation came from one sample. A sample that missed a few giant orders gives a sigma, and a size, that are too small.

#### [day1#traffic] Revenue needs twice the traffic of orders for the same 2% lift

*Lab 1.4, step 5*

| Item | Value |
| --- | --- |
| Revenue per customer | 83,699 per arm, about 55 days |
| Orders per customer | 41,480 per arm, about 27 days |

> **So T-101 runs 28 days on orders per triggered customer.** Revenue becomes a guardrail with a one-sided limit.

#### [day1#check-power] How many customers for a smaller effect?

*Checkpoint*

**Question:** A test needs 41,000 customers per arm to detect a 2% lift in orders with 80% power. The product manager now wants to detect 1%. Roughly how many per arm?

- A. 82,000
- B. 58,000
- C. 20,500
- D. 164,000

#### [day1#lab-1-4] Power by simulation for the search test

Lab 1.4 · 25 min

Size the search test by simulation on revenue per user and compare with the textbook formula, for triggered customers.

[D1_4_power_heavy_tails.ipynb](https://sdaiaacademy.github.io/ds-302/labs/D1_4_power_heavy_tails.ipynb)

- [ ] Revenue per triggered customer: mean, spread, tail (4 min)
- [ ] The formula: customers per arm for a 2% lift (5 min)
- [ ] Power by simulation at that size (7 min)
- [ ] A power curve and the size for 80% power (5 min)
- [ ] Weeks of traffic needed, and the same for orders per customer (4 min)
- [ ] ✱ Stretch: Repeat with a 1% lift and say whether the test is worth running

#### [day1#wrap-up] Three things to keep

*Day 1*

- **Trigger, in both arms.** Analyse who could be affected, with the same rule in control.
- **Check the split first.** A sample ratio mismatch voids the test; find the cause before any metric.
- **Write the limits first.** A primary, guardrails with numbers, and a size from simulation, all before the test.

#### [day1#next] Next: the same test, a narrower interval

*Day 2*

- Capping the tail, and what it changes in the estimate
- Pre-period data that removes most of the noise
- Intervals for ratio metrics that respect the customer
