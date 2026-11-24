"""The persistent-holdout example of Day 4, session 1 (slides holdout-idea and holdout-read) and
its practice question (holdout-report).

Run from labs/:  uv run python _tools/holdout_example.py

Sufrah keeps 10% of its customers on the experience of the start of a quarter for six months.
Every feature that won its 14-day test ships to the other 90%. Each feature has a settled effect
and a novelty effect that fades; the script runs each feature's 14-day test, then reads the
holdout month by month with the 28 days before the quarter as the pre-period (CUPED, Lab 2.2).
A month is 30 days. Everything is synthetic, from fixed seeds; no lab reads this file.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sufrah as U  # noqa: E402

Z = 1.959964


def effect(t, settled, novelty, tau):
    """Relative effect of one feature on day t after its launch (0 before it)."""
    t = np.asarray(t, dtype=float)
    return np.where(t >= 0, settled + novelty * np.exp(-np.maximum(t, 0) / tau), 0.0)


def multiplier(days, features, launched):
    """Mean of the product of (1 + effect) over the given days, for a group with these features."""
    m = np.ones(len(days))
    for (name, launch, s, nov, tau), on in zip(features, launched):
        if on:
            m *= 1 + effect(days - launch, s, nov, tau)
    return m.mean()


def cuped(y, x, treat):
    """Relative difference (treated over control) adjusted with x, and its 95% interval."""
    theta = np.cov(x, y)[0, 1] / np.var(x, ddof=1)
    ya = y - theta * (x - x.mean())
    a, b = ya[treat], ya[~treat]
    d = a.mean() - b.mean()
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    base = y[~treat].mean()
    return d / base, (d - Z * se) / base, (d + Z * se) / base, se / base


def run(features, holdout_share, seed, label):
    C = U.customers(200_000)
    rate = C["_sessions_per_day"].to_numpy() * C["_conv"].to_numpy()
    n = len(rate)
    rng = np.random.default_rng(seed)
    print(f"\n== {label}: {n:,} customers, holdout {holdout_share:.0%} ==")

    # 1. Each feature's 14-day test, 50/50 on everyone outside the holdout's later reading
    wins = []
    for i, (name, launch, s, nov, tau) in enumerate(features):
        days = np.arange(launch - 14, launch)          # the test runs in the 14 days before launch
        treat = rng.random(n) < 0.5
        earlier = [j < i for j in range(len(features))]
        base = multiplier(days, features, earlier)
        # the feature's own effect during its test: days since the test started
        own = np.mean(1 + effect(np.arange(14), s, nov, tau))
        x = rng.poisson(rate * 28)
        y = rng.poisson(rate * 14 * base * np.where(treat, own, 1.0))
        rel, lo, hi, _ = cuped(y.astype(float), x.astype(float), treat)
        wins.append(rel)
        print(f"  {name:<28} 14-day test {rel:+.1%} (95% {lo:+.1%} to {hi:+.1%});"
              f" settled {s:+.1%}")
    print(f"  sum of the test wins          {sum(wins):+.1%};"
          f" sum of the settled effects {sum(f[2] for f in features):+.1%}")

    # 2. The holdout, read month by month against the 28 days before the quarter
    hold = rng.random(n) < holdout_share
    print(f"  holdout {hold.sum():,} customers, launched group {(~hold).sum():,}")
    x = rng.poisson(rate * 28).astype(float)
    every = [True] * len(features)
    for m in range(6):
        days = np.arange(30 * m, 30 * (m + 1))
        mult = multiplier(days, features, every)
        y = rng.poisson(rate * 30 * np.where(hold, 1.0, mult)).astype(float)
        rel, lo, hi, se = cuped(y, x, ~hold)
        print(f"  month {m + 1}: launched over holdout {rel:+.1%} (95% {lo:+.1%} to {hi:+.1%}),"
              f" true {mult - 1:+.1%}")
    # 3. What a holdout of this size and one of 5% can detect at month 6 (80% power, 5% two-sided)
    for share in (holdout_share, 0.05):
        scale = np.sqrt((1 / share + 1 / (1 - share)) / (1 / holdout_share + 1 / (1 - holdout_share)))
        print(f"  detectable at month 6 with a {share:.0%} holdout: {(Z + 0.841621) * se * scale:.1%}")


if __name__ == "__main__":
    # name, launch day, settled effect, novelty at launch, novelty decay time in days (e-folding)
    MAIN = [
        ("Spice-level labels", 0, 0.006, 0.020, 10.0),
        ("Delivery-time estimates", 20, 0.004, 0.016, 10.0),
        ("Saved baskets", 45, 0.005, 0.018, 12.0),
        ("Cuisine filters", 70, 0.004, 0.016, 10.0),
    ]
    run(MAIN, 0.10, seed=901, label="Sufrah customer app, launches of one quarter")

    PARALLEL = [
        ("Loyalty stamps", 0, 0.007, 0.022, 9.0),
        ("Weekly offers screen", 30, 0.002, 0.018, 9.0),
        ("Birthday voucher", 60, 0.004, 0.015, 9.0),
    ]
    run(PARALLEL, 0.10, seed=902, label="Sufrah loyalty team, launches of a half-year")
