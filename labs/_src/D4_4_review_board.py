# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scipy>=1.13"]
# ///
# %% [markdown]
# # Lab 4.4 · Two write-ups, and the capstone change
#
# Day 4 · Session 4 (The review board) · 25 min.
#
# Rawan Al-Mubarak's review board reads five write-ups this week, W1 to W5, each ending "we recommend launch".
# You sit on the board. You load the write-ups, check two of them against what this course has taught, give each
# a decision (launch, iterate or stop) with the fault you found, score your log against the board's, and choose
# the change your capstone will design.
#
# **AI policy: AI-tutor.** An assistant may explain a check; the decisions are yours.
#
# **Reference state.** `data/writeups/` (five write-ups, each a page and its numbers) and
# `data/capstone_changes.json`. The group sequential plan of W2 is given below. Nothing from another lab.
#
# **Tasks**
# - [ ] 1 · The review checklist: load the write-ups (3')
# - [ ] 2 · W1: check, decide, log (6')
# - [ ] 3 · W2: check, decide, log (6')
# - [ ] 4 · Score the log (3')
# - [ ] 5 · Choose the capstone change and its primary metric (7')
# - [ ] ✱ Stretch · Decide W3, W4 and W5

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
from scipy import stats
import sufrah as U

WRITEUPS = Path("data/writeups")

# The board's checklist: the questions every write-up must answer, in the order the course taught them.
CHECKLIST = [
    "Did the split work? (sample ratio, Lab 1.2)",
    "Is the analysis the pre-registered one, at the planned time? (Labs 1.4, 3.1)",
    "Is the effect settled, or fading? (Lab 4.1)",
    "Did every guardrail hold, and the harm guardrail above all? (Labs 1.3, 4.1)",
    "Is a segment or a metric picked after the fact? (Lab 4.2)",
]

# %% [markdown]
# ## 1 · Load the write-ups (3')
#
# ✏️ **Exercise** · Write `load()`: a dict from write-up id (`W1` ... `W5`) to `{"page": text of the .md,
# "data": the parsed .json}`.

# %%
def load() -> dict:
    # BEGIN SOLUTION
    return {p.stem: {"page": p.read_text(encoding="utf-8"),
                     "data": json.loads(p.with_suffix(".json").read_text(encoding="utf-8"))}
            for p in sorted(WRITEUPS.glob("W*.md"))}
    # END SOLUTION


# %%
try:
    W = load()
except NotImplementedError:
    W = {p.stem: {"page": p.read_text(encoding="utf-8"),
                  "data": json.loads(p.with_suffix(".json").read_text(encoding="utf-8"))}
         for p in sorted(WRITEUPS.glob("W*.md"))}
for wid, w in W.items():
    print(wid, "|", w["page"].splitlines()[0][2:], "|", sorted(w["data"]))
U.check(sorted(W) == ["W1", "W2", "W3", "W4", "W5"], "five write-ups loaded")
print("\n".join(f"  {i + 1}. {c}" for i, c in enumerate(CHECKLIST)))

# %% [markdown]
# ## 2 · Review W1 (6')
#
# W1 reports a 2.1% lift with a clean interval. Run the first question of the checklist.
#
# ✏️ **Exercise** · Write `review_w1(data)`: the chi-square p-value of the users against the planned 50/50
# split, and a dict `{"decision": ..., "fault": ...}` in one sentence.

# %%
def review_w1(data: dict) -> tuple[float, dict]:
    # BEGIN SOLUTION
    c, t = data["users"]["control"], data["users"]["treatment"]
    p = float(stats.chisquare([c, t]).pvalue)
    return p, {"decision": "iterate",
               "fault": f"sample ratio mismatch: {t:,} against {c:,} has a chi-square p-value of {p:.1e}; the "
                        f"result cannot be trusted until the cause is found and the test is rerun"}
    # END SOLUTION


# %%
try:
    P_W1, D_W1 = review_w1(W["W1"]["data"])
except NotImplementedError:
    P_W1, D_W1 = U.reference("d4_4_w1")
U.keep("d4_4_w1", [P_W1, D_W1])
print(f"W1 sample ratio p = {P_W1:.2e} ->", D_W1["decision"].upper(), "|", D_W1["fault"])
U.check(P_W1 < 0.001 and D_W1["decision"] != "launch", "W1 fails the first check")

# %% [markdown]
# ## 3 · Review W2 (6')
#
# W2 was checked every morning and stopped on day 9. Its pre-registration did plan looks: a group sequential
# design with O'Brien-Fleming-type spending over 28 days, no looks in the first six days. The boundaries are given.
#
# ✏️ **Exercise** · Write `review_w2(data)`: did the daily z cross the planned boundary on any day? What does the
# planned day-28 analysis show? Return `(crossed, z_final, decision)` with `decision` the dict of step 2.

# %%
BOUNDS = [None] * 6 + [3.80, 3.60, 3.47, 3.38, 3.26, 3.15, 3.02, 2.91, 2.82, 2.74, 2.70, 2.63, 2.55, 2.49,
                       2.44, 2.38, 2.35, 2.32, 2.26, 2.23, 2.19, 2.14]   # day 1 ... day 28 (Lab 3.1's plan)


def review_w2(data: dict) -> tuple[bool, float, dict]:
    # BEGIN SOLUTION
    z = data["daily_z"]
    crossed = any(b is not None and abs(v) >= b for v, b in zip(z, BOUNDS))
    z_final = float(z[data["planned_days"] - 1])
    stop_day = data["stopped_day"]
    return crossed, z_final, {
        "decision": "stop",
        "fault": f"peeking: on day {stop_day} z = {z[stop_day - 1]:.2f} against a planned boundary of "
                 f"{BOUNDS[stop_day - 1]:.2f}; no day crossed, and the planned day-28 analysis gives z = "
                 f"{z_final:.2f}, no effect"}
    # END SOLUTION


# %%
try:
    CROSSED, Z_FINAL, D_W2 = review_w2(W["W2"]["data"])
except NotImplementedError:
    CROSSED, Z_FINAL, D_W2 = U.reference("d4_4_w2")
U.keep("d4_4_w2", [CROSSED, Z_FINAL, D_W2])
print("W2 crossed the planned boundary:", CROSSED, "| day-28 z:", round(Z_FINAL, 2), "->", D_W2["decision"].upper())
print(D_W2["fault"])
U.check(not CROSSED and Z_FINAL < 1.96 and D_W2["decision"] == "stop", "W2 stopped on a peek; the plan says no effect")

# %% [markdown]
# ## 4 · Score your log (3')
#
# The board's own log is in `data/reference/review_decisions.*.json`. Open it only now.
#
# ✏️ **Exercise** · Write `score(log, key)`: for each write-up in your log, whether your decision matches the
# board's. Return a DataFrame with `mine`, `board`, `match`.

# %%
LOG = {"W1": D_W1, "W2": D_W2}


def score(log: dict, key: dict) -> pd.DataFrame:
    # BEGIN SOLUTION
    return pd.DataFrame({w: {"mine": d["decision"], "board": key[w]["decision"],
                             "match": d["decision"] == key[w]["decision"]} for w, d in log.items()}).T
    # END SOLUTION


# %%
KEY = U.reference("review_decisions")
try:
    SCORE = score(LOG, KEY)
except NotImplementedError:
    SCORE = U.reference("d4_4_score")
U.keep("d4_4_score", SCORE)
print(SCORE)
U.save("review_log.json", json.dumps(LOG, indent=1, ensure_ascii=False))
U.check(bool(SCORE["match"].all()), "your decisions match the board's on W1 and W2")

# %% [markdown]
# ## 5 · Choose your capstone change and size it (7')
#
# The capstone designs one of three changes in `data/capstone_changes.json`. Before you choose, know what each
# can detect in 28 days with its traffic.
#
# ✏️ **Exercise** · Write `mde(change)`: from `U.capstone_data(change)["customers"]`, the minimum detectable
# relative lift in orders per customer at 5% two-sided and 80% power, raw and adjusted with the pre-period
# (CUPED: the variance shrinks by 1 - ρ², with ρ the correlation of two consecutive 28-day periods in the
# control arm). Then fill `CHOICE` with your change, its primary metric, its
# guardrails and its harm guardrail.

# %%
CHANGES = U.js("capstone_changes")["changes"]
for c in CHANGES:
    print(c["id"], "|", c["name"], "|", c["owner"], "|", f"{c['customers']:,} customers", "| harm:", c["harm"])


def mde(change: str) -> dict:
    # BEGIN SOLUTION
    cu = U.capstone_data(change)["customers"]
    y = cu.orders_pre.to_numpy(float)        # one 28-day period stands in for the test period
    n = len(cu) / 2
    ctl = cu[cu.variant == "control"]        # two consecutive periods of untreated customers give rho
    rho = np.corrcoef(ctl.orders_pre, ctl.orders)[0, 1]
    k = stats.norm.ppf(0.975) + stats.norm.ppf(0.80)
    raw = k * np.sqrt(2 * y.var(ddof=1) / n) / y.mean()
    return {"change": change, "raw": float(raw), "cuped": float(raw * np.sqrt(1 - rho ** 2)), "rho": float(rho)}
    # END SOLUTION


# %%
try:
    MDE = pd.DataFrame([mde(c["id"]) for c in CHANGES]).set_index("change")
except NotImplementedError:
    MDE = U.reference("d4_4_mde")
U.keep("d4_4_mde", MDE)
print(MDE.round(4))
U.check(bool((MDE.cuped < MDE.raw).all()), "the pre-period shrinks every detectable lift")

# %%
def choose() -> dict:
    # BEGIN SOLUTION
    return {
        "change": "C2",
        "why": "Luqma's lift was real in T-401 and the harm was the reason to stop; the allergen checker is the fix, "
               "and the board will want proof that the harm is gone",
        "primary": "orders per customer over 28 days, CUPED-adjusted with the 28 pre-period days",
        "unit": "customer",
        "guardrails": ["Luqma p95 response time", "cost per conversation", "complaints per 1,000 orders"],
        "harm_guardrail": "wrong ingredient or allergen complaints per 1,000 orders, upper 95% bound of the difference",
    }
    # END SOLUTION


# %%
try:
    CHOICE = choose()
except NotImplementedError:
    CHOICE = U.reference("d4_4_choice")
U.keep("d4_4_choice", CHOICE)
U.save("capstone_choice.json", json.dumps({**CHOICE, "mde": MDE.loc[CHOICE["change"]].round(4).to_dict()},
                                          indent=1, ensure_ascii=False))
print(json.dumps(CHOICE, indent=1, ensure_ascii=False))
U.check(CHOICE["change"] in MDE.index and bool(CHOICE["harm_guardrail"]), "a change chosen, with a harm guardrail")

# %% [markdown]
# ## ✱ Stretch · W3, W4 and W5
#
# Decide the other three with the checklist and add them to `LOG`, then score again. Each has one fault or none:
# W3's weekly lifts, W4's sample ratio and pre-registration, W5's guardrail against its threshold.

# %% [markdown]
# ## Checkpoint
#
# 1. W1's interval is clean. Why is the decision not launch? <details><summary>Answer</summary>A sample ratio
#    mismatch says the arms differ in who is in them; every number after it is suspect.</details>
# 2. W2 crossed p = 0.05 on day 9. Why stop rather than iterate? <details><summary>Answer</summary>The planned
#    analysis ran to day 28 and found nothing; there is no effect to iterate on.</details>
# 3. Why size the capstone change before choosing it? <details><summary>Answer</summary>A change whose plausible
#    lift is below what 28 days can detect needs a different metric, more traffic or a longer test, and the
#    design must say which.</details>
#
# **Carry forward.** `artifacts/capstone_choice.json` starts your capstone; its README is in `capstone/`.
