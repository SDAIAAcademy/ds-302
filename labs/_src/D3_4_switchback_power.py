# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "statsmodels>=0.14"]
# ///
# %% [markdown]
# # Lab 3.4 · A city-by-hour switchback and its power
#
# Day 3 · Session 4 (Cluster and switchback designs) · 25 min.
#
# If customers in one city and hour share couriers, randomise the city-hour: every order in a block gets the same
# dispatch rule, so treated orders can no longer steal couriers from control orders. You design that switchback for
# T-301, estimate its effect with city and hour adjustment, simulate its power, and measure the bias that
# carryover between hours leaves.
#
# **AI policy: AI-tutor.** An assistant may explain fixed effects; the design choices are yours.
#
# **Reference state.** `U.dispatch_sim()` with `assign="switchback"`, and the global effect of the rule measured in
# Lab 3.3, supplied in `data/reference/`. You do not need to have done Lab 3.3.
#
# **Tasks**
# - [ ] 1 · One switchback run: blocks and arms (4')
# - [ ] 2 · The estimate with city and hour adjustment (6')
# - [ ] 3 · Power over 200 runs, with and without an effect (7')
# - [ ] 4 · Carryover: the bias of one-hour blocks (4')
# - [ ] 5 · Finish the memo: bias and power (4')
# - [ ] ✱ Stretch · Use two-hour blocks and drop the first hour after a switch

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

import json
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import sufrah as U

GLOBAL = U._unjson(json.loads((U.REF / f"d3_3_bias.{U.MODE}.json").read_text(encoding="utf-8")))
true_min = float(GLOBAL.loc["delivery_min", "global"])
print(f"global effect of the rule on delivery time (Lab 3.3 reference): {true_min:.2f} minutes")

# %% [markdown]
# ## 1 · One switchback run (4')
#
# 6 cities x 14 days x 14 operating hours = 1,176 blocks of one hour, each treated with probability 1/2.

# %%
run = U.dispatch_sim("switchback", seed=301)
run["treat"] = (run.arm == "treatment").astype(int)
print(len(run), "blocks;", int(run.treat.sum()), "treated")
print("Riyadh, first three days (1 = new rule):")
print(run[run.city == "Riyadh"].pivot(index="day", columns="hour", values="treat").iloc[:3].to_string())

# %% [markdown]
# ## 2 · The estimate (6')
#
# The block is the unit now. Delivery time differs a lot by city and by hour, so compare treated and control
# blocks within the same city and hour: a regression with city and hour fixed effects and robust standard errors.
#
# ✏️ **Exercise** · Write `estimate(d)`: the coefficient of `treat`, its standard error and p-value from
# `delivery_min ~ treat + C(city) + C(hour)`.

# %%
def estimate(d: pd.DataFrame) -> tuple[float, float, float]:
    # BEGIN SOLUTION
    d = d.assign(treat=(d.arm == "treatment").astype(int)).dropna(subset=["delivery_min"])
    fit = smf.ols("delivery_min ~ treat + C(city) + C(hour)", data=d).fit(cov_type="HC1")
    return float(fit.params["treat"]), float(fit.bse["treat"]), float(fit.pvalues["treat"])
    # END SOLUTION


# %%
try:
    est = estimate(run)
except NotImplementedError:
    est = U.reference("d3_4_one")
U.keep("d3_4_one", list(est))
print(f"switchback estimate: {est[0]:.2f} minutes (se {est[1]:.2f}, p = {est[2]:.3g}); global effect {true_min:.2f}")
U.check(abs(est[0] - true_min) < 4 * est[1], "the switchback lands near the global effect")

# %% [markdown]
# ## 3 · Power by simulation (7')
#
# ✏️ **Exercise** · Write `power(days, gain, runs)`: run the switchback `runs` times (seeds 5000 onwards) with
# `days` days and the batching `gain`, and return the mean estimate, its standard deviation and the share of runs
# with p < 0.05. With `gain=0` the rule has no global effect, so that share is the false-positive rate.

# %%
RUNS = U.pick(200, 60)


def power(days: int, gain: float, runs: int) -> dict:
    # BEGIN SOLUTION
    res = np.array([estimate(U.dispatch_sim("switchback", seed=5000 + s, days=days, gain=gain)) for s in range(runs)])
    return {"mean": float(res[:, 0].mean()), "sd": float(res[:, 0].std(ddof=1)), "rate": float((res[:, 2] < 0.05).mean())}
    # END SOLUTION


# %%
try:
    grid = pd.DataFrame([{"days": days, "gain": gain, **power(days, gain, RUNS)}
                         for days in (3, 7, 14) for gain in (0.04, 0.0)])
except NotImplementedError:
    grid = U.reference("d3_4_grid")
U.keep("d3_4_grid", grid)
print(grid.round(3).to_string(index=False))
null_rates = grid.loc[grid.gain == 0, "rate"]
U.check((null_rates <= 0.05 + 2 * np.sqrt(0.05 * 0.95 / RUNS)).all(), "near 5% false wins without an effect")
U.check(grid.loc[(grid.days == 14) & (grid.gain > 0), "rate"].iloc[0] > 0.8, "14 days give enough power")

# %% [markdown]
# ## 4 · Carryover (4')
#
# Wait spills into the next hour (the simulator's `carry`): a treated hour that follows a control hour inherits
# part of the control backlog, and the other way round. To isolate that bias, run the same switchback with
# `carry=0` and compare. (What remains against the global effect comes from weighting: the regression weights every
# city-hour equally, the global effect weights every order.)

# %%
sb14 = grid.loc[(grid.days == 14) & (grid.gain > 0)].iloc[0]
try:
    no_carry = float(np.mean([estimate(U.dispatch_sim("switchback", seed=7000 + s, carry=0.0))[0]
                          for s in range(RUNS // 2)]))
except NotImplementedError:
    no_carry = U.reference("d3_4_no_carry")
U.keep("d3_4_no_carry", no_carry)
carry_bias = sb14["mean"] - no_carry
print(f"switchback mean with carryover {sb14['mean']:.2f}, without {no_carry:.2f}: carryover bias {carry_bias:+.2f} "
      f"minutes ({carry_bias / no_carry:+.0%}); global effect per order {true_min:.2f}")
U.check(abs(carry_bias) < abs(no_carry) / 2, "carryover bias is small next to the effect")

# %% [markdown]
# ## 5 · The memo, second half (4')
#
# ✏️ **Exercise** · Write `memo_part2()`: the design you recommend (blocks, days), its power, its false-positive
# rate and the carryover bias, in three or four sentences.

# %%
def memo_part2() -> str:
    # BEGIN SOLUTION
    p7 = grid.loc[(grid.days == 7) & (grid.gain > 0), "rate"].iloc[0]
    p14, f14 = sb14["rate"], grid.loc[(grid.days == 14) & (grid.gain == 0), "rate"].iloc[0]
    return (f"Run T-301 again as a switchback: each city and operating hour gets the new rule or the old one at "
            f"random, analysed with city and hour fixed effects. Over 14 days its power to detect the "
            f"{-true_min:.1f}-minute gain is {p14:.0%} ({p7:.0%} over 7 days), with {f14:.0%} false wins when there is "
            f"no gain. Carryover between hours shifts the estimate by only {carry_bias:+.2f} minutes here; the larger "
            f"gap to the per-order effect ({true_min:.2f}) comes from weighting every city-hour equally, so weight "
            f"blocks by orders when the decision is about orders.")
    # END SOLUTION


# %%
try:
    MEMO2 = memo_part2()
except NotImplementedError:
    MEMO2 = U.reference("d3_4_memo")
U.keep("d3_4_memo", MEMO2)
part1 = json.loads((U.REF / f"d3_3_memo.{U.MODE}.json").read_text(encoding="utf-8"))   # Lab 3.3, supplied
U.save("T301_memo.md", "# Dispatch test T-301\n\n## What the customer-randomised test measured\n\n" + part1 +
       "\n\n## The design that can measure it\n\n" + MEMO2 + "\n")
print(MEMO2)
U.check("switchback" in MEMO2 and len(MEMO2) > 150, "the memo is complete")

# %% [markdown]
# ## ✱ Stretch · Longer blocks
#
# Run `U.dispatch_sim("switchback", block_hours=2)` and repeat steps 3 and 4. Then drop, in the estimate, the
# first hour of each block (the hour that inherits the other arm's backlog). Which design would you pre-register?

# %% [markdown]
# ## Checkpoint
#
# 1. What does a switchback give up for removing interference? <details><summary>Answer</summary>Power: 1,176
#    blocks instead of hundreds of thousands of orders, and outcomes that vary a lot between hours.</details>
# 2. Why adjust for city and hour? <details><summary>Answer</summary>They explain most of the variance between
#    blocks; comparing treated and control blocks within them removes it.</details>
# 3. Where does carryover come from here? <details><summary>Answer</summary>Unfinished deliveries: the backlog of
#    one hour delays the next, whichever rule the next hour has.</details>
#
# **Carry forward.** The memo, `artifacts/T301_memo.md`, is LO5's evidence.
