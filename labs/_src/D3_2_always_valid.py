# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2"]
# ///
# %% [markdown]
# # Lab 3.2 · An always-valid test on the same simulator
#
# Day 3 · Session 2 (Always-valid tests) · 25 min.
#
# A group sequential design needs the looks planned in advance. An always-valid test stays valid however often
# you look and whenever you stop. You implement the mixture sequential probability ratio test (mSPRT) for a
# difference in means, measure its false-positive rate under daily looks, and compare its power and stopping
# day with the group sequential results of Lab 3.1.
#
# **AI policy: AI-tutor.** An assistant may explain the likelihood ratio; write the statistic yourself.
#
# **Reference state.** `U.peek_sim()` (the same simulator as Lab 3.1) and the group sequential results of
# Lab 3.1, supplied in `data/reference/`. You do not need to have done Lab 3.1.
#
# **Tasks**
# - [ ] 1 · The mSPRT statistic for a difference in means (7')
# - [ ] 2 · False-positive rate under daily looks (5')
# - [ ] 3 · Power and stopping day with a true effect (5')
# - [ ] 4 · The mixture width: three values (4')
# - [ ] 5 · One table: fixed, GST, always-valid (4')
# - [ ] ✱ Stretch · Turn the statistic into an always-valid interval and plot it

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

import json
import numpy as np
import pandas as pd
import sufrah as U

LIFT = 0.016
null, alt = U.peek_sim(0.0, seed=31), U.peek_sim(LIFT, seed=32)
ALPHA = 0.05
print("true effect under the alternative:", LIFT * null["base"], "orders per customer")

# %% [markdown]
# ## 1 · The mSPRT statistic (7')
#
# With an estimated difference d and its variance V = se², and a normal mixture of width tau over the possible
# effects, the mixture likelihood ratio against "no effect" is
#
# Λ = √(V / (V + τ²)) · exp(τ² d² / (2 V (V + τ²)))
#
# Reject, at any look, as soon as Λ ≥ 1 / alpha. Because Λ is a martingale under no effect, the chance it ever
# reaches 1 / alpha is at most alpha, however many looks.
#
# ✏️ **Exercise** · Write `msprt(est, se, tau)` returning Λ for arrays of estimates and standard errors.

# %%
def msprt(est: np.ndarray, se: np.ndarray, tau: float) -> np.ndarray:
    # BEGIN SOLUTION
    v = se ** 2
    return np.sqrt(v / (v + tau ** 2)) * np.exp(tau ** 2 * est ** 2 / (2 * v * (v + tau ** 2)))
    # END SOLUTION


# %%
TAU = 0.08          # about the effect we hope to detect, in orders per customer
try:
    lam_null = msprt(null["est"], null["se"], TAU)
    lam_alt = msprt(alt["est"], alt["se"], TAU)
except NotImplementedError:
    print("↪ using a reference implementation of the statistic")
    v = null["se"] ** 2
    f = lambda e: np.sqrt(v / (v + TAU ** 2)) * np.exp(TAU ** 2 * e ** 2 / (2 * v * (v + TAU ** 2)))
    lam_null, lam_alt = f(null["est"]), f(alt["est"])
print("Λ at day 28, first five null tests:", lam_null[:5, -1].round(2))
U.check(lam_null.shape == null["est"].shape and (lam_null > 0).all(), "one Λ per test and day")

# %% [markdown]
# ## 2 · False-positive rate under daily looks (5')

# %%
def rate_and_stop(lam: np.ndarray) -> tuple[float, float]:
    cross = lam >= 1 / ALPHA
    stop = np.where(cross.any(axis=1), cross.argmax(axis=1) + 1, lam.shape[1])
    return float(cross.any(axis=1).mean()), float(stop.mean())


fpr, _ = rate_and_stop(lam_null)
print(f"always-valid, 28 daily looks, no effect: {fpr:.3f} false wins (nominal at most 0.05)")
U.keep("d3_2_fpr", fpr)
U.check(fpr <= 0.05, "at or below the nominal level under daily monitoring")

# %% [markdown]
# ## 3 · Power and stopping day (5')
#
# ✏️ **Exercise** · Compute `power` (share of tests that stop for an effect) and `mean_stop` (the mean stopping
# day, 28 for tests that never stop) under the true 1.6% lift.

# %%
def power_and_stop(lam: np.ndarray) -> tuple[float, float]:
    # BEGIN SOLUTION
    return rate_and_stop(lam)
    # END SOLUTION


# %%
try:
    power, mean_stop = power_and_stop(lam_alt)
except NotImplementedError:
    power, mean_stop = U.reference("d3_2_power")
U.keep("d3_2_power", [power, mean_stop])
print(f"power {power:.3f}; mean stopping day {mean_stop:.1f}")
U.check(0 < power < 1 and mean_stop <= 28, "power and stopping day measured")

# %% [markdown]
# ## 4 · The mixture width (4')
#
# tau says which effects the test is tuned to find. Too small and it waits for a lot of data; too large and it
# loses power on realistic effects. Platforms expose this as a tuning parameter.
#
# ✏️ **Exercise** · Fill `widths` with the false-positive rate, power and mean stopping day for tau = 0.04, 0.08
# and 0.32.

# %%
def width_table() -> pd.DataFrame:
    # BEGIN SOLUTION
    rows = {}
    for tau in (0.04, 0.08, 0.32):
        f, _ = rate_and_stop(msprt(null["est"], null["se"], tau))
        p, s = rate_and_stop(msprt(alt["est"], alt["se"], tau))
        rows[tau] = {"fpr": f, "power": p, "mean_stop": s}
    return pd.DataFrame(rows).T
    # END SOLUTION


# %%
try:
    widths = width_table()
except NotImplementedError:
    widths = U.reference("d3_2_widths")
U.keep("d3_2_widths", widths)
print(widths.round(3))
U.check((widths.fpr <= 0.05).all(), "every width keeps the false-positive rate at or below 5%")

# %% [markdown]
# ## 5 · One table (4')
#
# The group sequential results come from the solution of Lab 3.1, supplied in `data/reference/`.

# %%
gst_rates = json.loads((U.REF / f"d3_1_rates.{U.MODE}.json").read_text(encoding="utf-8"))
gst_stop = json.loads((U.REF / f"d3_1_stop.{U.MODE}.json").read_text(encoding="utf-8"))
fixed_fpr = float((np.abs(null["z"][:, -1]) > 1.96).mean())
fixed_power = float((np.abs(alt["z"][:, -1]) > 1.96).mean())
table = pd.DataFrame({
    "fixed horizon, one look on day 28": [fixed_fpr, fixed_power, 28.0],
    "naive daily peeking at 1.96": [float((np.abs(null["z"]) >= 1.96).any(axis=1).mean()), np.nan, np.nan],
    "group sequential (O'Brien-Fleming)": [gst_rates[0], gst_rates[1], gst_stop],
    f"always-valid (mSPRT, tau = {TAU})": [fpr, power, mean_stop],
}, index=["false-positive rate", "power", "mean stopping day"]).T
print(table.round(3))
U.check(table.iloc[3, 0] <= 0.05 and table.iloc[2, 0] <= 0.06, "both sequential designs control false wins")

# %% [markdown]
# 🔍 **Look at** the power column. The group sequential test knows its maximum of 28 days and spends its alpha
# for exactly that; the always-valid test pays for its freedom to look at any time and stop at any time.

# %% [markdown]
# ## ✱ Stretch · An always-valid interval
#
# Invert the test: at each day, the always-valid 95% interval holds every effect delta for which Λ computed on
# (d - delta) stays below 20. For a normal mixture it is d ± √((V + τ²) / τ² · V · (2 log(20) + log((V + τ²) / V))).
# Plot it with the fixed 95% interval for one simulated test.

# %% [markdown]
# ## Checkpoint
#
# 1. Why does mSPRT stay below 5% false wins with 28 looks? <details><summary>Answer</summary>Under no effect
#    the mixture likelihood ratio is a martingale with mean 1, so the chance it ever reaches 20 is at most 1 in
#    20.</details>
# 2. When would you choose a group sequential design over an always-valid test? <details><summary>Answer
#    </summary>When the maximum duration and the looks can be fixed in advance: it has more power for that plan.
#    </details>
# 3. What does a larger tau do? <details><summary>Answer</summary>Tunes the test to larger effects: quicker to
#    stop on big ones, slower and less powerful on small ones.</details>
#
# **Carry forward.** The capstone's sequential plan chooses one of the two designs and says why.
