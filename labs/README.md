# Online Experiments and A/B Testing: labs

## Quick start

- Google Colab: open a notebook from the course page; its first cell clones this repository.
- Locally: clone the repository, then open the notebooks in `labs/` with Jupyter.

| Unit | Session | Notebook |
|---|---|---|
| Day 1 | Session 1 · Assignment, exposure and triggering | [`D1_1_trace_assignment_exposure.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D1_1_trace_assignment_exposure.ipynb) |
| Day 1 | Session 2 · Sample ratio mismatch and A/A tests | [`D1_2_run_sample_ratio.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D1_2_run_sample_ratio.ipynb) |
| Day 1 | Session 3 · Metrics for AI features | [`D1_3_define_primary_metric.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D1_3_define_primary_metric.ipynb) |
| Day 1 | Session 4 · Power for heavy-tailed metrics | [`D1_4_size_search_test.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D1_4_size_search_test.ipynb) |
| Day 2 | Session 1 · Variance and heavy tails | [`D2_1_measure_how_capping.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D2_1_measure_how_capping.ipynb) |
| Day 2 | Session 2 · Regression adjustment | [`D2_2_adjust_pre_period.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D2_2_adjust_pre_period.ipynb) |
| Day 2 | Session 3 · Ratio metrics | [`D2_3_compute_delta_method.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D2_3_compute_delta_method.ipynb) |
| Day 2 | Session 4 · Stratification | [`D2_4_estimate_city_stratified.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D2_4_estimate_city_stratified.ipynb) |
| Day 3 | Session 1 · Group sequential designs | [`D3_1_add_group_sequential.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D3_1_add_group_sequential.ipynb) |
| Day 3 | Session 2 · Always-valid tests | [`D3_2_run_always_valid.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D3_2_run_always_valid.ipynb) |
| Day 3 | Session 3 · Interference in marketplaces | [`D3_3_measure_bias_customer.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D3_3_measure_bias_customer.ipynb) |
| Day 3 | Session 4 · Cluster and switchback designs | [`D3_4_design_city_hour.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D3_4_design_city_hour.ipynb) |
| Day 4 | Session 1 · Testing AI features | [`D4_1_analyse_chat_assistant.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D4_1_analyse_chat_assistant.ipynb) |
| Day 4 | Session 2 · Many segments | [`D4_2_correct_20_segment.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D4_2_correct_20_segment.ipynb) |
| Day 4 | Session 3 · Writing the recommendation | [`D4_3_draft_one_page.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D4_3_draft_one_page.ipynb) |
| Day 4 | Session 4 · The review board | [`D4_4_decide_two_seeded.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D4_4_decide_two_seeded.ipynb) |

The notebooks are generated from the percent-format sources in `labs/_src/` by `labs/_tools/py2nb.py` (`uv run python _tools/py2nb.py` from `labs/`), which also writes the solutions to `labs/solutions/`. Edit the sources, not the notebooks.
