# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "duckdb>=1.1"]
# ///
# %% [markdown]
# # Lab 2.3 · Orders per session: delta method and bootstrap
#
# Day 2 · Session 3 (Ratio metrics) · 25 min.
#
# Yazeed asks for "conversion": orders per session. T-101 randomised customers, not sessions, and one customer's
# sessions are alike. You compute the naive interval that treats sessions as independent, the delta-method
# interval that respects the customer, and a bootstrap over customers that checks it.
#
# **AI policy: AI-off for the first attempt.** Derive and code the delta-method variance yourself first.
#
# **Reference state.** The T-101 stream: orders and sessions per triggered customer in the test period. Nothing
# from another lab.
#
# **Tasks**
# - [ ] 1 · Orders per session in each arm (3')
# - [ ] 2 · The naive interval, sessions as independent (5')
# - [ ] 3 · The delta-method interval (7')
# - [ ] 4 · A bootstrap over customers (6')
# - [ ] 5 · Two agreeing intervals and why the naive one is narrow (4')
# - [ ] ✱ Stretch · Compute the interval for the relative difference

# %%
import os, sys, subprocess
from pathlib import Path

IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    REPO_URL = "https://github.com/SDAIAAcademy/online-experiments.git"
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
df = pc.loc[pc.triggered & (pc.sessions_test > 0), ["customer_id", "variant", "treat", "orders", "sessions_test"]]
df = df.rename(columns={"sessions_test": "sessions"}).reset_index(drop=True)
T, C = df[df.treat == 1], df[df.treat == 0]
print(len(df), "triggered customers with a session;", int(df.sessions.sum()), "sessions")

# %% [markdown]
# ## 1 · The ratio in each arm (3')
#
# The metric is a ratio of sums: all orders over all sessions in the arm. It is **not** the mean of each
# customer's own ratio, which weights a one-session customer like a fifty-session one.

# %%
r_t, r_c = T.orders.sum() / T.sessions.sum(), C.orders.sum() / C.sessions.sum()
diff = r_t - r_c
print(f"orders per session: treatment {r_t:.4f}, control {r_c:.4f}, difference {diff:+.4f} ({diff / r_c:+.1%})")

# %% [markdown]
# ## 2 · The naive interval (5')
#
# Treat every session as an independent trial that ends in an order or not: the variance of each arm's rate is
# r (1 - r) / sessions.
#
# ✏️ **Exercise** · Write `naive_se()`: the standard error of the difference under that assumption.

# %%
def naive_se() -> float:
    # BEGIN SOLUTION
    return float(np.sqrt(r_t * (1 - r_t) / T.sessions.sum() + r_c * (1 - r_c) / C.sessions.sum()))
    # END SOLUTION


# %%
try:
    se_naive = naive_se()
except NotImplementedError:
    se_naive = U.reference("d2_3_naive")
U.keep("d2_3_naive", se_naive)
print(f"naive: {diff:+.4f} ± {1.96 * se_naive:.4f}")

# %% [markdown]
# ## 3 · The delta method (7')
#
# Per arm, with n customers, orders O and sessions S per customer and R = mean(O) / mean(S):
#
# Var(R) ≈ [Var(O) - 2 R Cov(O, S) + R² Var(S)] / (n · mean(S)²)
#
# The unit in every term is the customer, the unit that was randomised.
#
# ✏️ **Exercise** · Write `delta_var(arm)` for one arm, and the standard error of the difference.

# %%
def delta_var(arm: pd.DataFrame) -> float:
    # BEGIN SOLUTION
    o, s = arm.orders.to_numpy(float), arm.sessions.to_numpy(float)
    r = o.mean() / s.mean()
    c = np.cov(o, s, ddof=1)
    return float((c[0, 0] - 2 * r * c[0, 1] + r ** 2 * c[1, 1]) / (len(o) * s.mean() ** 2))
    # END SOLUTION


# %%
try:
    se_delta = float(np.sqrt(delta_var(T) + delta_var(C)))
except NotImplementedError:
    se_delta = U.reference("d2_3_delta")
U.keep("d2_3_delta", se_delta)
print(f"delta method: {diff:+.4f} ± {1.96 * se_delta:.4f}   (naive ± {1.96 * se_naive:.4f})")
U.check(se_delta > se_naive, "the customer-level interval is wider than the naive one")

# %% [markdown]
# ## 4 · A bootstrap over customers (6')
#
# Resample **customers** with replacement, within each arm, and recompute the difference of ratios. A Poisson
# bootstrap gives each customer a weight drawn from Poisson(1), which is fast and close to resampling.
#
# ✏️ **Exercise** · Write `boot_se(B, rng)`: the standard deviation of B bootstrap differences.

# %%
B = U.pick(1000, 300)
rng = np.random.default_rng(23)


def boot_se(B: int, rng) -> float:
    # BEGIN SOLUTION
    def ratios(arm, b):
        w = rng.poisson(1.0, (b, len(arm)))
        return (w @ arm.orders.to_numpy(float)) / (w @ arm.sessions.to_numpy(float))
    diffs = []
    for start in range(0, B, 50):                       # in chunks, to keep memory small
        b = min(50, B - start)
        diffs.append(ratios(T, b) - ratios(C, b))
    return float(np.std(np.concatenate(diffs), ddof=1))
    # END SOLUTION


# %%
try:
    se_boot = boot_se(B, rng)
except NotImplementedError:
    se_boot = U.reference("d2_3_boot")
U.keep("d2_3_boot", se_boot)
table = pd.DataFrame({"se": [se_naive, se_delta, se_boot]}, index=["naive (sessions)", "delta method", "bootstrap"])
table["lo"], table["hi"] = diff - 1.96 * table.se, diff + 1.96 * table.se
print(table.round(5))
U.check(abs(se_boot / se_delta - 1) < 0.1, "bootstrap and delta method agree within 10%")

# %% [markdown]
# ## 5 · The note (4')
#
# ✏️ **Exercise** · Write `note()`: the ratio of the delta-method to the naive standard error, and one sentence on
# why the naive interval is too narrow.

# %%
def note() -> dict:
    # BEGIN SOLUTION
    return {"ratio": se_delta / se_naive,
            "why": "Sessions of one customer are alike (same habits, same conversion), so they are not independent "
                   "trials; customers were randomised, and the variance must be computed over customers."}
    # END SOLUTION


# %%
try:
    NOTE = note()
except NotImplementedError:
    NOTE = U.reference("d2_3_note")
U.keep("d2_3_note", NOTE)
print(f"the naive standard error is {NOTE['ratio']:.2f} times too small. {NOTE['why']}")
U.check(NOTE["ratio"] > 1.1, "the note gives the size of the error")

# %% [markdown]
# ## ✱ Stretch · The relative difference
#
# Decision makers ask for "+x%". The relative difference r_t / r_c - 1 is a ratio of ratios: apply the delta
# method again (Var(r_t / r_c) ≈ Var(r_t) / r_c² + r_t² Var(r_c) / r_c⁴), and check it with the same bootstrap.

# %% [markdown]
# ## Checkpoint
#
# 1. A test randomises customers and reports clicks per page view with a binomial interval. What is wrong?
#    <details><summary>Answer</summary>Page views of one customer are not independent: the interval is too narrow
#    and false wins too frequent.</details>
# 2. When does the naive interval come out right? <details><summary>Answer</summary>When the unit of analysis is
#    the unit of randomisation, for example sessions randomised one by one.</details>
# 3. Why bootstrap customers, not sessions? <details><summary>Answer</summary>The bootstrap must copy how the data
#    was produced: customers were drawn and randomised, and each brings all their sessions.</details>
#
# **Carry forward.** The Luqma analysis in Lab 4.1 reports per-customer metrics for the same reason.
