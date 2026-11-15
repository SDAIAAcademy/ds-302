# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2"]
# ///
# %% [markdown]
# # Lab 3.3 · The bias of a customer-randomised dispatch test
#
# Day 3 · Session 3 (Interference in marketplaces) · 25 min.
#
# Joud Al-Fahad, who runs Sufrah's couriers, tested a new dispatch rule (T-301) on half the customers: their
# orders go to the next free courier first, and when a whole city-hour runs the rule, batching nearby orders adds
# capacity. The test showed treated customers getting their food much faster. In the marketplace simulator you
# measure that naive effect, then the effect of running the rule everywhere, and the bias between them.
#
# **AI policy: AI-tutor.** An assistant may explain the queueing idea; the measurements are yours.
#
# **Reference state.** `U.dispatch_sim()`: six cities, 14 operating hours a day for 14 days, couriers shared by
# treated and control customers. Nothing from another lab.
#
# **Tasks**
# - [ ] 1 · Run the customer-randomised test (4')
# - [ ] 2 · The naive effect on delivery time and conversion (5')
# - [ ] 3 · The global effect: all treated against none (6')
# - [ ] 4 · The bias, over 30 runs (6')
# - [ ] 5 · Write the first half of the memo (4')
# - [ ] ✱ Stretch · Treat 10% of customers instead of 50% and see the bias change

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

# %% [markdown]
# ## 1 · The customer-randomised test (4')
#
# One row per city, day, operating hour and arm: sessions, orders, mean delivery minutes.

# %%
test = U.dispatch_sim("customer", seed=101)
print(test.head())
print(test.groupby("arm")[["sessions", "orders"]].sum())

# %% [markdown]
# ## 2 · The naive effect (5')
#
# ✏️ **Exercise** · Write `summary(d)`: conversion (orders over sessions) and mean delivery minutes weighted by
# orders, for a frame of rows. Then the naive effect is treatment minus control.

# %%
def summary(d: pd.DataFrame) -> pd.Series:
    # BEGIN SOLUTION
    ok = d.orders > 0
    return pd.Series({"conversion": d.orders.sum() / d.sessions.sum(),
                      "delivery_min": np.average(d.delivery_min[ok], weights=d.orders[ok])})
    # END SOLUTION


# %%
def naive_effect(d: pd.DataFrame) -> pd.Series:
    return summary(d[d.arm == "treatment"]) - summary(d[d.arm == "control"])


try:
    naive = naive_effect(test)
except NotImplementedError:
    naive = pd.Series(U.reference("d3_3_naive"))
U.keep("d3_3_naive", naive.to_dict())
print("naive effect (treatment minus control):", naive.round(4).to_dict())
U.check(naive["delivery_min"] < -5, "treated customers look much faster")

# %% [markdown]
# ## 3 · The global effect (6')
#
# The question the business asks is: what happens if **everyone** gets the new rule? Run the simulator with all
# orders treated and with none, and compare.
#
# ✏️ **Exercise** · Write `global_effect(seed)`: summary of `assign="all"` minus summary of `assign="none"`.

# %%
def global_effect(seed: int) -> pd.Series:
    # BEGIN SOLUTION
    return summary(U.dispatch_sim("all", seed=seed)) - summary(U.dispatch_sim("none", seed=seed + 1))
    # END SOLUTION


# %%
try:
    glob = global_effect(201)
except NotImplementedError:
    glob = pd.Series(U.reference("d3_3_global"))
U.keep("d3_3_global", glob.to_dict())
print("global effect (all minus none):", glob.round(4).to_dict())
U.check(naive["delivery_min"] < glob["delivery_min"] < 0, "the global gain is real but far smaller")

# %% [markdown]
# 🔍 **Look at** why. A priority rule does not create couriers: it moves the wait from control orders to treated
# ones. In a 50/50 test, the control arm is slower than it would be without the test, and the treated arm faster
# than it would be if everyone had the rule. Only the batching gain is real.
#
# ## 4 · The bias, over 30 runs (6')
#
# One run is noisy. Repeat both designs 30 times with different seeds and report the mean naive effect, the
# mean global effect and their difference: the bias of the customer-randomised test.
#
# ✏️ **Exercise** · Fill `bias_table(runs)`.

# %%
RUNS = U.pick(30, 10)


def bias_table(runs: int) -> pd.DataFrame:
    # BEGIN SOLUTION
    n = pd.DataFrame([naive_effect(U.dispatch_sim("customer", seed=1000 + s)) for s in range(runs)])
    g = pd.DataFrame([global_effect(2000 + 2 * s) for s in range(runs)])
    return pd.DataFrame({"naive": n.mean(), "global": g.mean(), "bias": n.mean() - g.mean(),
                         "naive_sd": n.std(), "global_sd": g.std()})
    # END SOLUTION


# %%
try:
    bias = bias_table(RUNS)
except NotImplementedError:
    bias = U.reference("d3_3_bias")
U.keep("d3_3_bias", bias)
print(bias.round(4))
ratio = bias.loc["delivery_min", "naive"] / bias.loc["delivery_min", "global"]
print(f"the naive test overstates the delivery-time gain {ratio:.1f} times")
U.check(ratio > 3, "the naive estimate is several times the real effect")

# %% [markdown]
# ## 5 · The memo, first half (4')
#
# ✏️ **Exercise** · Write `memo_part1()`: three or four sentences for Joud. What the test claimed, what running the
# rule everywhere would really do, the size of the bias, and why. Lab 3.4 writes the second half: the design.

# %%
def memo_part1() -> str:
    # BEGIN SOLUTION
    b = bias.loc["delivery_min"]
    c = bias.loc["conversion"]
    return (f"The customer-randomised test of the new dispatch rule showed treated orders arriving "
            f"{-b['naive']:.1f} minutes sooner and converting {100 * c['naive']:+.1f} points more often. Run for everyone, the "
            f"simulator gives a gain of only {-b['global']:.1f} minutes and {100 * c['global']:+.1f} points of conversion. The "
            f"test overstated the delivery gain by {-b['bias']:.1f} minutes because treated and control customers "
            f"share couriers: the rule moved waiting from control orders to treated ones, and only the batching gain "
            f"is real. A customer-randomised test cannot measure this change.")
    # END SOLUTION


# %%
try:
    MEMO1 = memo_part1()
except NotImplementedError:
    MEMO1 = U.reference("d3_3_memo")
U.keep("d3_3_memo", MEMO1)
U.save("T301_memo_part1.md", "# Dispatch test T-301: what the customer-randomised test measured\n\n" + MEMO1 + "\n")
print(MEMO1)
U.check(len(MEMO1) > 150, "the first half of the memo is written")

# %% [markdown]
# ## ✱ Stretch · Treat 10%
#
# Run `U.dispatch_sim("customer", p_treat=0.1)` and compare the naive effect with the 50/50 test. It changes with
# the split, and stays far from the global effect: the bias of a customer-randomised test depends on the split
# itself. What does that say about reading a 5% ramp of a marketplace feature as its effect?

# %% [markdown]
# ## Checkpoint
#
# 1. Which assumption does the dispatch test break? <details><summary>Answer</summary>No interference (SUTVA): a
#    control customer's outcome depends on which other customers are treated.</details>
# 2. Why does the bias point toward a bigger gain? <details><summary>Answer</summary>The treated arm gains what the
#    control arm loses; their difference counts the transfer twice and the real gain once.</details>
# 3. Name two other Sufrah tests that share a resource. <details><summary>Answer</summary>Restaurant ranking
#    (kitchen capacity), courier incentives (courier time), promotions with a limited budget.</details>
#
# **Carry forward.** Lab 3.4 designs the test that can measure this change.
