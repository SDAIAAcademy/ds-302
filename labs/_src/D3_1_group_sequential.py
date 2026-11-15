# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scipy>=1.13"]
# ///
# %% [markdown]
# # Lab 3.1 · Group sequential boundaries
#
# Day 3 · Session 1 (Group sequential designs) · 25 min.
#
# Sufrah's dashboard shows every test's p-value every morning, and people stop tests when it dips below 0.05.
# On the daily-peeking simulator you measure how many false wins that produces, then replace the fixed 1.96 with
# O'Brien-Fleming boundaries from an alpha-spending function, computed by simulation, and measure the
# false-positive rate, the power and the day the test stops.
#
# **AI policy: AI-tutor.** An assistant may explain alpha spending; write the boundary loop yourself.
#
# **Reference state.** `U.peek_sim()`: 28 daily looks at a test of orders per customer (mean 5.0, sd 6.0), 3,000
# new customers per arm per day, with no effect or with a true lift of 1.6%. Nothing from another lab.
#
# **Tasks**
# - [ ] 1 · Daily peeking with no effect: the false-win rate (4')
# - [ ] 2 · The O'Brien-Fleming spending function (4')
# - [ ] 3 · Boundaries by simulation, look by look (8')
# - [ ] 4 · False-positive rate and power with the boundaries (5')
# - [ ] 5 · Expected stopping day with a true effect (4')
# - [ ] ✱ Stretch · Use weekly looks only and compare power and stopping day

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
LIFT = 0.016
null, alt = U.peek_sim(0.0, seed=31), U.peek_sim(LIFT, seed=32)
print("simulations:", null["z"].shape[0], "| looks:", null["z"].shape[1])
print("fixed-horizon power at day 28:", round(float((np.abs(alt["z"][:, -1]) > 1.96).mean()), 3))

# %% [markdown]
# ## 1 · The false-win rate of daily peeking (4')
#
# ✏️ **Exercise** · Write `peek_rate(z, bound)`: the share of simulated tests whose |z| crosses `bound` at any
# look. `bound` is a number or an array with one value per look.

# %%
def peek_rate(z: np.ndarray, bound) -> float:
    # BEGIN SOLUTION
    return float((np.abs(z) >= np.broadcast_to(bound, z.shape[1])).any(axis=1).mean())
    # END SOLUTION


# %%
try:
    naive = peek_rate(null["z"], 1.96)
except NotImplementedError:
    naive = U.reference("d3_1_naive")
U.keep("d3_1_naive", naive)
print(f"stop at the first p < 0.05, 28 looks, no effect: {naive:.1%} false wins")
U.check(naive > 0.15, "daily peeking multiplies the false-win rate")

# %% [markdown]
# ## 2 · The spending function (4')
#
# An alpha-spending function says how much of the total alpha may be spent by information fraction t (here the
# share of the planned 28 days). The O'Brien-Fleming type, from Lan and DeMets:
# alpha(t) = 2 - 2 Φ(z_{1 - alpha/2} / √t). It spends almost nothing early and nearly all at the end.
#
# ✏️ **Exercise** · Write `obf(t, alpha=0.05)`.

# %%
def obf(t, alpha: float = 0.05):
    # BEGIN SOLUTION
    t = np.asarray(t, float)
    return 2 - 2 * stats.norm.cdf(stats.norm.ppf(1 - alpha / 2) / np.sqrt(t))
    # END SOLUTION


# %%
t = np.arange(1, 29) / 28
try:
    spent = obf(t)
except NotImplementedError:
    spent = np.array(U.reference("d3_1_spent"))
U.keep("d3_1_spent", spent.tolist())
print(pd.Series(spent[[0, 6, 13, 20, 27]], index=["day 1", "day 7", "day 14", "day 21", "day 28"]).round(5))
U.check(abs(spent[-1] - 0.05) < 1e-9 and np.all(np.diff(spent) >= 0), "all 5% spent by day 28, never unspent")

# %% [markdown]
# ## 3 · Boundaries by simulation (8')
#
# Simulate many null tests. At each look k, among the tests that have not stopped yet, choose the boundary c_k
# so that the share of **all** tests that stop at look k equals the alpha spent at that look,
# alpha(t_k) - alpha(t_{k-1}). Where that share is below one test, the boundary is infinite.
#
# ✏️ **Exercise** · Write `boundaries(z, spent)`.

# %%
calib = U.peek_sim(0.0, sims=U.pick(40_000, 10_000), seed=30)["z"]


def boundaries(z: np.ndarray, spent: np.ndarray) -> np.ndarray:
    # BEGIN SOLUTION
    n, looks = z.shape
    alive = np.ones(n, bool)
    c = np.full(looks, np.inf)
    increments = np.diff(np.concatenate([[0.0], spent]))
    for k in range(looks):
        to_stop = increments[k] * n
        a = np.abs(z[alive, k])
        if to_stop >= 1 and len(a):
            c[k] = np.quantile(a, 1 - to_stop / len(a))
            alive &= ~(np.abs(z[:, k]) >= c[k])
    return c
    # END SOLUTION


# %%
try:
    bounds = boundaries(calib, spent)
except NotImplementedError:
    bounds = np.array(U.reference("d3_1_bounds"), float)
U.keep("d3_1_bounds", [float(b) if np.isfinite(b) else 99.0 for b in bounds])
bounds = np.where(bounds >= 99, np.inf, bounds)
print(pd.Series(bounds, index=range(1, 29)).round(2).to_string())
fig, ax = plt.subplots()
ax.plot(range(1, 29), np.where(np.isfinite(bounds), bounds, np.nan), "o-", label="O'Brien-Fleming, by simulation")
ax.axhline(1.96, color="grey", ls="--", label="1.96 every day")
ax.set_xlabel("day"); ax.set_ylabel("|z| boundary"); ax.set_ylim(0, 8); ax.legend()
plt.show()
U.check(bounds[-1] < 2.3 and np.nanmax(bounds[np.isfinite(bounds)]) > 3, "strict early, close to 2 at the end")

# %% [markdown]
# ## 4 · False-positive rate and power (5')
#
# Check the boundaries on simulations they were not computed on.

# %%
try:
    fpr, power = peek_rate(null["z"], bounds), peek_rate(alt["z"], bounds)
except NotImplementedError:
    fpr, power = U.reference("d3_1_rates")
U.keep("d3_1_rates", [fpr, power])
band = 1.96 * np.sqrt(0.05 * 0.95 / null["z"].shape[0])
print(f"false-positive rate {fpr:.3f} (nominal 0.05 ± {band:.3f}); power {power:.3f}")
U.check(fpr <= 0.05 + band, "the false-positive rate is at or below 5%")

# %% [markdown]
# ## 5 · When does the test stop? (4')
#
# ✏️ **Exercise** · Write `stop_days(z, bound)`: for each simulated test, the first day |z| crosses the boundary,
# or 28 when it never does. Report the mean under the true effect.

# %%
def stop_days(z: np.ndarray, bound) -> np.ndarray:
    # BEGIN SOLUTION
    cross = np.abs(z) >= np.broadcast_to(bound, z.shape[1])
    return np.where(cross.any(axis=1), cross.argmax(axis=1) + 1, z.shape[1])
    # END SOLUTION


# %%
try:
    days_alt = stop_days(alt["z"], bounds)
    mean_stop = float(days_alt.mean())
except NotImplementedError:
    mean_stop = U.reference("d3_1_stop")
U.keep("d3_1_stop", mean_stop)
print(f"with a true 1.6% lift, the group sequential test stops on day {mean_stop:.1f} on average (fixed test: day 28)")
U.check(mean_stop < 28, "a true effect usually stops the test early")

# %% [markdown]
# ## ✱ Stretch · Weekly looks
#
# Look only on days 7, 14, 21 and 28: compute the spending at those four information fractions, the four
# boundaries, the power and the mean stopping day. Fewer looks spend less alpha on looking.

# %% [markdown]
# ## Checkpoint
#
# 1. Why is the O'Brien-Fleming boundary near 2 on the last day, not 1.96? <details><summary>Answer</summary>A
#    little alpha was spent on earlier looks, so the last look gets slightly less than 5%.</details>
# 2. A test crosses 1.96 on day 5 but not the day-5 boundary. What do you do? <details><summary>Answer</summary>
#    Keep running: the design says that evidence is not yet enough.</details>
# 3. What must be fixed before the test starts? <details><summary>Answer</summary>The number and timing of
#    looks (or the information fractions), the spending function and the maximum duration.</details>
#
# **Carry forward.** Lab 3.2 reads these results from `data/reference/` to compare with an always-valid test.
