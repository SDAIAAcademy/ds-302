"""Capstone starter: generate the data for one change and print the first numbers of the pack.

Run from labs/:   uv run python capstone/starter.py C2
                  uv run python capstone/starter.py C2 --customers 80000 --seed 7
                  uv run python capstone/starter.py C2 --pre-days 14

It writes capstone/out/<change>_customers.csv, <change>_guardrails.csv and <change>_first_look.json.
Everything here is a starting point: the pack needs the pre-registration, the sequential plan and the
recommendation, which are yours to write.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sufrah as U  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("change", choices=["C1", "C2", "C3"])
ap.add_argument("--customers", type=int, default=None, help="the traffic: customers in the test")
ap.add_argument("--pre-days", type=int, default=28, help="days of pre-period data per customer")
ap.add_argument("--seed", type=int, default=None)
a = ap.parse_args()

D = U.capstone_data(a.change, seed=a.seed, n=a.customers, pre_days=a.pre_days)
cu, g = D["customers"], D["guardrails"]
out = Path(__file__).parent / "out"
out.mkdir(exist_ok=True)
cu.to_csv(out / f"{a.change}_customers.csv", index=False, lineterminator="\n")
g.to_csv(out / f"{a.change}_guardrails.csv", index=False, lineterminator="\n")

t = (cu.variant == "treatment").to_numpy()
n_c, n_t = int((~t).sum()), int(t.sum())
srm_p = float(stats.chisquare([n_c, n_t]).pvalue)


def diff_ci(y: np.ndarray) -> dict:
    a_, b_ = y[t], y[~t]
    d = a_.mean() - b_.mean()
    se = np.sqrt(a_.var(ddof=1) / len(a_) + b_.var(ddof=1) / len(b_))
    return {"diff": float(d), "lo": float(d - 1.96 * se), "hi": float(d + 1.96 * se), "rel": float(d / b_.mean())}


y, x = cu.orders.to_numpy(float), cu.orders_pre.to_numpy(float)
theta = np.cov(y, x, ddof=1)[0, 1] / np.var(x, ddof=1)
first = {
    "change": a.change,
    "customers": {"control": n_c, "treatment": n_t, "sample_ratio_p": round(srm_p, 4)},
    "pre_days": a.pre_days,
    "pre_test_correlation": round(float(np.corrcoef(x, y)[0, 1]), 3),
    "orders_per_customer_raw": diff_ci(y),
    "orders_per_customer_cuped": diff_ci(y - theta * (x - x.mean())),
    "latency_ms_p95": g.groupby("variant").latency_ms.quantile(0.95).to_dict(),
    "cost_sar_mean": g.groupby("variant").cost_sar.mean().round(5).to_dict(),
    "harm_per_1000": (g.groupby("variant").harm_flag.mean() * 1000).round(3).to_dict(),
}
(out / f"{a.change}_first_look.json").write_text(json.dumps(first, indent=1), encoding="utf-8", newline="\n")
print(json.dumps(first, indent=1))
print("\nNext: the harm guardrail needs an interval and a pre-registered limit; the sequential plan needs looks "
      "and a spending function; the recommendation follows Lab 4.3.")
