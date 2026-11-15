# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scipy>=1.13", "duckdb>=1.1"]
# ///
# %% [markdown]
# # Lab 2.1 · Capping order value
#
# Day 2 · Session 1 (Variance and heavy tails) · 25 min.
#
# Revenue per triggered customer in T-101 is noisy because about one order in a hundred is a group order worth
# many baskets. Capping each order's value at a high percentile cuts that noise, and changes what you estimate.
# Because the data is synthetic, the generator knows every customer's revenue under both arms, so you can
# measure the bias of each cap exactly: no real test lets you do that.
#
# **AI policy: AI-tutor.** An assistant may explain winsorising; the trade-off is yours to judge.
#
# **Reference state.** The T-101 stream: test-period orders of triggered customers, and the generator's
# potential outcomes (`_potential`). Nothing from Day 1.
#
# **Tasks**
# - [ ] 1 · Where the variance of revenue comes from (5')
# - [ ] 2 · Cap at the pooled 99th and 99.9th percentiles (5')
# - [ ] 3 · Effect and standard error under each cap (6')
# - [ ] 4 · Bias against the true uncapped effect (5')
# - [ ] 5 · Choose a cap and write the reason (4')
# - [ ] ✱ Stretch · Cap per customer instead of per order and compare

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

S = U.stream()
pc = U.per_customer(S)
trig = pc.loc[pc.triggered, ["customer_id", "variant", "treat"]]
orders = S["orders"].query("day >= 0").merge(trig, on="customer_id")      # test-period orders, triggered customers
print(len(trig), "triggered customers;", len(orders), "orders")

# %% [markdown]
# ## 1 · Where the variance comes from (5')
#
# ✏️ **Exercise** · Write `revenue(orders, cap=None)`: revenue per triggered customer (customers with no order
# count as 0), with each order's value capped at `cap` when given. Return a Series indexed by `customer_id`,
# aligned with `trig`.

# %%
def revenue(orders: pd.DataFrame, cap: float | None = None) -> pd.Series:
    # BEGIN SOLUTION
    v = orders.value if cap is None else orders.value.clip(upper=cap)
    return v.groupby(orders.customer_id).sum().reindex(trig.customer_id, fill_value=0.0)
    # END SOLUTION


# %%
try:
    y = revenue(orders)
except NotImplementedError:
    print("↪ using revenue per customer from U.per_customer()")
    y = pc.set_index("customer_id").loc[trig.customer_id, "revenue"]
top = y.sort_values(ascending=False)
k = len(y) // 100
var_all, var_rest = y.var(), top.iloc[k:].var()
print(f"sd of revenue: {y.std():.0f} SAR; without the top 1% of customers: {top.iloc[k:].std():.0f}")
print(f"the top 1% of customers carry {1 - var_rest / var_all:.0%} of the variance")
U.check(abs(y.sum() - pc.loc[pc.triggered, "revenue"].sum()) < 1, "revenue per customer matches the stream")

# %% [markdown]
# ## 2 · Caps from the pooled data (5')
#
# A cap is set from **both arms pooled**, so the rule cannot depend on the treatment. Caps at the 95th, 99th and
# 99.9th percentiles of order value:

# %%
caps = {"none": None, "p99.9": float(orders.value.quantile(0.999)), "p99": float(orders.value.quantile(0.99)),
        "p95": float(orders.value.quantile(0.95))}
print({k: (round(v) if v else v) for k, v in caps.items()})
print(f"orders above the p99 cap: {(orders.value > caps['p99']).mean():.1%}")

# %% [markdown]
# ## 3 · Effect and standard error under each cap (6')
#
# ✏️ **Exercise** · Write `effect(y)`: the difference in mean revenue, treatment minus control, and its standard
# error (unequal variances), for a Series aligned with `trig`. Return `(diff, se)`.

# %%
treat = trig.treat.to_numpy() == 1


def effect(y: pd.Series) -> tuple[float, float]:
    # BEGIN SOLUTION
    a, b = y.to_numpy()[treat], y.to_numpy()[~treat]
    return a.mean() - b.mean(), np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    # END SOLUTION


# %%
rows = {}
try:
    for name, cap in caps.items():
        d, se = effect(revenue(orders, cap))
        rows[name] = {"cap": cap, "diff": d, "se": se}
    table = pd.DataFrame(rows).T
except NotImplementedError:
    table = U.reference("d2_1_table")
U.keep("d2_1_table", table)
table["se_vs_none"] = table.se / table.loc["none", "se"]
print(table.round(3))
U.check(table.loc["p99", "se"] < table.loc["none", "se"], "capping lowers the standard error")

# %% [markdown]
# ## 4 · Bias against the true uncapped effect (5')
#
# The generator kept every customer's orders under both arms (`_potential`: the orders they place anyway, and
# the `extra` orders the new ranking adds). The true effect of a cap is the mean, over triggered customers, of
# capped revenue with the extra orders minus capped revenue without them.
#
# ✏️ **Exercise** · Write `true_effect(cap)`.

# %%
pot = S["_potential"].merge(trig[["customer_id"]], on="customer_id")


def true_effect(cap: float | None) -> float:
    # BEGIN SOLUTION
    v = pot.value if cap is None else pot.value.clip(upper=cap)
    return float(v[pot.extra].sum() / len(trig))
    # END SOLUTION


# %%
try:
    table["true_effect"] = [true_effect(c) for c in table.cap]
except NotImplementedError:
    table["true_effect"] = U.reference("d2_1_true")
U.keep("d2_1_true", table.true_effect.tolist())
truth = table.loc["none", "true_effect"]
table["bias_vs_uncapped"] = table.true_effect - truth
table["rmse"] = np.sqrt(table.bias_vs_uncapped ** 2 + table.se ** 2)
print(table[["cap", "diff", "se", "true_effect", "bias_vs_uncapped", "rmse"]].round(2))
U.check(table.loc["p95", "bias_vs_uncapped"] < table.loc["p99.9", "bias_vs_uncapped"] <= 0,
        "a lower cap moves the estimand further below the uncapped effect")

# %% [markdown]
# 🔍 **Look at** the `rmse` column: the error of the estimate around the effect you actually care about, bias and
# noise together. A cap is worth it while it removes more noise than it adds bias.
#
# ## 5 · Choose a cap (4')
#
# ✏️ **Exercise** · Fill `choice()` with the cap you would pre-register for revenue per customer, and one sentence
# on why. A cap is chosen before the test, from data that does not include its result.

# %%
def choice() -> dict:
    # BEGIN SOLUTION
    best = table.rmse.astype(float).idxmin()
    return {"cap": best, "why": f"{best} has the lowest error around the uncapped effect: it removes most of the "
                                "group-order noise for a small, stated bias; the estimand is revenue with each order "
                                "counted up to that value."}
    # END SOLUTION


# %%
try:
    CHOICE = choice()
except NotImplementedError:
    CHOICE = U.reference("d2_1_choice")
U.keep("d2_1_choice", CHOICE)
print(CHOICE)
U.check(CHOICE["cap"] in caps, "a cap from the table, with a reason")

# %% [markdown]
# ## ✱ Stretch · Cap per customer
#
# Cap revenue per customer (the 99th percentile of customer revenue) instead of each order. Compare the standard
# error and the bias. Which one would a finance director find easier to read?

# %% [markdown]
# ## Checkpoint
#
# 1. Why is the cap computed on both arms pooled? <details><summary>Answer</summary>A cap from one arm, or from
#    each arm separately, makes the metric depend on the treatment and can create a difference by itself.
#    </details>
# 2. A lower cap always gives a smaller standard error. Why not cap at the median? <details><summary>Answer
#    </summary>The estimand drifts away from revenue: the bias grows until it dominates the error.</details>
# 3. What do you write in the pre-registration about the cap? <details><summary>Answer</summary>The percentile,
#    the data it is computed on (pooled, both arms), and that the uncapped result is reported beside it.</details>
#
# **Carry forward.** Lab 2.2 removes far more noise with pre-period data, without changing the estimand.
