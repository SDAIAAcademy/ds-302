# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scipy>=1.13", "duckdb>=1.1"]
# ///
# %% [markdown]
# # Lab 1.4 · Power by simulation for the search test
#
# Day 1 · Session 4 (Power for heavy-tailed metrics) · 25 min.
#
# How many triggered customers does T-101 need to detect a 2% lift in revenue per customer? You answer twice:
# with the two-sample formula, and by simulating the test on Sufrah's own revenue history, heavy tail included.
# Then you turn customers into weeks of traffic and compare with orders per customer.
#
# **AI policy: AI-off for the first attempt.** Compute the sample size yourself first; an assistant may review
# your code afterwards.
#
# **Reference state.** The 28 pre-period days of the T-101 stream, for the customers who search (the population
# T-101 triggers). Nothing from another lab.
#
# **Tasks**
# - [ ] 1 · Revenue per triggered customer: mean, spread, tail (4')
# - [ ] 2 · The formula: customers per arm for a 2% lift (5')
# - [ ] 3 · Power by simulation at that size (7')
# - [ ] 4 · A power curve and the size for 80% power (5')
# - [ ] 5 · Weeks of traffic needed, and the same for orders per customer (4')
# - [ ] ✱ Stretch · Repeat with a 1% lift and say whether the test is worth running

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
from scipy import stats
import sufrah as U

plt = U.style()
pc = U.per_customer()
hist = pc.loc[pc.triggered, ["revenue_pre", "orders_pre"]]
print(len(hist), "customers who search; their revenue over the 28 pre-period days is the history")

# %% [markdown]
# ## 1 · The metric's shape (4')

# %%
r = hist.revenue_pre
top = r.sort_values(ascending=False)
print(f"mean {r.mean():.1f} SAR, sd {r.std():.1f}, median {r.median():.1f}, max {r.max():,.0f}")
print(f"share of revenue from the top 1% of customers: {top.head(len(r) // 100).sum() / r.sum():.1%}")

# %% [markdown]
# ## 2 · The formula (5')
#
# For a two-sided test at level alpha with power 1 - beta and an absolute difference delta, each arm needs
# n = 2 (z_{1-alpha/2} + z_{1-beta})^2 sigma^2 / delta^2.
#
# ✏️ **Exercise** · Write `n_formula(sd, delta, alpha=0.05, power=0.8)`.

# %%
def n_formula(sd: float, delta: float, alpha: float = 0.05, power: float = 0.8) -> int:
    # BEGIN SOLUTION
    z = stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)
    return int(np.ceil(2 * z ** 2 * sd ** 2 / delta ** 2))
    # END SOLUTION


# %%
LIFT = 0.02
delta = LIFT * r.mean()
try:
    n_star = n_formula(r.std(), delta)
except NotImplementedError:
    n_star = U.reference("d1_4_n_star")
U.keep("d1_4_n_star", n_star)
print(f"formula: {n_star:,} customers per arm to detect +{LIFT:.0%} ({delta:.2f} SAR)")
U.check(50_000 < n_star < 200_000, "tens of thousands per arm, as expected for a 2% lift in revenue")

# %% [markdown]
# ## 3 · Power by simulation (7')
#
# Simulate the test many times: draw two arms of n customers from the history (with replacement), multiply
# the treatment arm by 1.02, run a Welch test, and count how often p < 0.05. This keeps the real tail.
#
# ✏️ **Exercise** · Write `sim_power(values, n, lift, sims, rng)`.

# %%
SIMS = U.pick(400, 150)
rng = np.random.default_rng(14)


def sim_power(values: np.ndarray, n: int, lift: float, sims: int, rng) -> float:
    # BEGIN SOLUTION
    hits = 0
    for _ in range(sims):
        c = rng.choice(values, n)
        t = rng.choice(values, n) * (1 + lift)
        hits += stats.ttest_ind(t, c, equal_var=False).pvalue < 0.05
    return hits / sims
    # END SOLUTION


# %%
values = r.to_numpy()
try:
    p_star = sim_power(values, n_star, LIFT, SIMS, rng)
except NotImplementedError:
    p_star = U.reference("d1_4_p_star")
U.keep("d1_4_p_star", p_star)
print(f"simulated power at n = {n_star:,}: {p_star:.2f} (formula promises 0.80; {SIMS} simulations)")
U.check(0.65 < p_star < 0.92, "simulation and formula agree within simulation error at this size")

# %% [markdown]
# ## 4 · A power curve (5')

# %%
grid = [int(n_star * f) for f in (0.25, 0.5, 0.75, 1.0, 1.25)]
try:
    curve = [sim_power(values, n, LIFT, SIMS // 2, rng) for n in grid]
except NotImplementedError:
    curve = U.reference("d1_4_curve")
U.keep("d1_4_curve", curve)
formula_curve = [stats.norm.cdf(delta / (r.std() * np.sqrt(2 / n)) - 1.96) for n in grid]
print(pd.DataFrame({"n per arm": grid, "simulated": curve, "formula": np.round(formula_curve, 3)}))
fig, ax = plt.subplots()
ax.plot(grid, curve, "o-", label="simulation")
ax.plot(grid, formula_curve, "--", label="formula")
ax.axhline(0.8, color="grey", lw=0.8)
ax.set_xlabel("customers per arm"); ax.set_ylabel("power"); ax.legend()
plt.show()
U.check(curve[-1] > curve[0], "power rises with n")

# %% [markdown]
# 🔍 **Look at** where the two curves differ. At these sizes the mean of 50,000 heavy-tailed values is close to
# normal, so the formula holds; what it hides is that its sigma came from one sample, and a sample that missed a
# few giant group orders gives a sigma, and a sample size, that are too small. Try the formula with the sd of a
# 2,000-customer subsample.
#
# ## 5 · Weeks of traffic (4')
#
# ✏️ **Exercise** · Write `days_needed(n_per_arm, triggered_per_day)` and use it for revenue and for orders
# per customer.

# %%
def days_needed(n_per_arm: int, triggered_per_day: float) -> float:
    # BEGIN SOLUTION
    return 2 * n_per_arm / triggered_per_day
    # END SOLUTION


# %%
per_day = pc.triggered.sum() / U.DAYS          # new triggered customers per day, roughly
o = hist.orders_pre
try:
    n_orders = n_formula(o.std(), LIFT * o.mean())
    d_rev, d_ord = days_needed(n_star, per_day), days_needed(n_orders, per_day)
except NotImplementedError:
    n_orders, d_rev, d_ord = U.reference("d1_4_days")
U.keep("d1_4_days", [n_orders, d_rev, d_ord])
print(f"revenue per customer: {n_star:,} per arm, about {d_rev:.0f} days of triggered traffic")
print(f"orders per customer:  {n_orders:,} per arm, about {d_ord:.0f} days")
U.check(d_ord < d_rev, "orders per customer needs far less traffic than revenue per customer")

# %% [markdown]
# Triggered customers do not arrive at a constant rate: most of the people who will ever search do so in the
# first days, then the rate falls. Use the day count as a lower bound, and plan whole weeks.
#
# ## ✱ Stretch · A 1% lift
#
# Repeat steps 2 and 5 for a 1% lift. The sample size quadruples. Is a 28-day test of revenue worth running, or
# is the answer "use orders, and the Day 2 methods"?

# %% [markdown]
# ## Checkpoint
#
# 1. Halving the minimum detectable effect multiplies the sample size by how much? <details><summary>Answer
#    </summary>By four: n grows with 1 / delta squared.</details>
# 2. Why simulate when the formula exists? <details><summary>Answer</summary>The simulation uses the metric's real
#    distribution and the real analysis (capping, triggering, a sequential plan), where the formula's assumptions
#    may not hold.</details>
# 3. You size on all customers but analyse triggered ones. What goes wrong? <details><summary>Answer</summary>The
#    sigma, the mean and the traffic all differ; the test can be badly over- or under-powered.</details>
#
# **Carry forward.** Day 2 narrows the same interval with capping, pre-period data and strata.
