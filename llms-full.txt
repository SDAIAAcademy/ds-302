---
course: "Online Experiments and A/B Testing"
code: "DS-302"
version: "2027.2.0"
scope: "course"
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-302/"
---

# Online Experiments and A/B Testing

Run trustworthy online experiments, including tests of AI features, and defend a launch, iterate or stop decision with the right interval

Participants run the statistics behind an experimentation programme that includes tests of AI features. On a synthetic event stream from Sufrah, a fictional food-delivery marketplace, they check tests for trust problems, analyse triggered exposure, reduce variance with pre-experiment data, compute intervals for ratio metrics, design sequential tests for daily monitoring, set guardrails for latency, cost and harm, and measure interference through shared couriers, ending on a mock review board that decides launch, iterate or stop.

- **Audience:** Specialists. Analysts and data scientists who have completed the level 200 set or can show equivalent work: an analysis or model they built, validated and can explain.
- **Prerequisites:** DS-201 Statistical Inference by Simulation; DS-205 Designing and Reading Experiments; Writes SQL with joins and window functions over event logs; Pre-work: two hours on power and the two-sample test, with an entry quiz (see labs/README.md); Setup: a laptop processor with uv, or Google Colab. No lab calls a model or downloads one. Run 00_setup_check before Day 1.
- **Case study:** Sufrah: Sufrah is a fictional food-delivery marketplace in six Saudi cities whose experimentation programme now tests AI features: AI-ranked search and Luqma, an in-app chat assistant. Participants check its tests for trust problems, size and analyse the AI-ranked search test with variance reduction and ratio intervals, monitor tests daily without inflating false wins, measure how a dispatch test is biased by shared couriers, and sit on its review board. All data is synthetic and generated with fixed seeds: 200,000 customers, about two million orders, a daily-peeking simulator and a marketplace simulator.

## Outcomes

- LO1 (Applied): Apply regression adjustment with pre-experiment data and report the sample-size saving, given a test with 28 days of pre-period data per customer
- LO2 (Applied): Compute intervals for ratio metrics with the delta method and with a bootstrap over the randomisation unit, given order-level logs from a customer-randomised test
- LO3 (Applied): Implement group sequential and always-valid tests and measure their false-positive rates under daily monitoring by simulation, given a simulator with and without a true effect
- LO4 (Performance): Design the metric set, power and decision rule for launching an AI feature, given a proposed AI-ranked search change with goals and expected traffic
- LO5 (Performance): Diagnose interference in a marketplace test and design a cluster or switchback alternative with its power, given a simulator in which treated customers take couriers from control customers
- LO6 (Performance): Review experiment write-ups and decide launch, iterate or stop for each, given five write-ups with seeded faults such as sample ratio mismatch, peeking and novelty decay

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

## Day 2: Precision

The same test, a narrower interval: capping, pre-period data, ratio metrics and strata

#### [day2#title] Precision

*SDAIA Academy · Online Experiments and A/B Testing*

Day 2: The same test, a narrower interval: capping, pre-period data, ratio metrics and strata

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-302

#### [day2#agenda] Precision

*Today*

- **Session 1 · Variance and heavy tails**: Group orders make revenue noisy; capping cuts the variance and changes what is estimated
- **Session 2 · Regression adjustment**: Pre-period behaviour predicts test behaviour; removing what it predicts narrows the interval
- **Session 3 · Ratio metrics**: Orders per session is a ratio of two sums per customer; its interval must respect the randomisation unit
- **Session 4 · Stratification**: Cities differ; using that in design or analysis removes between-city noise, sometimes by little

#### [day2#review-day1] Which check comes first?

*Review of Day 1*

**Question:** Ruba receives the results of a 28-day test with a 4% lift on the primary metric, all guardrails green. Which check does she run before reading any of it?

- A. Regression adjustment, to narrow the interval
- B. A false discovery correction over the segments
- C. The sample ratio check on the assignment counts
- D. A power calculation for the observed effect

### Session 1: Variance and heavy tails

#### [day2#s1] Variance and heavy tails

*Session 1*

- Measure how a few large orders drive the variance of revenue per customer
- Cap a metric at a percentile of the pooled data
- Report the bias and the variance a cap trades

#### [day2#variance-sources] One customer in a hundred carries half the variance of revenue

*Lab 2.1, step 1*

- **753** SAR, standard deviation of revenue per triggered customer
- **536** SAR, the same without the top 1% of customers
- **49%** of the variance from that top 1%

85,080 triggered customers, 561,609 test-period orders. About one order in a hundred is a group order worth many baskets.

#### [day2#capping-rule] Count each order up to a cap set from both arms pooled

*Capping, also called winsorising*

```python
# file: Lab 2.1
cap = orders.value.quantile(0.99)   # pooled
v = orders.value.clip(upper=cap)
revenue = v.groupby(orders.customer_id).sum()
```

| Cap | SAR |
| --- | --- |
| 99.9th percentile | 1,402 |
| 99th percentile | 337 |
| 95th percentile | 184 |

> **Never set the cap per arm.** A cap that depends on the treatment can create a difference on its own.

#### [day2#cap-changes-estimand] A capped metric estimates a different, smaller effect

*The price of a cap*

- The ranking adds orders, some of them group orders.
- Capped, those orders count for less: the effect on the capped metric is smaller than on revenue.
- That gap is a **bias** if the decision is about revenue.

- **Only in synthetic data.** The generator knows every customer's orders under both arms, so the true effect of each cap is exact. No real test can measure this bias; a simulation can.

#### [day2#cap-tradeoff] The 99th-percentile cap gives the smallest total error

*Lab 2.1, full mode*

| Cap | Estimate | Standard error | True effect | Bias against uncapped | Root mean square error |
| --- | --- | --- | --- | --- | --- |
| none | 20.13 | 5.16 | 17.91 | 0 | 5.16 |
| 99.9th | 19.71 | 4.34 | 17.37 | -0.54 | 4.37 |
| 99th | 19.11 | 4.02 | 16.70 | -1.21 | 4.20 |
| 95th | 17.92 | 3.72 | 15.91 | -1.99 | 4.23 |

SAR per triggered customer over 28 days.

#### [day2#cap-reporting] Pre-register the cap, report the uncapped result beside it

*Writing it down*

1. The percentile and the data it comes from: pooled, before the test.
2. What the metric now means: revenue with each order counted up to SAR 337.
3. The uncapped estimate in the appendix, so nobody wonders what was hidden.

> **Capping is not deleting.** The large orders stay in the data; they just stop deciding the interval.

#### [day2#check-capping] Where does the cap come from?

*Checkpoint*

**Question:** Ruba wants to cap order value at the 99th percentile for T-101's revenue metric. Which data should set the cap?

- A. Order values from both arms pooled, or from history before the test
- B. Order values of the control arm only
- C. Each arm's own 99th percentile
- D. Whichever cap gives the smallest p-value

#### [day2#lab-2-1] Capping order value

Lab 2.1 · 25 min

Measure how capping order value changes variance and bias, using the potential outcomes the generator knows.

[D2_1_capping.ipynb](https://sdaiaacademy.github.io/ds-302/labs/D2_1_capping.ipynb)

- [ ] Where the variance of revenue comes from (5 min)
- [ ] Cap at the pooled 99th and 99.9th percentiles (5 min)
- [ ] Effect and standard error under each cap (6 min)
- [ ] Bias against the true uncapped effect (5 min)
- [ ] Choose a cap and write the reason (4 min)
- [ ] ✱ Stretch: Cap per customer instead of per order and compare

### Session 2: Regression adjustment

#### [day2#s2] Regression adjustment

*Session 2*

- Estimate the CUPED coefficient from pre-period data
- Compute adjusted and unadjusted intervals
- Report the variance reduction as an effective sample-size gain

#### [day2#habits-persist] Last month's orders predict this month's, whatever the arm

*The idea*

**0.85** correlation between orders in the 28 pre-period days and the 28 test days, triggered customers

- Most of the variance between customers is habit, and habit was there before the test.
- Remove what the pre-period predicts and the remaining noise is small.
- The pre-period cannot carry the effect: it ended before assignment.

#### [day2#cuped-formula] Subtract theta times the centred pre-period metric

*CUPED*

```python
# file: Lab 2.2
theta = cov(y, x) / var(x)       # both arms pooled
y_cuped = y - theta * (x - x.mean())
diff_ci(y_cuped, t)
```

- Same expected difference: the term has mean zero in each arm.
- Variance multiplied by 1 - rho²: here 0.27.
- theta = 0.864 for orders in T-101.

#### [day2#cuped-result] The interval halves; the estimate stays compatible

*Lab 2.2, full mode*

| Orders per triggered customer | Difference | Standard error | 95% interval |
| --- | --- | --- | --- |
| Unadjusted | +0.253 | 0.046 | +0.163 to +0.343 |
| Adjusted (CUPED) | +0.226 | 0.024 | +0.179 to +0.273 |

- **73%** less variance
- **3.7×** the customers an unadjusted test would need for the same precision

#### [day2#cuped-regression] Regression adjustment gives the same number to four decimals

*The same thing, as a regression*

```python
# file: Lab 2.2, step 4
d = df.assign(xc=df.orders_pre - df.orders_pre.mean())
fit = smf.ols("orders ~ treat + xc", data=d).fit(cov_type="HC2")
fit.params["treat"], fit.bse["treat"]    # 0.2261, 0.0241
```

- The regression form extends to several covariates: pre-period orders, revenue, city.
- Use robust standard errors; centre the covariate so the treatment coefficient is the average effect.

#### [day2#effective-n] Report the gain as customers: it is what the business buys

*Reporting the saving*

| Item | Value |
| --- | --- |
| Orders, 28 pre-period days | 3.7× the customers |
| Revenue, 28 pre-period days | about 1.5× |

Gain = 1 / (1 - rho²). Orders: rho = 0.85. Revenue: rho = 0.59, so 1 / (1 - 0.34) ≈ 1.5.

> **For T-101**: a revenue test that needed 55 days on Day 1 needs far fewer with capping and adjustment together.

#### [day2#check-cuped] What can go into the adjustment?

*Checkpoint*

**Question:** Ruba wants a stronger adjustment for T-101 and considers adding one more covariate to the regression. Which one is safe?

- A. Number of searches during the test
- B. Revenue during the test
- C. Day of the first search in the test
- D. Revenue in the 28 pre-period days

#### [day2#lab-2-2] Regression adjustment with 28 pre-period days

Lab 2.2 · 25 min

Adjust for pre-period behaviour and report the reduction in interval width and the effective sample-size gain.

[D2_2_cuped.ipynb](https://sdaiaacademy.github.io/ds-302/labs/D2_2_cuped.ipynb)

- [ ] The unadjusted effect and interval (4 min)
- [ ] Theta from the pooled pre-period (5 min)
- [ ] The adjusted effect and interval (6 min)
- [ ] The same with a regression (5 min)
- [ ] Variance reduction and effective sample size (5 min)
- [ ] ✱ Stretch: Use 14 pre-period days, the default of one platform, and compare

### Session 3: Ratio metrics

#### [day2#s3] Ratio metrics

*Session 3*

- Explain why a session-level interval is too narrow when customers are randomised
- Compute a delta-method interval for a ratio metric
- Check it with a bootstrap over customers

#### [day2#ratio-metrics] Orders per session: the numerator and the denominator both vary

*Ratio metrics*

- Randomised: customers. Counted: sessions and orders.
- The metric: all orders over all sessions in the arm, a ratio of two sums.
- Not the mean of each customer's own rate, which weights a one-session customer like a fifty-session one.

**0.2036 vs 0.1964** orders per session, treatment and control: +3.7%

#### [day2#naive-too-narrow] Treating sessions as independent makes the interval 2.6 times too narrow

*The trap*

| Item | Value |
| --- | --- |
| Naive, sessions as trials | ± 0.0009 |
| Delta method, by customer | ± 0.0024 |

> **Why it matters.** An interval 2.6 times too narrow turns noise into wins: the A/A test of Day 1 would show far more than 5% false wins.

#### [day2#delta-method] Compute the variance of a ratio from customer-level sums

*The delta method*

```python
# file: Lab 2.3, step 3
o, s = arm.orders, arm.sessions          # one row per customer
r = o.mean() / s.mean()
c = np.cov(o, s)
var_r = (c[0,0] - 2*r*c[0,1] + r**2*c[1,1]) / (n * s.mean()**2)
```

- A first-order Taylor expansion of mean(O) / mean(S) around its expectation.
- Every term is per customer, the unit that was randomised.

#### [day2#bootstrap-check] A bootstrap over customers agrees within 4%

*The check*

| Method | Standard error | 95% interval of the difference |
| --- | --- | --- |
| Naive, sessions | 0.00048 | +0.0063 to +0.0081 |
| Delta method | 0.00124 | +0.0048 to +0.0096 |
| Bootstrap, 1,000 resamples of customers | 0.00120 | +0.0048 to +0.0095 |

Poisson bootstrap: each customer gets a weight from Poisson(1), all their sessions and orders with it.

#### [day2#check-ratio] Which interval is right for clicks per view?

*Checkpoint*

**Question:** A test randomises customers and reports clicks per page view: 1.9 million views, 80,000 customers. Which standard error should the analysis use?

- A. The binomial standard error over 1.9 million views
- B. A delta-method standard error over the 80,000 customers
- C. The standard error of the mean of each customer's click rate
- D. A bootstrap that resamples page views

#### [day2#lab-2-3] Orders per session: delta method and bootstrap

Lab 2.3 · 25 min

Compute a delta-method interval for orders per session and check it by a bootstrap over customers.

[D2_3_delta_method.ipynb](https://sdaiaacademy.github.io/ds-302/labs/D2_3_delta_method.ipynb)

- [ ] Orders per session in each arm (3 min)
- [ ] The naive interval, sessions as independent (5 min)
- [ ] The delta-method interval (7 min)
- [ ] A bootstrap over customers (6 min)
- [ ] Two agreeing intervals and why the naive one is narrow (4 min)
- [ ] ✱ Stretch: Compute the interval for the relative difference

### Session 4: Stratification

#### [day2#s4] Stratification

*Session 4*

- Distinguish stratified assignment from post-stratification
- Compute a post-stratified estimate and its standard error
- Judge when strata help and when pre-period data helps more

#### [day2#two-ways-strata] Use the strata in the design, or in the analysis

*Stratification*

- **Stratified assignment.** Randomise 50/50 inside each city. The arms cannot differ in their city mix.
- **Post-stratification.** Randomise simply, then estimate city by city and weight by each city's share.

Both remove the noise that comes from differences between cities. Neither can remove more than the cities explain.

#### [day2#post-strat-formula] Estimate per city, weight by each city's share

*Lab 2.4, step 3*

```python
# file: post_strat
g = d.groupby(["city", "treat"]).orders.agg(["mean", "var", "size"]).unstack("treat")
w = (g["size"][0] + g["size"][1]) / len(d)
est = (w * (g["mean"][1] - g["mean"][0])).sum()
se = sqrt((w**2 * (g["var"][1]/g["size"][1] + g["var"][0]/g["size"][0])).sum())
```

#### [day2#cities-differ] Cities differ in their means, and explain 1.2% of the variance

*Lab 2.4, step 1*

| Item | Value |
| --- | --- |
| Riyadh | 7.36 |
| Jeddah | 6.90 |
| Dammam | 6.39 |
| Makkah | 5.87 |
| Madinah | 5.63 |
| Abha | 5.09 |

Orders per triggered customer in the test period. The spread inside each city (standard deviations of 5 to 7.4) dwarfs the spread between them.

#### [day2#strata-result] City strata buy almost nothing; pre-period strata buy a lot

*Lab 2.4, full mode*

| Estimator, orders per triggered customer | Estimate | Standard error |
| --- | --- | --- |
| Simple difference | +0.253 | 0.046 |
| Post-stratified by city | +0.258 | 0.046 |
| Post-stratified by pre-period deciles | +0.227 | 0.028 |
| CUPED, pre-period orders (Lab 2.2) | +0.226 | 0.024 |

On a 3,000-customer pilot repeated 1,000 times, city post-stratification cut the variance by 1.3%.

#### [day2#check-strata] When does stratifying by city pay off?

*Checkpoint*

**Question:** Sufrah plans a 2,000-customer pilot in two cities whose customers order at very different rates. Which design reduces the variance of the estimate most?

- A. A simple 50/50 randomisation, analysed as a simple difference
- B. Strata for every district, analysed per district
- C. Randomisation within each city, analysed with the city strata
- D. A separate test in each city, reported side by side

#### [day2#lab-2-4] City strata in the search test

Lab 2.4 · 25 min

Estimate a city-stratified test with and without post-stratification, on the full test and on a small pilot.

[D2_4_stratification.ipynb](https://sdaiaacademy.github.io/ds-302/labs/D2_4_stratification.ipynb)

- [ ] Orders by city: how much the cities differ (4 min)
- [ ] The simple difference and its standard error (4 min)
- [ ] The post-stratified estimate and standard error (7 min)
- [ ] A 3,000-customer pilot, 1,000 times (6 min)
- [ ] When strata help: write two sentences (4 min)
- [ ] ✱ Stretch: Stratify on deciles of pre-period orders and compare with Lab 2.2

#### [day2#wrap-up] Three things to keep

*Day 2*

- **Cap, and say so.** A pooled cap trades a small, stated bias for less noise.
- **Use the pre-period.** Regression adjustment halved T-101's interval: 3.7 times the customers for free.
- **Respect the unit.** Compute every interval over the unit that was randomised.

#### [day2#next] Next: watching tests every day, and tests where customers share couriers

*Day 3*

- Why daily peeking invents wins, and two ways to look safely
- A dispatch test whose customer-randomised result is mostly stealing
- City-by-hour switchbacks and their power

## Day 3: Monitoring and interference

Watch a test every day without inventing wins, and test a marketplace where customers share couriers

#### [day3#title] Monitoring and interference

*SDAIA Academy · Online Experiments and A/B Testing*

Day 3: Watch a test every day without inventing wins, and test a marketplace where customers share couriers

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-302

#### [day3#agenda] Monitoring and interference

*Today*

- **Session 1 · Group sequential designs**: Looking every day and stopping at the first p below 0.05 inflates false wins; spending alpha across looks does not
- **Session 2 · Always-valid tests**: A test that stays valid at every look, whenever you stop, at a price in power
- **Session 3 · Interference in marketplaces**: When treated and control customers share couriers, a customer-randomised test measures stealing, not the change
- **Session 4 · Cluster and switchback designs**: Randomise what shares the couriers, city by hour, and pay for it in power

#### [day3#review-day2] Which change narrows T-101's interval without changing the estimand?

*Review of Day 2*

**Question:** Ruba must narrow the interval of revenue per triggered customer in T-101 and keep estimating exactly the effect on revenue. Which method does that?

- A. Capping each order at the 99th percentile
- B. Regression adjustment on revenue in the 28 pre-period days
- C. Dropping the customers with the largest orders
- D. Switching to revenue per order

### Session 1: Group sequential designs

#### [day3#s1] Group sequential designs

*Session 1*

- Measure the false-positive rate of daily peeking by simulation
- Compute boundaries from an alpha-spending function
- Report the false-positive rate, power and expected stopping day of a group sequential test

#### [day3#peeking-cost] Stopping at the first p below 0.05 gives 28% false wins

*Lab 3.1, step 1*

**28.1%** of 4,000 simulated tests with no effect cross 1.96 on at least one of 28 daily looks

- Each look is another chance for noise to cross the line.
- The daily z values are correlated, so the rate is not 1 - 0.95²⁸, but it is still far above 5%.
- The fixed test, one look on day 28: 5.3%.

#### [day3#alpha-spending] Spend the 5% across the looks, on a schedule fixed in advance

*The idea*

```python
# file: Lan-DeMets, O'Brien-Fleming type
def obf(t, alpha=0.05):   # t: share of the plan
    z = norm.ppf(1 - alpha / 2)
    return 2 - 2 * norm.cdf(z / sqrt(t))
```

| Day | Alpha spent |
| --- | --- |
| 7 | 0.0001 |
| 14 | 0.0056 |
| 21 | 0.0236 |
| 28 | 0.0500 |

Almost nothing early, when the data is thin; nearly all at the end.

#### [day3#boundaries-by-simulation] Compute each day's boundary by simulation

*Lab 3.1, step 3*

1. Simulate 40,000 tests with no effect.
2. At day k, among tests not yet stopped, find the |z| that stops exactly the alpha spent at day k, as a share of all tests.
3. Stop those tests; move to day k + 1.

| Item | Value |
| --- | --- |
| Day 7 | 3.80 |
| Day 14 | 2.91 |
| Day 21 | 2.44 |
| Day 28 | 2.14 |

#### [day3#gst-result] Five percent false wins, nearly the same power, a week saved

*Lab 3.1, full mode, fresh simulations*

| Design | False-positive rate | Power, true lift 1.6% | Mean stopping day |
| --- | --- | --- | --- |
| Fixed, one look on day 28 | 0.053 | 0.777 | 28 |
| Daily peeking at 1.96 | 0.281 | not valid | not valid |
| Group sequential, O'Brien-Fleming | 0.052 | 0.759 | 21.1 |

#### [day3#gst-rules] A group sequential plan is a contract written before day 1

*What the pre-registration fixes*

- **The looks.** How many and when, or the information fractions.
- **The spending.** O'Brien-Fleming, Pocock or another function, with alpha.
- **The maximum.** The longest the test may run: 28 days for T-101.

> **Guardrails can stop a test too.** A harm guardrail is usually monitored with its own, looser boundary: stopping for harm should be easy.

#### [day3#check-gst] Day 5: the dashboard is green

*Checkpoint*

**Question:** A 28-day test with an O'Brien-Fleming plan shows z = 2.4 on day 5. The boundary on day 5 is infinite. Yazeed wants to launch. What do you tell him?

- A. The result is significant at 5%, so launch
- B. We should not have looked at day 5 at all
- C. Keep running: the evidence has not crossed the planned boundary
- D. Switch to a Pocock plan, whose day-5 boundary is lower

#### [day3#lab-3-1] Group sequential boundaries

Lab 3.1 · 25 min

Add group sequential boundaries to the daily-peeking simulator and measure the false-positive rate and the stopping day.

[D3_1_group_sequential.ipynb](https://sdaiaacademy.github.io/ds-302/labs/D3_1_group_sequential.ipynb)

- [ ] Daily peeking with no effect: the false-win rate (4 min)
- [ ] The O'Brien-Fleming spending function (4 min)
- [ ] Boundaries by simulation, look by look (8 min)
- [ ] False-positive rate and power with the boundaries (5 min)
- [ ] Expected stopping day with a true effect (4 min)
- [ ] ✱ Stretch: Use weekly looks only and compare power and stopping day

### Session 2: Always-valid tests

#### [day3#s2] Always-valid tests

*Session 2*

- Compute a mixture sequential probability ratio statistic
- Measure its false-positive rate under daily monitoring
- Compare stopping times and power with the group sequential test

#### [day3#always-valid-idea] An always-valid test lets you look and stop at any time

*The other family*

- No plan of looks, no maximum duration.
- Its statistic is a likelihood ratio averaged over possible effects; under no effect it never drifts upward on average.
- So the chance it ever reaches 1 / alpha is at most alpha.

- **Names you will meet.** mixture SPRT (mSPRT), confidence sequences, anytime-valid inference.

#### [day3#msprt-formula] The mSPRT statistic needs the estimate, its variance and a width

*Lab 3.2, step 1*

```python
# file: msprt
v = se**2
lam = sqrt(v / (v + tau**2)) * exp(tau**2 * est**2 / (2 * v * (v + tau**2)))
stop = lam >= 1 / alpha                     # 20 for alpha = 0.05
```

- **tau**, the mixture width, says which effects the test is tuned to: here 0.08 orders, the effect we hope for.
- Platforms expose it as a tuning parameter; GrowthBook's default is 5,000 observations.

#### [day3#msprt-result] Always valid, and far less powerful on a 28-day test

*Lab 3.2, full mode*

| Design, daily looks | False-positive rate | Power | Mean stopping day |
| --- | --- | --- | --- |
| Group sequential (O'Brien-Fleming) | 0.052 | 0.759 | 21.1 |
| mSPRT, tau = 0.08 | 0.014 | 0.459 | 23.1 |
| mSPRT, tau = 0.04 | 0.004 | 0.333 | 25.5 |
| mSPRT, tau = 0.32 | 0.018 | 0.378 | 23.3 |

The always-valid test spends far less than its 5%: it is built to stay valid beyond day 28 too.

#### [day3#choose-family] Choose by what you can promise in advance

*Choosing*

| If | Use |
| --- | --- |
| The maximum duration and the looks can be fixed | Group sequential: more power for that plan |
| People will look whenever they like, and stop whenever | Always valid: the guarantee survives any behaviour |
| One look at the end is enough | The fixed test: the most power of all |

> **For the capstone.** The sequential plan names its family and gives the reason in one line.

#### [day3#check-avi] Which design for a test nobody can stop people watching?

*Checkpoint*

**Question:** The Luqma team will check results on a public dashboard several times a day and may stop at any moment. The test has no fixed end date. Which design keeps the false-win rate at 5%?

- A. A fixed test at alpha = 0.01
- B. A group sequential test with daily looks
- C. A Bonferroni correction over the expected number of looks
- D. An always-valid test such as mSPRT

#### [day3#lab-3-2] An always-valid test on the same simulator

Lab 3.2 · 25 min

Run an always-valid sequential test on the same simulator and compare its error rate and stopping times with the group sequential design.

[D3_2_always_valid.ipynb](https://sdaiaacademy.github.io/ds-302/labs/D3_2_always_valid.ipynb)

- [ ] The mSPRT statistic for a difference in means (7 min)
- [ ] False-positive rate under daily looks (5 min)
- [ ] Power and stopping day with a true effect (5 min)
- [ ] The mixture width: three values (4 min)
- [ ] One table: fixed, GST, always-valid (4 min)
- [ ] ✱ Stretch: Turn the statistic into an always-valid interval and plot it

### Session 3: Interference in marketplaces

#### [day3#s3] Interference in marketplaces

*Session 3*

- Explain how shared couriers break the no-interference assumption
- Measure the naive effect of a customer-randomised dispatch test
- Compare it with the global effect and report the bias

#### [day3#shared-couriers] In a marketplace, one customer's treatment changes another's outcome

*Interference*

1. **Treated order** Goes to the next free courier first
2. **Same couriers** Busy with treated orders
3. **Control order** Waits longer than it would without the test

> **No interference is an assumption.** A randomised comparison is unbiased only if a unit's outcome depends on its own treatment alone.

#### [day3#naive-dispatch] T-301 says treated orders arrive ten minutes sooner

*Lab 3.3, the customer-randomised test*

- **-10.4 min** delivery time, treated minus control, mean of 30 simulated runs
- **+4.4 points** conversion, orders per session

Six cities, 14 operating hours a day, 14 days. Half the customers on the new dispatch rule.

#### [day3#global-vs-naive] Run for everyone, the rule saves 1.8 minutes, not 10.4

*Lab 3.3, step 4*

| Item | Value |
| --- | --- |
| Naive, customer-randomised | -10.4 min |
| Global, all against none | -1.8 min |
| Bias | -8.6 min |

Conversion: +4.4 points naive, +0.7 global. The naive test overstates the delivery gain 5.8 times.

#### [day3#memo-part1] The memo states the claim, the real effect and why they differ

*LO5's evidence, first half*

- "The customer-randomised test showed treated orders arriving 10.4 minutes sooner. Run for everyone, the simulator gives a gain of only 1.8 minutes. The test overstated the gain by 8.6 minutes because treated and control customers share couriers: the rule moved waiting from control orders to treated ones."

From the solution of Lab 3.3, step 5, shortened. Lab 3.4 adds the design.

#### [day3#check-interference] Which Sufrah test is most at risk of interference?

*Checkpoint*

**Question:** Four tests are planned, each randomised by customer. Which result is most likely biased by interference between customers?

- A. A new wording on the checkout button
- B. A delivery-fee discount that raises orders at peak hours
- C. A dark mode for the app
- D. AI-ranked search for one customer's results

#### [day3#lab-3-3] The bias of a customer-randomised dispatch test

Lab 3.3 · 25 min

Measure the bias of a customer-randomised dispatch test in the marketplace simulator against the effect of running the change everywhere.

[D3_3_courier_interference.ipynb](https://sdaiaacademy.github.io/ds-302/labs/D3_3_courier_interference.ipynb)

- [ ] Run the customer-randomised test (4 min)
- [ ] The naive effect on delivery time and conversion (5 min)
- [ ] The global effect: all treated against none (6 min)
- [ ] The bias, over 30 runs (6 min)
- [ ] Write the first half of the memo (4 min)
- [ ] ✱ Stretch: Treat 10% of customers instead of 50% and see the bias change

### Session 4: Cluster and switchback designs

#### [day3#s4] Cluster and switchback designs

*Session 4*

- Design a city-by-hour switchback
- Estimate its effect with city and hour adjustments
- Simulate its power and the bias from carryover

#### [day3#randomise-the-cluster] Randomise what shares the couriers: the city-hour

*The fix*

- **Cluster design.** Whole cities on the new rule. Six units: hopeless power.
- **Switchback.** Each city switches between rules hour by hour, at random: 6 cities × 14 hours × 14 days = 1,176 blocks.

Inside a block every order has the same rule, so nobody jumps a queue of the other arm.

#### [day3#switchback-schedule] One random schedule: Riyadh, day 1

*Lab 3.4, step 1*

1. **Hours 1 to 3** new rule
2. **Hours 4 to 6** old rule
3. **Hours 7 to 9** new rule
4. **Hour 10** old rule
5. **Hour 11** new rule
6. **Hours 12 to 14** old rule

Each operating hour of each city and day is assigned by a coin flip; runs of the same rule happen by chance. Each city has its own schedule.

#### [day3#switchback-estimate] Estimate with city and hour fixed effects, block as the unit

*Lab 3.4, step 2*

```python
# file: estimate
fit = smf.ols("delivery_min ~ treat + C(city) + C(hour)",
              data=blocks).fit(cov_type="HC1")
fit.params["treat"], fit.bse["treat"]      # one run: -1.19, se 0.30
```

- One row per city-hour block, not per order: the block was randomised.
- Each block counts once; weight by orders when the decision is about orders.

#### [day3#switchback-power] Seven days give 95% power; the false-win rate stays near 5%

*Lab 3.4, full mode, 200 runs each*

| Days | Mean estimate (min) | Spread | Power | False wins, no effect |
| --- | --- | --- | --- | --- |
| 3 | -1.42 | 0.51 | 0.80 | 0.050 |
| 7 | -1.53 | 0.41 | 0.95 | 0.050 |
| 14 | -1.51 | 0.30 | 1.00 | 0.035 |

#### [day3#carryover] Carryover between hours is small in this simulator, so measure it

*Lab 3.4, step 4*

- Unfinished deliveries spill into the next hour, whichever rule it has.
- Measured: switchback with carryover -1.51 minutes, without -1.49.
- In a real city the spill can be larger: test two-hour blocks, or drop the first hour after each switch.

> **An honest finding.** The design choice here is the weighting, not the block length. Your marketplace may differ: simulate yours.

#### [day3#check-switchback] What is the unit of analysis in a switchback?

*Checkpoint*

**Question:** Joud's switchback randomised 1,176 city-hour blocks; they contain about 83,000 orders. Ruba computes the standard error from the 83,000 orders as independent rows. What is wrong?

- A. The block was randomised, so the standard error must be computed over blocks
- B. The estimate is biased by interference
- C. Nothing: more rows give a more precise estimate
- D. The first hour after each switch must always be dropped

#### [day3#lab-3-4] A city-by-hour switchback and its power

Lab 3.4 · 25 min

Design a city-by-hour switchback for the dispatch change and simulate its power.

[D3_4_switchback_power.ipynb](https://sdaiaacademy.github.io/ds-302/labs/D3_4_switchback_power.ipynb)

- [ ] One switchback run: blocks and arms (4 min)
- [ ] The estimate with city and hour adjustment (6 min)
- [ ] Power over 200 runs, with and without an effect (7 min)
- [ ] Carryover: the bias of one-hour blocks (4 min)
- [ ] Finish the memo: bias and power (4 min)
- [ ] ✱ Stretch: Use two-hour blocks and drop the first hour after a switch

#### [day3#wrap-up] Three things to keep

*Day 3*

- **Plan the looks.** Daily peeking gave 28% false wins; a spending plan gave 5% and stopped a week early.
- **Or pay for freedom.** Always-valid tests survive any looking, at a large cost in power over a fixed horizon.
- **Randomise what is shared.** Shared couriers made a 1.8-minute gain look like 10.4.

#### [day3#next] Next: deciding, and defending the decision

*Day 4*

- The Luqma chat-assistant test and its harm guardrail
- Twenty segments and the false wins hiding in them
- A one-page recommendation and the review board

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

## Capstone: The capstone review board

Each participant defends a design and analysis pack in ten minutes: seven to present, three for the board

#### [capstone#title] The capstone review board

*SDAIA Academy · Online Experiments and A/B Testing*

Capstone: Each participant defends a design and analysis pack in ten minutes: seven to present, three for the board

Data Science Track · 4 teaching days + capstone day · 7 min talk and demo · 3 min Q&A · DS-302

#### [capstone#agenda] How the review board runs

*Capstone*

- **The brief and final prep**: the rubric, the board's questions, a last rerun of each analysis
- **Defences**: seven minutes to present, three for the board, one participant at a time
- **Review and closing**: peer feedback, the trainer's review, what next

#### [capstone#the-brief] One AI-feature change, designed, analysed and decided

*The brief*

| Change | Goal | Harm to guard against |
| --- | --- | --- |
| C1 · AI-written dish descriptions | more orders from menus without a description | an ingredient the dish does not have |
| C2 · Luqma with an allergen checker | keep Luqma's lift without T-401's harm | a wrong ingredient or allergen answer |
| C3 · AI-ranked restaurant list | more first orders in a session | small restaurants pushed off the first screen |

The pack: pre-registration, sequential plan, trust checks, variance-reduced analysis, guardrails, one-page recommendation. Data from `sufrah.capstone_data()`; brief in `labs/capstone/README.md`.

#### [capstone#rubric] The rubric

*How packs are scored*

| Item | Value |
| --- | --- |
| Design and power | 25% |
| Analysis | 25% |
| Monitoring and guardrails | 20% |
| Recommendation | 20% |
| Reproducibility | 10% |

> **Every number reruns.** A number the board cannot regenerate from the repository scores as a claim, not a result.

#### [capstone#format] Ten minutes: seven to present, three for the board

*Format*

- **1 · The change and its risk.** Who it is for, what could go wrong, the harm guardrail. One slide.
- **2 · The design.** Unit, metrics, limits, power, the sequential plan, the rule.
- **3 · The result and the decision.** The effect with its interval, the guardrails, launch, iterate or stop.

> **Peer feedback.** After each defence, everyone writes one strength, one question and one suggestion.

#### [capstone#board-questions] One live change, then two questions

*What the board asks*

- **The live change.** The assessor changes the traffic (for example, halves it) or the pre-period (for example, 14 days in place of 28). The participant reruns the power calculation and says what can still be detected and what they would change.

- "Your harm rate is lower in treatment. Is that evidence the harm is gone?"
- "Why this spending function, not a fixed horizon?"
- "Your raw interval includes zero and the adjusted one does not. Which do you report?"
- "What would make you stop this test on day 10?"

#### [capstone#running-order] Who defends when

*Running order*

| # | Participant | Change |
| --- | --- | --- |
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |
| 4 |  |  |
| 5 |  |  |
| 6 |  |  |
| 7 |  |  |
| 8 |  |  |

#### [capstone#final-prep] Final prep · 20 minutes

*Before the first defence*

Rerun your analysis from a clean clone, rehearse once, open your repository on this screen.

#### [capstone#now-presenting] Present

*Now defending*

##### The board

#### [capstone#review] What the defences showed

*Trainer review*

- **Strongest patterns.** What several packs got right.
- **Common gaps.** What most packs would fix next.
- **One surprise.** Something nobody expected.

#### [capstone#what-next] Keep going

*After the course*

- **Follow-up task:** review one experiment from your workplace, or a public write-up, against the board's checklist of Lab 4.4.
- **Your pack stays yours:** keep it rerunnable and add the next design you named today.
- **When you cannot randomise:** DS-303 Causal Inference from Observational Data.
- **Deciding with heterogeneous effects:** DS-402 Causal Machine Learning and Policy Evaluation.

#### [capstone#thanks] Thank you

*SDAIA Academy*

Online Experiments and A/B Testing
