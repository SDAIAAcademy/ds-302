<!-- academy:title -->
# Online Experiments and A/B Testing

التجارب عبر الإنترنت واختبارات أ/ب

Data Science Track · SDAIA Academy · DS-302 · Level 300

REPLACE: one line under the title: what participants can do after the course

Participants run the statistics behind an experimentation programme that includes tests of AI features. On a synthetic event stream from Sufrah, a fictional food-delivery marketplace, they check tests for trust problems, analyse triggered exposure, reduce variance with pre-experiment data, compute intervals for ratio metrics, design sequential tests for daily monitoring, set guardrails for latency, cost and harm, and measure interference through shared couriers, ending on a mock review board that decides launch, iterate or stop.

**Format:** Intensive: 4 teaching days of four sessions and a capstone day, with guided pre-work and a tracked follow-up task

**Course page:** https://sdaiaacademy.github.io/online-experiments/
<!-- /academy:title -->

## Outcomes

| | Outcomes | Level | Evidence |
|---|---|---|---|
| LO1 | Apply regression adjustment with pre-experiment data and report the sample-size saving, given a test with 28 days of pre-period data per customer | Applied | unadjusted and adjusted intervals with the effective sample-size gain |
| LO2 | Compute intervals for ratio metrics with the delta method and with a bootstrap over the randomisation unit, given order-level logs from a customer-randomised test | Applied | two agreeing intervals and a note on why the naive one is too narrow |
| LO3 | Implement group sequential and always-valid tests and measure their false-positive rates under daily monitoring by simulation, given a simulator with and without a true effect | Applied | error rates at or below the nominal level, with expected stopping times |
| LO4 | Design the metric set, power and decision rule for launching an AI feature, given a proposed AI-ranked search change with goals and expected traffic | Performance | a pre-registration with guardrail thresholds, sample size and a written decision rule |
| LO5 | Diagnose interference in a marketplace test and design a cluster or switchback alternative with its power, given a simulator in which treated customers take couriers from control customers | Performance | a memo quantifying the naive bias and the power of the new design |
| LO6 | Review experiment write-ups and decide launch, iterate or stop for each, given five write-ups with seeded faults such as sample ratio mismatch, peeking and novelty decay | Performance | a review log scored against reference decisions |

<!-- academy:units -->
## Units

| Unit | Title | Sessions | Slides |
|---|---|---|---|
| Day 1 | Trustworthy experiments | Assignment, exposure and triggering; Sample ratio mismatch and A/A tests; Metrics for AI features; Power for heavy-tailed metrics | [`slides/day1.html`](slides/day1.html) |
| Day 2 | Precision | Variance and heavy tails; Regression adjustment; Ratio metrics; Stratification | [`slides/day2.html`](slides/day2.html) |
| Day 3 | Monitoring and interference | Group sequential designs; Always-valid tests; Interference in marketplaces; Cluster and switchback designs | [`slides/day3.html`](slides/day3.html) |
| Day 4 | Decide and review | Testing AI features; Many segments; Writing the recommendation; The review board | [`slides/day4.html`](slides/day4.html) |
| Capstone | Capstone project presentations |  | [`slides/capstone.html`](slides/capstone.html) |
<!-- /academy:units -->

## Case study

**REPLACE: the name of the fictional organisation every lab works on.** REPLACE: two sentences on the case study and its synthetic data

<!-- academy:labs -->
## Labs

Every lab is a notebook in `labs/`. Open it in Google Colab from the course page, or run it locally with `uv`. Exercises raise `NotImplementedError` until they are done; the reference versions are in `labs/solutions/`.

| | Session | Lab | File |
|---|---|---|---|
| 1.1 | Day 1 · Session 1 | Trace assignment and exposure in SQL and compare the triggered effect with the diluted overall effect | [`D1_1_trace_assignment_exposure.ipynb`](labs/D1_1_trace_assignment_exposure.ipynb) |
| 1.2 | Day 1 · Session 2 | Run A/A and sample ratio checks on three tests and name the faulty one | [`D1_2_run_sample_ratio.ipynb`](labs/D1_2_run_sample_ratio.ipynb) |
| 1.3 | Day 1 · Session 3 | Define a primary metric and latency, cost and harm guardrails for an AI-ranked search test | [`D1_3_define_primary_metric.ipynb`](labs/D1_3_define_primary_metric.ipynb) |
| 1.4 | Day 1 · Session 4 | Size the search test by simulation on revenue per user and compare with the textbook formula | [`D1_4_size_search_test.ipynb`](labs/D1_4_size_search_test.ipynb) |
| 2.1 | Day 2 · Session 1 | Measure how capping order value changes variance and bias | [`D2_1_measure_how_capping.ipynb`](labs/D2_1_measure_how_capping.ipynb) |
| 2.2 | Day 2 · Session 2 | Adjust for pre-period behaviour and report the reduction in interval width | [`D2_2_adjust_pre_period.ipynb`](labs/D2_2_adjust_pre_period.ipynb) |
| 2.3 | Day 2 · Session 3 | Compute a delta-method interval for orders per session and check it by bootstrap | [`D2_3_compute_delta_method.ipynb`](labs/D2_3_compute_delta_method.ipynb) |
| 2.4 | Day 2 · Session 4 | Estimate a city-stratified test with and without post-stratification | [`D2_4_estimate_city_stratified.ipynb`](labs/D2_4_estimate_city_stratified.ipynb) |
| 3.1 | Day 3 · Session 1 | Add group sequential boundaries to the daily-peeking simulator and measure the false-positive rate | [`D3_1_add_group_sequential.ipynb`](labs/D3_1_add_group_sequential.ipynb) |
| 3.2 | Day 3 · Session 2 | Run an always-valid sequential test on the same simulator and compare stopping times | [`D3_2_run_always_valid.ipynb`](labs/D3_2_run_always_valid.ipynb) |
| 3.3 | Day 3 · Session 3 | Measure the bias of a customer-randomised dispatch test | [`D3_3_measure_bias_customer.ipynb`](labs/D3_3_measure_bias_customer.ipynb) |
| 3.4 | Day 3 · Session 4 | Design a city-by-hour switchback and simulate its power | [`D3_4_design_city_hour.ipynb`](labs/D3_4_design_city_hour.ipynb) |
| 4.1 | Day 4 · Session 1 | Analyse a chat-assistant test with latency, cost and complaint guardrails | [`D4_1_analyse_chat_assistant.ipynb`](labs/D4_1_analyse_chat_assistant.ipynb) |
| 4.2 | Day 4 · Session 2 | Correct 20 segment results for false discoveries and report what survives | [`D4_2_correct_20_segment.ipynb`](labs/D4_2_correct_20_segment.ipynb) |
| 4.3 | Day 4 · Session 3 | Draft a one-page launch recommendation with effect, interval and guardrails | [`D4_3_draft_one_page.ipynb`](labs/D4_3_draft_one_page.ipynb) |
| 4.4 | Day 4 · Session 4 | Decide two seeded write-ups and choose the capstone change | [`D4_4_decide_two_seeded.ipynb`](labs/D4_4_decide_two_seeded.ipynb) |
<!-- /academy:labs -->

## Capstone

A design and analysis pack for an AI-feature change (pre-registration, sequential plan, guardrails, variance-reduced analysis, launch recommendation) in a public repository, defended in a ten-minute review-board session

**Submission:** REPLACE: what participants submit and how: a public repository link, or a shared folder for a course without code

## Prerequisites

- DS-201 Statistical Inference by Simulation
- DS-205 Designing and Reading Experiments
- Writes SQL with joins and window functions over event logs

<!-- academy:tools -->
## Tools

Each line is a capability; the examples are interchangeable.

- **Analysis language and notebooks:** Python with Jupyter or marimo, R with Quarto
- **Analytical SQL engine over event logs:** DuckDB, PostgreSQL
- **Statistics and simulation:** statsmodels, SciPy, NumPy
- **Experimentation platform, for comparing defaults:** GrowthBook, published documentation of a commercial platform such as Spotify Confidence
<!-- /academy:tools -->

<!-- academy:sources -->
## Sources

- REPLACE: every source the course cites, with its address, in course.json under "sources"; this list is written from there
<!-- /academy:sources -->

### National references

- Personal Data Protection Law and its implementing regulations: REPLACE: the address of the official text
- NDMO Data Classification Policy: REPLACE: the address of the official text
- SDAIA AI Ethics Principles: REPLACE: the address of the official text
- SDAIA Generative AI Guidelines: REPLACE: the address of the official text
