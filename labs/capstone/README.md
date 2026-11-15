# Capstone · A design and analysis pack for one AI-feature change at Sufrah

The capstone is individual. You take **one of three AI-feature changes** that Sufrah's teams want to test, design
its experiment, analyse it on the course's synthetic data and recommend launch, iterate or stop. You publish the
pack in a **public repository**. Then you defend it before a review board in **ten minutes: seven to present,
three for the board's questions**. During the defence the assessor changes the traffic or the pre-period and you
rerun your power calculation live.

You chose the change in Lab 4.4 (`artifacts/capstone_choice.json`). The three changes are in
`data/capstone_changes.json`:

| Change | Owner | Goal | Customers | Harm to guard against |
|---|---|---|---|---|
| C1 · AI-written dish descriptions | Yazeed Al-Hamdan | more orders from menus that had no description | 160,000 | a description that names an ingredient the dish does not have |
| C2 · Luqma with an allergen checker | Rawan Al-Mubarak | keep Luqma's lift without the wrong-information complaints of T-401 | 120,000 | a wrong ingredient or allergen answer |
| C3 · AI-ranked restaurant list on the home page | Yazeed Al-Hamdan | more first orders in a session | 200,000 | small restaurants pushed off the first screen |

Use the course's synthetic data only. No personal data and no data from your workplace.

## The data

`sufrah.capstone_data(change, seed=None, n=None, pre_days=28)` generates the test, and reruns identically for the same arguments:

- `customers`: one row per customer with `city`, `variant`, `orders_pre` and `revenue_pre` (the `pre_days` before
  the test, 28 unless changed) and `orders` and `revenue` (28 days of the test);
- `daily`: new customers per day and arm, to plan the looks of a sequential design;
- `guardrails`: one row per event with `latency_ms`, `cost_sar` and `harm_flag`.

`n` is the traffic, `pre_days` the length of the pre-period and `seed` a fresh draw; in the defence the assessor
changes the traffic or the pre-period. The starter writes the data to
CSV and prints a first look:

```bash
cd labs
uv run python capstone/starter.py C2
uv run python capstone/starter.py C2 --customers 80000 --seed 7
uv run python capstone/starter.py C2 --pre-days 14
```

The first look is a starting point, not the pack: it has no limits, no plan and no decision.

## What the pack contains

1. **Pre-registration** (written before you look at the test columns): the hypothesis, the randomisation unit,
   the primary metric and its estimator, the guardrails with their limits, the harm guardrail and how it is judged,
   the sample size with its power calculation, and the written decision rule (Labs 1.3, 1.4, 4.3).
2. **Sequential plan**: the looks, the spending function and the boundaries, with the false-positive rate of the
   plan measured by simulation (Lab 3.1), or an always-valid design with your reason (Lab 3.2).
3. **Trust checks**: sample ratio, and what you would do if it failed (Lab 1.2).
4. **Variance-reduced analysis**: the primary effect with and without the pre-period adjustment, the effective
   sample-size gain, and any ratio metric with the delta method (Labs 2.2, 2.3).
5. **Guardrails**: each against its limit, with intervals where the limit is on a bound (Labs 1.3, 4.1).
6. **The one-page recommendation**: decision first, then the effect with its interval, the guardrails, the
   risks, the next step (Lab 4.3).

Every number in the pack comes from code in the repository that reruns from `capstone_data`.

## Rubric

| Criterion | Weight |
|---|---|
| Design and power | 25 |
| Analysis | 25 |
| Monitoring and guardrails | 20 |
| Recommendation | 20 |
| Reproducibility | 10 |

The capstone counts for 60% of the course result and you need at least 60% on this rubric. The review-board
defence counts for 20%, and the supervised entry and exit checks for 20%. The pass mark is 70% overall.

**AI policy.** AI-full: an assistant may write code with you. You defend every number live, including a power
calculation rerun on the traffic or the pre-period the assessor chooses.

## The defence

Seven minutes: the change and its risk, the design and its power, the result with its interval, the guardrails, the
decision. Three minutes of questions from the board, which may include:

- "Halve the traffic. What can you still detect, and what would you change?"
- "You have 14 days of pre-period data, not 28. What does the adjustment still save?"
- "The harm rate is lower in treatment. Is that evidence the harm is gone?"
- "Why this spending function and not a fixed horizon?"
