---
course: "Online Experiments and A/B Testing"
code: "DS-302"
version: "2027.2.0"
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-302/index.html"
---

# Online Experiments and A/B Testing

التجارب عبر الإنترنت واختبارات A/B

Data Science Track · 4 teaching days + capstone day · 26 hours · Level 300

Run trustworthy online experiments, including tests of AI features, and defend a launch, iterate or stop decision with the right interval

Participants run the statistics behind an experimentation programme that includes tests of AI features. On a synthetic event stream from Sufrah, a fictional food-delivery marketplace, they check tests for trust problems, analyse triggered exposure, reduce variance with pre-experiment data, compute intervals for ratio metrics, design sequential tests for daily monitoring, set guardrails for latency, cost and harm, and measure interference through shared couriers, ending on a mock review board that decides launch, iterate or stop.

**Who it is for:** Specialists. Analysts and data scientists who have completed the level 200 set or can show equivalent work: an analysis or model they built, validated and can explain.

**Format:** Intensive: 4 teaching days of four sessions and a capstone day, with guided pre-work and a tracked follow-up task

## The case study

**Sufrah.** Sufrah is a fictional food-delivery marketplace in six Saudi cities whose experimentation programme now tests AI features: AI-ranked search and Luqma, an in-app chat assistant. Participants check its tests for trust problems, size and analyse the AI-ranked search test with variance reduction and ratio intervals, monitor tests daily without inflating false wins, measure how a dispatch test is biased by shared couriers, and sit on its review board. All data is synthetic and generated with fixed seeds: 200,000 customers, about two million orders, a daily-peeking simulator and a marketplace simulator.

## The course

### Day 1: Trustworthy experiments

Slides: https://sdaiaacademy.github.io/ds-302/slides/day1.md

- **Session 1: Assignment, exposure and triggering**
  - Separate assignment, exposure and the trigger condition in an event log
  - Compute a triggered effect and the diluted overall effect from it
  - Explain why counterfactual logging keeps the control group comparable
  - [Lab 1.1: Triggered and diluted effects in SQL (25 min)](https://sdaiaacademy.github.io/ds-302/labs/D1_1_triggered_exposure.ipynb)
- **Session 2: Sample ratio mismatch and A/A tests**
  - Test a split against its plan with a chi-square test
  - Locate the cause of a mismatch by segment
  - Measure a false-positive rate with A/A reshuffles of real data
  - [Lab 1.2: Sample ratio and A/A checks (25 min)](https://sdaiaacademy.github.io/ds-302/labs/D1_2_srm_aa_checks.ipynb)
- **Session 3: Metrics for AI features**
  - Choose a primary metric that the change can move and that matters to the decision
  - Set latency, cost and harm guardrails with thresholds from baseline data
  - Decide which event data a test may use under purpose limitation and data classification
  - [Lab 1.3: A metric spec for AI-ranked search (25 min)](https://sdaiaacademy.github.io/ds-302/labs/D1_3_ai_search_metrics.ipynb)
- **Session 4: Power for heavy-tailed metrics**
  - Compute a sample size with the two-sample formula
  - Estimate power by simulation from historical data
  - Explain when the formula and the simulation disagree for a heavy-tailed metric
  - [Lab 1.4: Power by simulation for the search test (25 min)](https://sdaiaacademy.github.io/ds-302/labs/D1_4_power_heavy_tails.ipynb)

### Day 2: Precision

Slides: https://sdaiaacademy.github.io/ds-302/slides/day2.md

- **Session 1: Variance and heavy tails**
  - Measure how a few large orders drive the variance of revenue per customer
  - Cap a metric at a percentile of the pooled data
  - Report the bias and the variance a cap trades
  - [Lab 2.1: Capping order value (25 min)](https://sdaiaacademy.github.io/ds-302/labs/D2_1_capping.ipynb)
- **Session 2: Regression adjustment**
  - Estimate the CUPED coefficient from pre-period data
  - Compute adjusted and unadjusted intervals
  - Report the variance reduction as an effective sample-size gain
  - [Lab 2.2: Regression adjustment with 28 pre-period days (25 min)](https://sdaiaacademy.github.io/ds-302/labs/D2_2_cuped.ipynb)
- **Session 3: Ratio metrics**
  - Explain why a session-level interval is too narrow when customers are randomised
  - Compute a delta-method interval for a ratio metric
  - Check it with a bootstrap over customers
  - [Lab 2.3: Orders per session: delta method and bootstrap (25 min)](https://sdaiaacademy.github.io/ds-302/labs/D2_3_delta_method.ipynb)
- **Session 4: Stratification**
  - Distinguish stratified assignment from post-stratification
  - Compute a post-stratified estimate and its standard error
  - Judge when strata help and when pre-period data helps more
  - [Lab 2.4: City strata in the search test (25 min)](https://sdaiaacademy.github.io/ds-302/labs/D2_4_stratification.ipynb)

### Day 3: Monitoring and interference

Slides: https://sdaiaacademy.github.io/ds-302/slides/day3.md

- **Session 1: Group sequential designs**
  - Measure the false-positive rate of daily peeking by simulation
  - Compute boundaries from an alpha-spending function
  - Report the false-positive rate, power and expected stopping day of a group sequential test
  - [Lab 3.1: Group sequential boundaries (25 min)](https://sdaiaacademy.github.io/ds-302/labs/D3_1_group_sequential.ipynb)
- **Session 2: Always-valid tests**
  - Compute a mixture sequential probability ratio statistic
  - Measure its false-positive rate under daily monitoring
  - Compare stopping times and power with the group sequential test
  - [Lab 3.2: An always-valid test on the same simulator (25 min)](https://sdaiaacademy.github.io/ds-302/labs/D3_2_always_valid.ipynb)
- **Session 3: Interference in marketplaces**
  - Explain how shared couriers break the no-interference assumption
  - Measure the naive effect of a customer-randomised dispatch test
  - Compare it with the global effect and report the bias
  - [Lab 3.3: The bias of a customer-randomised dispatch test (25 min)](https://sdaiaacademy.github.io/ds-302/labs/D3_3_courier_interference.ipynb)
- **Session 4: Cluster and switchback designs**
  - Design a city-by-hour switchback
  - Estimate its effect with city and hour adjustments
  - Simulate its power and the bias from carryover
  - [Lab 3.4: A city-by-hour switchback and its power (25 min)](https://sdaiaacademy.github.io/ds-302/labs/D3_4_switchback_power.ipynb)

### Day 4: Decide and review

Slides: https://sdaiaacademy.github.io/ds-302/slides/day4.md

- **Session 1: Testing AI features**
  - Analyse an AI-feature test with latency, cost and harm guardrails
  - Detect novelty decay in a weekly effect
  - Apply a decision rule in which harm overrides the primary metric
  - [Lab 4.1: The Luqma chat-assistant test (25 min)](https://sdaiaacademy.github.io/ds-302/labs/D4_1_chat_assistant_test.ipynb)
- **Session 2: Many segments**
  - Compute how many false wins 20 uncorrected tests produce
  - Apply Holm and Benjamini-Hochberg corrections
  - Report the segments that survive and what that means for the decision
  - [Lab 4.2: Twenty segment results, corrected (25 min)](https://sdaiaacademy.github.io/ds-302/labs/D4_2_segment_fdr.ipynb)
- **Session 3: Writing the recommendation**
  - Compute every number the pre-registration asks for
  - Apply the written decision rule without exception
  - Write a one-page recommendation a decision maker can act on
  - [Lab 4.3: A one-page recommendation for T-101 (25 min)](https://sdaiaacademy.github.io/ds-302/labs/D4_3_launch_recommendation.ipynb)
- **Session 4: The review board**
  - Check a write-up for sample ratio mismatch, peeking and novelty
  - Decide launch, iterate or stop with a stated reason
  - Choose and scope the capstone change
  - [Lab 4.4: Two write-ups, and the capstone change (25 min)](https://sdaiaacademy.github.io/ds-302/labs/D4_4_review_board.ipynb)

### Capstone: The capstone review board

Slides: https://sdaiaacademy.github.io/ds-302/slides/capstone.md

## Capstone

A design and analysis pack for an AI-feature change (pre-registration, sequential plan, guardrails, variance-reduced analysis, launch recommendation) in a public repository, defended in a ten-minute review-board session

**What you submit:** A link to a public GitHub repository with the pack: pre-registration, sequential plan, guardrails, the variance-reduced analysis that reruns from the generator, and the one-page recommendation

**Rubric:**

- Design and power: 25%
- Analysis: 25%
- Monitoring and guardrails: 20%
- Recommendation: 20%
- Reproducibility: 10%

## Outcomes

- **LO1** Apply regression adjustment with pre-experiment data and report the sample-size saving, given a test with 28 days of pre-period data per customer (Applied) Evidence: unadjusted and adjusted intervals with the effective sample-size gain
- **LO2** Compute intervals for ratio metrics with the delta method and with a bootstrap over the randomisation unit, given order-level logs from a customer-randomised test (Applied) Evidence: two agreeing intervals and a note on why the naive one is too narrow
- **LO3** Implement group sequential and always-valid tests and measure their false-positive rates under daily monitoring by simulation, given a simulator with and without a true effect (Applied) Evidence: error rates at or below the nominal level, with expected stopping times
- **LO4** Design the metric set, power and decision rule for launching an AI feature, given a proposed AI-ranked search change with goals and expected traffic (Performance) Evidence: a pre-registration with guardrail thresholds, sample size and a written decision rule
- **LO5** Diagnose interference in a marketplace test and design a cluster or switchback alternative with its power, given a simulator in which treated customers take couriers from control customers (Performance) Evidence: a memo quantifying the naive bias and the power of the new design
- **LO6** Review experiment write-ups and decide launch, iterate or stop for each, given five write-ups with seeded faults such as sample ratio mismatch, peeking and novelty decay (Performance) Evidence: a review log scored against reference decisions

## Tools

- **Analysis language and notebooks:** Python with Jupyter or marimo, R with Quarto
- **Analytical SQL engine over event logs:** DuckDB, PostgreSQL
- **Statistics and simulation:** statsmodels, SciPy, NumPy
- **Experimentation platform, for comparing defaults:** GrowthBook, published documentation of a commercial platform such as Spotify Confidence

## Prerequisites

- DS-201 Statistical Inference by Simulation
- DS-205 Designing and Reading Experiments
- Writes SQL with joins and window functions over event logs
- Pre-work: two hours on power and the two-sample test, with an entry quiz (see labs/README.md)
- Setup: a laptop processor with uv, or Google Colab. No lab calls a model or downloads one. Run 00_setup_check before Day 1.

## Sources

### National references

- [Personal Data Protection Law (SDAIA)](https://sdaia.gov.sa/en/SDAIA/about/Documents/PersonalDataProtectionLaw.pdf)
- [Implementing Regulation of the Personal Data Protection Law (SDAIA)](https://sdaia.gov.sa/en/SDAIA/about/Documents/ImplementingRegulationPersonalDataProtectionLaw.pdf)
- [Data Classification Policy (National Data Management Office, SDAIA)](https://sdaia.gov.sa/en/SDAIA/about/Documents/DataClassificationPolicy.pdf)
- [AI Ethics Principles (SDAIA)](https://sdaia.gov.sa/en/SDAIA/about/Documents/ai-principles.pdf)
- [Generative AI Guidelines for Government (SDAIA)](https://sdaia.gov.sa/en/SDAIA/about/Files/GenAIGuidelinesForGovernmentENCompressed.pdf)
- [Generative AI Guidelines for the Public (SDAIA)](https://sdaia.gov.sa/en/SDAIA/about/Files/GenerativeAIPublicEN.pdf)

### Methods

- [Deng, Xu, Kohavi, Walker (2013). Improving the sensitivity of online controlled experiments by utilizing pre-experiment data (CUPED)](https://exp-platform.com/Documents/2013-02-CUPED-ImprovingSensitivityOfControlledExperiments.pdf)
- [Deng, Knoblich, Lu (2018). Applying the delta method in metric analytics](https://arxiv.org/abs/1803.06336)
- [Johari, Pekelis, Walsh. Always valid inference: bringing sequential analysis to A/B testing](https://arxiv.org/abs/1512.04922)
- [Bojinov, Simchi-Levi, Zhao. Design and analysis of switchback experiments](https://arxiv.org/abs/2009.00148)
- [Kohavi, Tang, Xu. Trustworthy Online Controlled Experiments (the book's site)](https://experimentguide.com/)

### Platforms and libraries

- [GrowthBook documentation: CUPED](https://docs.growthbook.io/statistics/cuped)
- [GrowthBook documentation: sequential testing](https://docs.growthbook.io/statistics/sequential)
- [GrowthBook documentation: multiple testing corrections](https://docs.growthbook.io/statistics/multiple-corrections)
- [Spotify Engineering (2023). Choosing a sequential testing framework](https://engineering.atspotify.com/2023/03/choosing-sequential-testing-framework-comparisons-and-discussions)
- [statsmodels: multipletests](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html)
- [SciPy: scipy.stats.chisquare](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chisquare.html)
- [DuckDB documentation](https://duckdb.org/docs/stable/)

---

SDAIA Academy · Data Science Track · Online Experiments and A/B Testing

Course version 2027.2.0 · engine 1.0.0 · built 2026-11-24 · commit f479981
