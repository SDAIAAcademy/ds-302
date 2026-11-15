# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "statsmodels>=0.14", "duckdb>=1.1"]
# ///
# %% [markdown]
# # Lab 2.2 · Regression adjustment with 28 pre-period days
#
# Day 2 · Session 2 (Regression adjustment) · 25 min.
#
# A customer who ordered a lot in the 28 days before T-101 will order a lot during it, whatever the ranking.
# Removing what the pre-period predicts (CUPED, a form of regression adjustment) narrows the interval without
# changing what is estimated. You compute the adjusted effect two ways and report the saving as customers.
#
# **AI policy: AI-off for the first attempt.** Compute theta and the interval yourself first.
#
# **Reference state.** The T-101 stream: orders and revenue per triggered customer in the 28 pre-period days and
# the 28 test days. Nothing from another lab.
#
# **Tasks**
# - [ ] 1 · The unadjusted effect and interval (4')
# - [ ] 2 · Theta from the pooled pre-period (5')
# - [ ] 3 · The adjusted effect and interval (6')
# - [ ] 4 · The same with a regression (5')
# - [ ] 5 · Variance reduction and effective sample size (5')
# - [ ] ✱ Stretch · Use 14 pre-period days, the default of one platform, and compare

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
import statsmodels.formula.api as smf
import sufrah as U

pc = U.per_customer()
df = pc.loc[pc.triggered, ["customer_id", "variant", "treat", "orders", "orders_pre", "revenue", "revenue_pre"]]
df = df.reset_index(drop=True)
print(len(df), "triggered customers")
print(df.groupby("variant")[["orders_pre", "orders"]].mean().round(3))

# %% [markdown]
# The pre-period means are equal in both arms (randomisation), the test-period means are not. That is the point:
# the pre-period carries no effect, only each customer's habit.
#
# ## 1 · The unadjusted effect (4')
#
# ✏️ **Exercise** · Write `diff_ci(y, t)`: difference in means of array `y` between `t == 1` and `t == 0`, its
# standard error and 95% interval. Return a dict with `diff`, `se`, `lo`, `hi`.

# %%
def diff_ci(y: np.ndarray, t: np.ndarray) -> dict:
    # BEGIN SOLUTION
    a, b = y[t == 1], y[t == 0]
    d = a.mean() - b.mean()
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return {"diff": d, "se": se, "lo": d - 1.96 * se, "hi": d + 1.96 * se}
    # END SOLUTION


# %%
y, x, t = df.orders.to_numpy(float), df.orders_pre.to_numpy(float), df.treat.to_numpy()
try:
    raw = diff_ci(y, t)
except NotImplementedError:
    raw = U.reference("d2_2_raw")
U.keep("d2_2_raw", raw)
print({k: round(float(v), 4) for k, v in raw.items()})
U.check(raw["lo"] < raw["diff"] < raw["hi"], "an interval around the difference")

# %% [markdown]
# ## 2 · Theta (5')
#
# theta = Cov(Y, X) / Var(X), with Y the test-period metric and X the same metric in the pre-period, computed on
# **both arms pooled**. It is the slope of a regression of Y on X.
#
# ✏️ **Exercise** · Write `theta(y, x)`.

# %%
def theta(y: np.ndarray, x: np.ndarray) -> float:
    # BEGIN SOLUTION
    return float(np.cov(y, x, ddof=1)[0, 1] / np.var(x, ddof=1))
    # END SOLUTION


# %%
try:
    th = theta(y, x)
except NotImplementedError:
    th = U.reference("d2_2_theta")
U.keep("d2_2_theta", th)
rho = np.corrcoef(y, x)[0, 1]
print(f"theta = {th:.3f}; correlation of pre and test orders = {rho:.3f}")
U.check(0 < th < 2, "a positive slope: heavy orderers stay heavy")

# %% [markdown]
# ## 3 · The adjusted effect (6')
#
# Y_cuped = Y - theta (X - mean(X)). Its mean is the same as Y's in expectation in each arm, so the difference
# estimates the same effect, but its variance is (1 - rho squared) times the variance of Y.
#
# ✏️ **Exercise** · Compute `adj`: `diff_ci` of the adjusted metric.

# %%
def adjusted(y: np.ndarray, x: np.ndarray, t: np.ndarray, th: float) -> dict:
    # BEGIN SOLUTION
    return diff_ci(y - th * (x - x.mean()), t)
    # END SOLUTION


# %%
try:
    adj = adjusted(y, x, t, th)
except NotImplementedError:
    adj = U.reference("d2_2_adj")
U.keep("d2_2_adj", adj)
show = pd.DataFrame({"unadjusted": raw, "adjusted (CUPED)": adj}).T
show["width"] = show.hi - show.lo
print(show.round(4))
U.check(adj["se"] < raw["se"] and abs(adj["diff"] - raw["diff"]) < 2 * raw["se"],
        "a narrower interval around a compatible estimate")

# %% [markdown]
# ## 4 · The same with a regression (5')
#
# Regression adjustment gives the same answer: regress Y on the treatment flag and the centred pre-period metric.
# Use robust (HC2) standard errors.
#
# ✏️ **Exercise** · Fit `orders ~ treat + xc` with `smf.ols` and return the coefficient and standard error of
# `treat`.

# %%
def regression(df: pd.DataFrame) -> tuple[float, float]:
    # BEGIN SOLUTION
    d = df.assign(xc=df.orders_pre - df.orders_pre.mean())
    fit = smf.ols("orders ~ treat + xc", data=d).fit(cov_type="HC2")
    return float(fit.params["treat"]), float(fit.bse["treat"])
    # END SOLUTION


# %%
try:
    b, se_b = regression(df)
except NotImplementedError:
    b, se_b = U.reference("d2_2_regression")
U.keep("d2_2_regression", [b, se_b])
print(f"regression: {b:.4f} (se {se_b:.4f})   CUPED: {adj['diff']:.4f} (se {adj['se']:.4f})")
U.check(abs(b - adj["diff"]) < 0.25 * adj["se"] and abs(se_b / adj["se"] - 1) < 0.05, "the two agree")

# %% [markdown]
# ## 5 · The saving, in customers (5')
#
# The variance falls by a factor 1 - rho squared. Equivalently, the unadjusted test would need 1 / (1 - rho
# squared) times as many customers to be as precise: the effective sample-size gain.
#
# ✏️ **Exercise** · Fill `saving()` with `variance_reduction`, `width_reduction` and `effective_gain`.

# %%
def saving() -> dict:
    # BEGIN SOLUTION
    vr = 1 - (adj["se"] / raw["se"]) ** 2
    return {"variance_reduction": vr, "width_reduction": 1 - adj["se"] / raw["se"], "effective_gain": 1 / (1 - vr)}
    # END SOLUTION


# %%
try:
    SAVE = saving()
except NotImplementedError:
    SAVE = U.reference("d2_2_saving")
U.keep("d2_2_saving", SAVE)
print({k: round(float(v), 3) for k, v in SAVE.items()}, "| 1 - rho^2 =", round(1 - rho ** 2, 3))
print(f"The adjusted test is as precise as an unadjusted one with {SAVE['effective_gain']:.1f} times the customers.")
U.check(abs(SAVE["variance_reduction"] - rho ** 2) < 0.02, "variance reduction is about rho squared")

# %% [markdown]
# 🔍 **Look at** revenue as well: `theta(df.revenue, df.revenue_pre)`. Its pre and test correlation is lower,
# because group orders are not habits, so the saving is smaller. Capping first (Lab 2.1) raises it.
#
# ## ✱ Stretch · 14 pre-period days
#
# One open-source platform uses 14 days of pre-exposure data by default. Count each customer's orders in days
# -14 to -1 only (`U.stream()["orders"]`), redo steps 2, 3 and 5, and compare the gain with 28 days.

# %% [markdown]
# ## Checkpoint
#
# 1. Why compute theta on both arms pooled? <details><summary>Answer</summary>A theta from one arm, or one per
#    arm, can absorb part of the effect; pooled, it depends only on habits.</details>
# 2. Pre and test correlation is 0.5. What sample-size gain do you expect? <details><summary>Answer</summary>
#    1 / (1 - 0.25) = 1.33: a third more customers for free.</details>
# 3. Why must the covariate be measured before assignment? <details><summary>Answer</summary>A covariate the
#    treatment can change would carry part of the effect and bias the adjusted estimate.</details>
#
# **Carry forward.** Lab 4.3 uses this estimator for the T-101 recommendation.
