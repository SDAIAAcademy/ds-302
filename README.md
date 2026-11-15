<!-- academy:title -->
# Online Experiments and A/B Testing

التجارب عبر الإنترنت واختبارات A/B

Data Science Track · SDAIA Academy · DS-302 · Level 300

Run trustworthy online experiments, including tests of AI features, and defend a launch, iterate or stop decision with the right interval

Participants run the statistics behind an experimentation programme that includes tests of AI features. On a synthetic event stream from Sufrah, a fictional food-delivery marketplace, they check tests for trust problems, analyse triggered exposure, reduce variance with pre-experiment data, compute intervals for ratio metrics, design sequential tests for daily monitoring, set guardrails for latency, cost and harm, and measure interference through shared couriers, ending on a mock review board that decides launch, iterate or stop.

**Format:** Intensive: 4 teaching days of four sessions and a capstone day, with guided pre-work and a tracked follow-up task

**Course page:** https://sdaiaacademy.github.io/ds-302/
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
| Capstone | The capstone review board |  | [`slides/capstone.html`](slides/capstone.html) |
<!-- /academy:units -->

## Case study

**Sufrah** (سفرة) is a fictional food-delivery marketplace in six Saudi cities whose experimentation programme now tests AI features: AI-ranked search (test T-101) and Luqma (لُقمة), an in-app chat assistant (test T-401). Rawan Al-Mubarak chairs the review board, Yazeed Al-Hamdan owns search, Joud Al-Fahad runs the couriers, Waleed Al-Sharif is the data protection officer, and the participant works as Ruba Kamal, the analyst.

All data is synthetic and deterministic. `labs/sufrah.py` generates, with fixed seeds, 200,000 customers with 28 pre-period and 28 test days (about two million orders, searches and sessions), the Luqma test, a daily-peeking simulator and a marketplace simulator in which couriers are shared by treated and control customers. `labs/prepare_data.py` writes the small files the labs read: three tests with assignment logs, a data inventory, the pre-registration of T-101, twenty segment results and five experiment write-ups with seeded faults. No real person, customer or company is represented.

## How the course runs

Four teaching days of four sessions, then a capstone day. Each session is about 50 minutes: 20 to 25 minutes of ideas and demonstration, a checkpoint, then a 25-minute lab in a notebook that starts from a supplied reference state. No lab depends on another.

- **Pre-work** (two hours): power and the two-sample test, with an entry quiz. The practice page of the course site holds the questions; DS-201 and DS-205 cover the ground.
- **Assessment**: AI-off entry and exit checks on power, intervals and trust problems (20%); the capstone rubric (60%); the review-board defence (20%). Passing needs 70% overall and at least 60% on both the capstone rubric and the supervised check.
- **AI use**: no AI help in the supervised checks and in the first attempt at power and interval calculations (Labs 1.4, 2.2, 2.3 and 2.4 say so); an assistant as a tutor in the other labs, hinting without writing the analysis; full use in the capstone, which is defended live.
- **Follow-up**: review one experiment from your workplace or a public write-up against the review checklist of Lab 4.4.
- **Responsible use**: experiments are run on people. Harm guardrails (complaints, wrong-information complaints, courier earnings) sit beside business metrics, the board stops a test whose harm guardrail worsens, and Lab 1.3 decides which event data a test may use under purpose limitation.

<!-- academy:labs -->
## Labs

Every lab is a notebook in `labs/`. Open it in Google Colab from the course page, or run it locally with `uv`. Exercises raise `NotImplementedError` until they are done; the reference versions are in `labs/solutions/`.

| | Session | Lab | File |
|---|---|---|---|
| 1.1 | Day 1 · Session 1 | Triggered and diluted effects in SQL | [`D1_1_triggered_exposure.ipynb`](labs/D1_1_triggered_exposure.ipynb) |
| 1.2 | Day 1 · Session 2 | Sample ratio and A/A checks | [`D1_2_srm_aa_checks.ipynb`](labs/D1_2_srm_aa_checks.ipynb) |
| 1.3 | Day 1 · Session 3 | A metric spec for AI-ranked search | [`D1_3_ai_search_metrics.ipynb`](labs/D1_3_ai_search_metrics.ipynb) |
| 1.4 | Day 1 · Session 4 | Power by simulation for the search test | [`D1_4_power_heavy_tails.ipynb`](labs/D1_4_power_heavy_tails.ipynb) |
| 2.1 | Day 2 · Session 1 | Capping order value | [`D2_1_capping.ipynb`](labs/D2_1_capping.ipynb) |
| 2.2 | Day 2 · Session 2 | Regression adjustment with 28 pre-period days | [`D2_2_cuped.ipynb`](labs/D2_2_cuped.ipynb) |
| 2.3 | Day 2 · Session 3 | Orders per session: delta method and bootstrap | [`D2_3_delta_method.ipynb`](labs/D2_3_delta_method.ipynb) |
| 2.4 | Day 2 · Session 4 | City strata in the search test | [`D2_4_stratification.ipynb`](labs/D2_4_stratification.ipynb) |
| 3.1 | Day 3 · Session 1 | Group sequential boundaries | [`D3_1_group_sequential.ipynb`](labs/D3_1_group_sequential.ipynb) |
| 3.2 | Day 3 · Session 2 | An always-valid test on the same simulator | [`D3_2_always_valid.ipynb`](labs/D3_2_always_valid.ipynb) |
| 3.3 | Day 3 · Session 3 | The bias of a customer-randomised dispatch test | [`D3_3_courier_interference.ipynb`](labs/D3_3_courier_interference.ipynb) |
| 3.4 | Day 3 · Session 4 | A city-by-hour switchback and its power | [`D3_4_switchback_power.ipynb`](labs/D3_4_switchback_power.ipynb) |
| 4.1 | Day 4 · Session 1 | The Luqma chat-assistant test | [`D4_1_chat_assistant_test.ipynb`](labs/D4_1_chat_assistant_test.ipynb) |
| 4.2 | Day 4 · Session 2 | Twenty segment results, corrected | [`D4_2_segment_fdr.ipynb`](labs/D4_2_segment_fdr.ipynb) |
| 4.3 | Day 4 · Session 3 | A one-page recommendation for T-101 | [`D4_3_launch_recommendation.ipynb`](labs/D4_3_launch_recommendation.ipynb) |
| 4.4 | Day 4 · Session 4 | Two write-ups, and the capstone change | [`D4_4_review_board.ipynb`](labs/D4_4_review_board.ipynb) |
<!-- /academy:labs -->

## Capstone

A design and analysis pack for an AI-feature change (pre-registration, sequential plan, guardrails, variance-reduced analysis, launch recommendation) in a public repository, defended in a ten-minute review-board session

**Submission:** a link to a public GitHub repository with the pack: pre-registration, sequential plan, guardrails, the variance-reduced analysis that reruns from the generator, and the one-page recommendation. Each participant chooses one of three AI-feature changes in Lab 4.4; `labs/capstone/README.md` describes the pack, `sufrah.capstone_data()` generates its data and `labs/capstone/starter.py` writes it to CSV with a first look. In the defence the assessor changes the traffic or the pre-period and the participant reruns the power calculation live. The defence takes ten minutes: seven to present, three for the board's questions.

| Criterion | Weight |
|---|---|
| Design and power | 25 |
| Analysis | 25 |
| Monitoring and guardrails | 20 |
| Recommendation | 20 |
| Reproducibility | 10 |

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
<!-- /academy:sources -->
