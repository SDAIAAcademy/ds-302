# Online Experiments and A/B Testing: labs

## Quick start

- Google Colab: open a notebook from the course page; its first cell clones this repository.
- Locally: clone the repository, then open the notebooks in `labs/` with Jupyter.

| Unit | Session | Notebook |
|---|---|---|
| Day 1 | Session 1 · Assignment, exposure and triggering | [`D1_1_triggered_exposure.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D1_1_triggered_exposure.ipynb) |
| Day 1 | Session 2 · Sample ratio mismatch and A/A tests | [`D1_2_srm_aa_checks.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D1_2_srm_aa_checks.ipynb) |
| Day 1 | Session 3 · Metrics for AI features | [`D1_3_ai_search_metrics.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D1_3_ai_search_metrics.ipynb) |
| Day 1 | Session 4 · Power for heavy-tailed metrics | [`D1_4_power_heavy_tails.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D1_4_power_heavy_tails.ipynb) |
| Day 2 | Session 1 · Variance and heavy tails | [`D2_1_capping.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D2_1_capping.ipynb) |
| Day 2 | Session 2 · Regression adjustment | [`D2_2_cuped.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D2_2_cuped.ipynb) |
| Day 2 | Session 3 · Ratio metrics | [`D2_3_delta_method.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D2_3_delta_method.ipynb) |
| Day 2 | Session 4 · Stratification | [`D2_4_stratification.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D2_4_stratification.ipynb) |
| Day 3 | Session 1 · Group sequential designs | [`D3_1_group_sequential.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D3_1_group_sequential.ipynb) |
| Day 3 | Session 2 · Always-valid tests | [`D3_2_always_valid.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D3_2_always_valid.ipynb) |
| Day 3 | Session 3 · Interference in marketplaces | [`D3_3_courier_interference.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D3_3_courier_interference.ipynb) |
| Day 3 | Session 4 · Cluster and switchback designs | [`D3_4_switchback_power.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D3_4_switchback_power.ipynb) |
| Day 4 | Session 1 · Testing AI features | [`D4_1_chat_assistant_test.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D4_1_chat_assistant_test.ipynb) |
| Day 4 | Session 2 · Many segments | [`D4_2_segment_fdr.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D4_2_segment_fdr.ipynb) |
| Day 4 | Session 3 · Writing the recommendation | [`D4_3_launch_recommendation.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D4_3_launch_recommendation.ipynb) |
| Day 4 | Session 4 · The review board | [`D4_4_review_board.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/online-experiments/blob/main/labs/D4_4_review_board.ipynb) |

The notebooks are generated from the percent-format sources in `labs/_src/` by `labs/_tools/py2nb.py` (`uv run python _tools/py2nb.py` from `labs/`), which also writes the solutions to `labs/solutions/`. Edit the sources, not the notebooks.
