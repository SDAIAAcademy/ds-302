# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scipy>=1.13", "duckdb>=1.1"]
# ///
# %% [markdown]
# # Lab 1.2 · Sample ratio and A/A checks
#
# Day 1 · Session 2 (Sample ratio mismatch and A/A tests) · 25 min.
#
# Three Sufrah tests were planned as 50/50 splits by customer. One of them is not what was planned. You test
# each split, find where the faulty one loses users, and measure with A/A reshuffles the false-win rate that the
# standard analysis really has on Sufrah's data.
#
# **AI policy: AI-tutor.** Run the checks yourself; an assistant may explain a test statistic.
#
# **Reference state.** `data/srm_tests.csv` (daily assignment logs of T-201, T-202, T-203 by platform and app
# build) and the pre-period of the T-101 stream. Nothing from another lab.
#
# **Tasks**
# - [ ] 1 · Users per arm for three tests (3')
# - [ ] 2 · A chi-square sample ratio test for each (5')
# - [ ] 3 · Find the platform and build that lose users (6')
# - [ ] 4 · A/A: 500 reshuffles of the pre-period, the false-win rate (7')
# - [ ] 5 · Name the faulty test and its cause in one line (4')
# - [ ] ✱ Stretch · Run the A/A at the order level and explain the higher rate

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
from scipy import stats
import sufrah as U

logs = U.csv("srm_tests")
print(logs.head())

# %% [markdown]
# ## 1 · Users per arm (3')

# %%
users = logs.groupby(["test_id", "variant"]).users.sum().unstack()
users["treatment_share"] = users.treatment / (users.control + users.treatment)
print(users)

# %% [markdown]
# A share of 49.4% looks harmless. Whether it is depends on the number of users: that is what the test says.
#
# ## 2 · The sample ratio test (5')
#
# ✏️ **Exercise** · Write `srm_p(control, treatment, share=0.5)`: the p-value of a chi-square goodness-of-fit
# test of the two counts against the planned share. Platforms commonly flag a split when p is below 0.001.

# %%
def srm_p(control: int, treatment: int, share: float = 0.5) -> float:
    # BEGIN SOLUTION
    n = control + treatment
    return float(stats.chisquare([control, treatment], [n * (1 - share), n * share]).pvalue)
    # END SOLUTION


# %%
try:
    srm = {t: srm_p(int(r.control), int(r.treatment)) for t, r in users.iterrows()}
except NotImplementedError:
    srm = U.reference("d1_2_srm")
U.keep("d1_2_srm", srm)
for t, p in srm.items():
    print(f"{t}: p = {p:.2g}", "  ← mismatch" if p < 0.001 else "")
U.check(sum(p < 0.001 for p in srm.values()) == 1, "exactly one test fails the sample ratio check")

# %% [markdown]
# ## 3 · Where are the users lost? (6')
#
# A mismatch is a symptom. The cause is found by splitting the counts by everything that could lose or add
# users unevenly: platform, app build, day, country, browser.
#
# ✏️ **Exercise** · Write `srm_by(df, column)`: for one test's rows, a table with one row per value of `column`,
# the control and treatment counts, the treatment share and the SRM p-value.

# %%
def srm_by(df: pd.DataFrame, column: str) -> pd.DataFrame:
    # BEGIN SOLUTION
    t = df.groupby([column, "variant"]).users.sum().unstack()
    t["treatment_share"] = t.treatment / (t.control + t.treatment)
    t["p"] = [stats.chisquare([c, x]).pvalue for c, x in zip(t.control, t.treatment)]
    return t
    # END SOLUTION


# %%
faulty_test = min(srm, key=srm.get)
try:
    by_build = srm_by(logs[logs.test_id == faulty_test], "app_build")
    by_day = srm_by(logs[logs.test_id == faulty_test], "day")
except NotImplementedError:
    by_build, by_day = U.reference("d1_2_by_build"), U.reference("d1_2_by_day")
U.keep("d1_2_by_build", by_build)
U.keep("d1_2_by_day", by_day)
print(by_build.round(4))
print("days with p < 0.05:", int((by_day.p < 0.05).sum()), "of", len(by_day))
bad_build = by_build.p.idxmin()
U.check(by_build.p.min() < 1e-6 and (by_build.drop(index=bad_build).p > 0.001).all(),
        "one build loses users; the others are fine")

# %% [markdown]
# 🔍 **Look at** the day table too. The loss is spread over every day, which points to a cause that is always
# there (a build) rather than an incident (an outage on one day).
#
# ## 4 · A/A: the false-win rate the analysis really has (7')
#
# An A/A test splits customers into two groups that get the same thing. On Sufrah's own data, a correct analysis
# should call about 5% of A/A splits "significant" at the 5% level. Reshuffling real pre-period data gives many
# A/A tests at no cost.
#
# ✏️ **Exercise** · Write `aa_rate(values, reps, rng)`: split `values` into two random halves `reps` times, run a
# Welch t-test each time, and return the share of p-values below 0.05.

# %%
pc = U.per_customer()
values = pc.revenue_pre.to_numpy()
reps = U.pick(500, 200)
rng = np.random.default_rng(12)


def aa_rate(values: np.ndarray, reps: int, rng) -> float:
    # BEGIN SOLUTION
    hits = 0
    for _ in range(reps):
        mask = rng.random(len(values)) < 0.5
        p = stats.ttest_ind(values[mask], values[~mask], equal_var=False).pvalue
        hits += p < 0.05
    return hits / reps
    # END SOLUTION


# %%
try:
    aa = aa_rate(values, reps, rng)
except NotImplementedError:
    aa = U.reference("d1_2_aa")
U.keep("d1_2_aa", aa)
band = 1.96 * np.sqrt(0.05 * 0.95 / reps)
print(f"A/A false-win rate: {aa:.3f} over {reps} reshuffles (expected 0.05 ± {band:.3f})")
U.check(abs(aa - 0.05) < 2 * band, "the customer-level A/A rate is close to 5%")

# %% [markdown]
# ## 5 · Name the faulty test (4')
#
# ✏️ **Exercise** · Fill `FINDING` with the test, the build and one line on the likely cause and what to do.

# %%
def finding() -> dict:
    # BEGIN SOLUTION
    return {"test": faulty_test, "build": str(bad_build),
            "cause": "Treatment users on Android build 7.4 are lost before they are logged, most likely because "
                     "the new checkout page fails on that build; do not read the result, fix the build and rerun."}
    # END SOLUTION


# %%
try:
    FINDING = finding()
except NotImplementedError:
    FINDING = U.reference("d1_2_finding")
U.keep("d1_2_finding", FINDING)
print(FINDING)
U.check(FINDING["test"] == "T-203" and FINDING["build"] == "7.4", "T-203, build 7.4")

# %% [markdown]
# ## ✱ Stretch · The A/A at the wrong unit
#
# Keep the split by customer, but run the t-test on pre-period **order values**, one row per order
# (`U.stream()["orders"]`, days below 0). The false-win rate rises above 5%: the orders of one customer move
# together, and the order-level test treats them as independent. Which Day 2 session repairs this?

# %% [markdown]
# ## Checkpoint
#
# 1. A test shows a 3% lift and p = 0.0004 on the sample ratio check. What do you report? <details><summary>
#    Answer</summary>No result: the split is broken, so the lift may be produced by the lost users. Find the cause,
#    fix it, rerun.</details>
# 2. Why use a strict threshold such as 0.001 for the sample ratio check? <details><summary>Answer</summary>It runs
#    on every test, often every day; a strict threshold keeps false alarms rare, and real mismatches are usually
#    far below it.</details>
# 3. An A/A over 500 reshuffles gives 9% false wins. What does that tell you? <details><summary>Answer</summary>The
#    analysis is wrong for this data: often the unit of analysis does not match the unit of randomisation, or the
#    variance is underestimated.</details>
#
# **Carry forward.** Lab 4.4 checks a write-up for exactly this fault.
