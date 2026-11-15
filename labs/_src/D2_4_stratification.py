# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "duckdb>=1.1"]
# ///
# %% [markdown]
# # Lab 2.4 · City strata in the search test
#
# Day 2 · Session 4 (Stratification) · 25 min.
#
# Customers in Riyadh order more often than customers in Abha. If the arms happen to differ in their city mix,
# the difference in means carries that noise. Post-stratification estimates the effect city by city and weights
# the cities by their size. You measure what it buys on the full test, then on a 3,000-customer pilot repeated
# 1,000 times.
#
# **AI policy: AI-off for the first attempt.** Write the estimator and its standard error yourself first.
#
# **Reference state.** The T-101 stream: orders per triggered customer, with city. Nothing from another lab.
#
# **Tasks**
# - [ ] 1 · Orders by city: how much the cities differ (4')
# - [ ] 2 · The simple difference and its standard error (4')
# - [ ] 3 · The post-stratified estimate and standard error (7')
# - [ ] 4 · A 3,000-customer pilot, 1,000 times (6')
# - [ ] 5 · When strata help: write two sentences (4')
# - [ ] ✱ Stretch · Stratify on deciles of pre-period orders and compare with Lab 2.2

# %%
import os, sys, subprocess
from pathlib import Path

IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    REPO_URL = "https://github.com/SDAIAAcademy/ds-302.git"
    if not Path("/content/online-experiments").exists():
        subprocess.run(["git", "clone", "-q", REPO_URL, "/content/online-experiments"], check=True)
    os.chdir("/content/online-experiments/labs")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements-colab.txt"], check=True)
else:
    while not Path("sufrah.py").exists() and Path.cwd() != Path.cwd().parent:
        os.chdir("..")  # solutions/ notebooks run from labs/
sys.path.insert(0, os.getcwd())

import numpy as np
import pandas as pd
import sufrah as U

pc = U.per_customer()
df = pc.loc[pc.triggered, ["customer_id", "city", "treat", "orders", "revenue", "orders_pre"]].reset_index(drop=True)
print(len(df), "triggered customers")

# %% [markdown]
# ## 1 · How much the cities differ (4')
#
# The metric is the primary of T-101, orders per triggered customer.

# %%
by_city = df.groupby("city").agg(customers=("orders", "size"), mean=("orders", "mean"), sd=("orders", "std"))
by_city["share"] = by_city.customers / len(df)
print(by_city.round(3).sort_values("mean", ascending=False))
between = np.average((by_city["mean"] - df.orders.mean()) ** 2, weights=by_city.customers)
print(f"share of the variance of orders explained by city: {between / df.orders.var():.1%}")

# %% [markdown]
# ## 2 · The simple difference (4')

# %%
def simple(d: pd.DataFrame, y: str = "orders") -> tuple[float, float]:
    a, b = d.loc[d.treat == 1, y], d.loc[d.treat == 0, y]
    return a.mean() - b.mean(), float(np.sqrt(a.var() / len(a) + b.var() / len(b)))


est_s, se_s = simple(df)
print(f"simple: {est_s:.4f} (se {se_s:.4f})")

# %% [markdown]
# ## 3 · Post-stratification (7')
#
# Estimate the difference in each city, then weight by each city's share of all customers:
# effect = Σ w_c (ȳ_T,c - ȳ_C,c), with variance Σ w_c² (s²_T,c / n_T,c + s²_C,c / n_C,c).
#
# ✏️ **Exercise** · Write `post_strat(d, y)`, returning `(estimate, se)`.

# %%
def post_strat(d: pd.DataFrame, y: str = "orders") -> tuple[float, float]:
    # BEGIN SOLUTION
    g = d.groupby(["city", "treat"])[y].agg(["mean", "var", "size"]).unstack("treat")
    w = (g["size"][0] + g["size"][1]) / len(d)
    est = float((w * (g["mean"][1] - g["mean"][0])).sum())
    var = float((w ** 2 * (g["var"][1] / g["size"][1] + g["var"][0] / g["size"][0])).sum())
    return est, np.sqrt(var)
    # END SOLUTION


# %%
try:
    est_p, se_p = post_strat(df)
except NotImplementedError:
    est_p, se_p = U.reference("d2_4_post")
U.keep("d2_4_post", [est_p, se_p])
print(f"post-stratified: {est_p:.4f} (se {se_p:.4f});  se ratio to simple: {se_p / se_s:.3f}")
U.check(abs(est_p - est_s) < se_s and se_p <= se_s * 1.001, "a compatible estimate, a standard error no larger")

# %% [markdown]
# 🔍 **Look at** the ratio. With 85,000 customers the city mix of the two arms is almost identical, and city
# explains little of the variance: post-stratification changes almost nothing here.
#
# ## 4 · A small pilot, 1,000 times (6')
#
# Draw 3,000 triggered customers, randomise them 50/50, add a known effect (0.25 orders) to the treated, and
# estimate it both ways. Repeat. The spread of the estimates is their real standard error.
#
# ✏️ **Exercise** · Write `pilot(reps, rng)`: an array of shape (reps, 2) with the simple and the post-stratified
# estimate of each repetition.

# %%
REPS = U.pick(1000, 300)
rng = np.random.default_rng(24)
pool = df[df.treat == 0][["city", "orders"]].reset_index(drop=True)    # control outcomes: no effect inside


def pilot(reps: int, rng) -> np.ndarray:
    # BEGIN SOLUTION
    out = np.empty((reps, 2))
    for i in range(reps):
        d = pool.iloc[rng.choice(len(pool), 3000, replace=False)].copy()
        d["treat"] = (rng.random(3000) < 0.5).astype(int)
        d["orders"] = d.orders + 0.25 * d.treat
        out[i] = simple(d)[0], post_strat(d)[0]
    return out
    # END SOLUTION


# %%
try:
    sims = pilot(REPS, rng)
except NotImplementedError:
    sims = np.array(U.reference("d2_4_pilot"))
U.keep("d2_4_pilot", sims.tolist())
sd_simple, sd_post = sims.std(axis=0, ddof=1)
print(f"pilot of 3,000, {len(sims)} repetitions: mean estimates {sims.mean(axis=0).round(3)} (true 0.25)")
print(f"spread: simple {sd_simple:.4f}, post-stratified {sd_post:.4f}; variance reduction {1 - (sd_post / sd_simple) ** 2:.1%}")
U.check(abs(sims[:, 1].mean() - 0.25) < 4 * sd_post / np.sqrt(len(sims)), "post-stratification is unbiased")

# %% [markdown]
# ## 5 · When strata help (4')
#
# ✏️ **Exercise** · Fill `verdict()` with two sentences: when stratifying by city helps Sufrah, and what to use
# instead when it does not.

# %%
def verdict() -> str:
    # BEGIN SOLUTION
    return ("City strata help only as much as city explains the metric, here about one percent of the variance, so "
            "they buy almost nothing for Sufrah, on the full test or on a 3,000-customer pilot. Pre-period behaviour explains far more, so regression adjustment on the pre-period (Lab 2.2) is "
            "the tool to reach for; strata remain useful for a test that must report per city.")
    # END SOLUTION


# %%
try:
    VERDICT = verdict()
except NotImplementedError:
    VERDICT = U.reference("d2_4_verdict")
U.keep("d2_4_verdict", VERDICT)
print(VERDICT)
U.check(len(VERDICT) > 80, "two sentences written")

# %% [markdown]
# ## ✱ Stretch · Strata from the pre-period
#
# Replace city by deciles of `orders_pre` (`pd.qcut(df.orders_pre.rank(method="first"), 10, labels=False)`) in
# `post_strat`. Compare the standard error with city strata and with the CUPED result of Lab 2.2.

# %% [markdown]
# ## Checkpoint
#
# 1. What is the difference between stratified assignment and post-stratification? <details><summary>Answer
#    </summary>The first randomises within each stratum at the design stage; the second analyses a simple
#    randomisation stratum by stratum. Both remove between-stratum noise; the first also prevents imbalance.
#    </details>
# 2. Why weight by each city's share of all customers? <details><summary>Answer</summary>So the estimate is the
#    average effect over the whole triggered population, as the simple difference is.</details>
# 3. A stratum has 12 customers in one arm. What can go wrong? <details><summary>Answer</summary>Its variance is
#    poorly estimated and its mean noisy; merge small strata before the test.</details>
#
# **Carry forward.** Day 3 changes the unit of randomisation itself: cities and hours.
