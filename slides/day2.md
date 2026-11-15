---
course: "Online Experiments and A/B Testing"
code: "DS-302"
version: "2027.1.0"
deck: "day2"
day: 2
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-302/slides/day2.html"
---

# Online Experiments and A/B Testing

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
