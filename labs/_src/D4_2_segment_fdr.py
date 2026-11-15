# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scipy>=1.13", "statsmodels>=0.14"]
# ///
# %% [markdown]
# # Lab 4.2 · Twenty segment results, corrected
#
# Day 4 · Session 2 (Many segments) · 25 min.
#
# T-205 added photos to restaurant menus. The team then cut the results by the
# cuisine of each customer's favourite restaurant: twenty segments, four of them "significant". You compute the
# twenty tests, measure how many false wins twenty tests produce by chance, and apply Bonferroni, Holm and
# Benjamini-Hochberg corrections to see what survives.
#
# **AI policy: AI-tutor.** An assistant may explain the procedures; apply them yourself.
#
# **Reference state.** `data/segments_T205.csv`: per segment, customers, means and standard deviations of orders
# per customer in each arm. Nothing from another lab.
#
# **Tasks**
# - [ ] 1 · Twenty z-tests from the segment table (5')
# - [ ] 2 · How many false wins by chance: simulate (5')
# - [ ] 3 · Bonferroni and Holm (5')
# - [ ] 4 · Benjamini-Hochberg (5')
# - [ ] 5 · What survives, in two sentences (5')
# - [ ] ✱ Stretch · Shrink the segment effects toward the overall effect and compare

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
from statsmodels.stats.multitest import multipletests
import sufrah as U

seg = U.csv("segments_T205")
print(seg.head())

# %% [markdown]
# ## 1 · Twenty z-tests (5')
#
# ✏️ **Exercise** · Write `tests(seg)`: add columns `diff`, `se`, `z` and `p` (two-sided) for treatment minus
# control in each segment.

# %%
def tests(seg: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    out = seg.copy()
    out["diff"] = out.mean_treatment - out.mean_control
    out["se"] = np.sqrt(out.sd_treatment ** 2 / out.n_treatment + out.sd_control ** 2 / out.n_control)
    out["z"] = out["diff"] / out.se
    out["p"] = 2 * stats.norm.sf(np.abs(out.z))
    return out
    # END SOLUTION


# %%
try:
    T = tests(seg)
except NotImplementedError:
    T = U.reference("d4_2_tests")
U.keep("d4_2_tests", T)
print(T[["segment", "diff", "z", "p"]].sort_values("p").head(6).round(4).to_string(index=False))
print("segments with p < 0.05:", int((T.p < 0.05).sum()), "of", len(T))
U.check(len(T) == 20 and (T.p < 0.05).sum() >= 3, "twenty tests, several 'significant'")

# %% [markdown]
# ## 2 · False wins by chance (5')
#
# ✏️ **Exercise** · Write `chance(reps, rng)`: simulate `reps` sets of 20 independent z-tests with no effect at
# all, and return the share of sets with at least one p < 0.05 and the mean number of false wins per set.

# %%
def chance(reps: int, rng) -> tuple[float, float]:
    # BEGIN SOLUTION
    p = 2 * stats.norm.sf(np.abs(rng.standard_normal((reps, 20))))
    wins = (p < 0.05).sum(axis=1)
    return float((wins > 0).mean()), float(wins.mean())
    # END SOLUTION


# %%
try:
    any_win, mean_wins = chance(U.pick(20_000, 5_000), np.random.default_rng(42))
except NotImplementedError:
    any_win, mean_wins = U.reference("d4_2_chance")
U.keep("d4_2_chance", [any_win, mean_wins])
print(f"with no effect anywhere: at least one false win in {any_win:.0%} of tests; {mean_wins:.2f} on average "
      f"(1 - 0.95^20 = {1 - 0.95 ** 20:.2f})")
U.check(abs(any_win - (1 - 0.95 ** 20)) < 0.02, "about 64% of twenty-segment analyses show a false win")

# %% [markdown]
# ## 3 · Bonferroni and Holm (5')
#
# Both control the family-wise error rate: the chance of **any** false win. Bonferroni tests each p against
# 0.05 / 20; Holm steps down from the smallest p and is never less powerful.
#
# ✏️ **Exercise** · Add boolean columns `bonferroni` and `holm` (rejected or not) with `multipletests`.

# %%
def fwer(T: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    T = T.copy()
    T["bonferroni"] = multipletests(T.p, alpha=0.05, method="bonferroni")[0]
    T["holm"] = multipletests(T.p, alpha=0.05, method="holm")[0]
    return T
    # END SOLUTION


# %%
try:
    T = fwer(T)
except NotImplementedError:
    T = U.reference("d4_2_fwer")
U.keep("d4_2_fwer", T)
print("Bonferroni keeps:", list(T.segment[T.bonferroni]), "| Holm keeps:", list(T.segment[T.holm]))

# %% [markdown]
# ## 4 · Benjamini-Hochberg (5')
#
# Benjamini-Hochberg controls the false discovery rate: the expected share of false wins **among the segments
# you report**. Sort the p-values; find the largest rank k with p_(k) ≤ 0.05 k / 20; report the k smallest.
#
# ✏️ **Exercise** · Write `bh(p, q=0.05)` by hand and compare it with `multipletests(..., method="fdr_bh")`.

# %%
def bh(p: np.ndarray, q: float = 0.05) -> np.ndarray:
    # BEGIN SOLUTION
    p = np.asarray(p)
    order = np.argsort(p)
    m = len(p)
    ok = p[order] <= q * np.arange(1, m + 1) / m
    k = ok.nonzero()[0].max() + 1 if ok.any() else 0
    keep = np.zeros(m, bool)
    keep[order[:k]] = True
    return keep
    # END SOLUTION


# %%
try:
    T["bh"] = bh(T.p.to_numpy())
except NotImplementedError:
    T["bh"] = U.reference("d4_2_bh")
U.keep("d4_2_bh", T.bh.tolist())
lib = multipletests(T.p, alpha=0.05, method="fdr_bh")[0]
print("Benjamini-Hochberg keeps:", list(T.segment[T.bh]))
U.check((T.bh.to_numpy() == lib).all(), "your procedure agrees with statsmodels")

# %%
summary = T.loc[T.p < 0.05, ["segment", "diff", "p", "bonferroni", "holm", "bh"]].sort_values("p")
print(summary.round(4).to_string(index=False))

# %% [markdown]
# ## 5 · What survives (5')
#
# ✏️ **Exercise** · Write `report()`: two sentences for the board on which segments survive and what that means
# for the decision about menu photos.

# %%
def report() -> str:
    # BEGIN SOLUTION
    kept = " and ".join(T.segment[T.bh])
    dropped = " and ".join(T.segment[(T.p < 0.05) & ~T.bh])
    return (f"Of four segments with p below 0.05, two survive every correction ({kept}); the other two ({dropped}) "
            f"are what twenty tests produce by chance. Menu photos may help {kept} customers: confirm it with a new "
            f"test pre-registered on those segments before launching anything on the strength of this cut.")
    # END SOLUTION


# %%
try:
    REPORT = report()
except NotImplementedError:
    REPORT = U.reference("d4_2_report")
U.keep("d4_2_report", REPORT)
print(REPORT)
U.check(set(T.segment[T.bh]) == {"Mandi", "Coffee"}, "the two planted segments survive Benjamini-Hochberg")

# %% [markdown]
# ## ✱ Stretch · Shrinkage
#
# A segment's estimate is noisy; shrink it toward the overall effect: w · diff + (1 - w) · overall, with
# w = τ² / (τ² + se²) and τ² the variance of the true segment effects (estimate it as the variance of the diffs
# minus the mean se²). Which segments still stand out?

# %% [markdown]
# ## Checkpoint
#
# 1. Twenty segments, one with p = 0.01. Is that evidence? <details><summary>Answer</summary>Weak: Bonferroni needs
#    p below 0.0025, and Benjamini-Hochberg would keep it only if it were the smallest and below 0.0025 too.
#    </details>
# 2. When is the false discovery rate the right target? <details><summary>Answer</summary>When you report a list of
#    findings and can accept that a stated share of them are false, as in exploring segments; a launch decision on
#    one primary metric needs no correction.</details>
# 3. What should happen to a segment that survives? <details><summary>Answer</summary>A new test, pre-registered on
#    that segment, before anything launches for it.</details>
#
# **Carry forward.** Lab 4.4's write-ups include the same temptation.
