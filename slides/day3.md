---
course: "Online Experiments and A/B Testing"
code: "DS-302"
version: "2027.1.0"
deck: "day3"
day: 3
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-302/slides/day3.html"
---

# Online Experiments and A/B Testing

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
