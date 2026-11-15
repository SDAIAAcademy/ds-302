# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scipy>=1.13", "duckdb>=1.1"]
# ///
# %% [markdown]
# # Lab 4.3 · A one-page recommendation for T-101
#
# Day 4 · Session 3 (Writing the recommendation) · 25 min.
#
# T-101, AI-ranked search, has run its 28 days. Rawan Al-Mubarak's review board meets tomorrow and reads one page.
# You compute every number the pre-registration asks for, apply its written decision rule without exception, and
# write the page: decision first, then the effect with its interval, the guardrails, the risks.
#
# **AI policy: AI-tutor.** An assistant may comment on your draft; the numbers and the decision are yours.
#
# **Reference state.** `data/preregistration_T101.json` and the T-101 stream. Nothing from another lab: the
# adjusted estimator of Lab 2.2 and the ratio interval of Lab 2.3 are given below.
#
# **Tasks**
# - [ ] 1 · Read the pre-registration (3')
# - [ ] 2 · The primary effect, adjusted, with its interval (6')
# - [ ] 3 · The four guardrails against their thresholds (6')
# - [ ] 4 · Apply the decision rule (4')
# - [ ] 5 · Write and save the one page (6')
# - [ ] ✱ Stretch · Add the effect in Riyadh only and say why it does not change the decision

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
import sufrah as U

S = U.stream(U.N_FULL)        # always the full stream, in quick mode too: the decision depends on it
pc = U.per_customer(S)
trig = pc[pc.triggered].reset_index(drop=True)

# %% [markdown]
# ## 1 · The pre-registration (3')

# %%
PRE = U.js("preregistration_T101")
print(json.dumps(PRE, indent=1, ensure_ascii=False))
n_arm = S["assignments"].variant.value_counts()
from scipy import stats
SRM_P = float(stats.chisquare([n_arm["control"], n_arm["treatment"]]).pvalue)
print(f"sample ratio check: {n_arm['control']:,} control, {n_arm['treatment']:,} treatment, p = {SRM_P:.3f}")


# Given: the estimators of Day 2
def cuped(y: np.ndarray, x: np.ndarray, t: np.ndarray) -> dict:
    th = np.cov(y, x, ddof=1)[0, 1] / np.var(x, ddof=1)
    ya = y - th * (x - x.mean())
    a, b = ya[t == 1], ya[t == 0]
    d = a.mean() - b.mean()
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return {"diff": d, "lo": d - 1.96 * se, "hi": d + 1.96 * se, "rel": d / y[t == 0].mean()}


def ratio_diff(num: np.ndarray, den: np.ndarray, t: np.ndarray) -> dict:
    out = {}
    for arm in (1, 0):
        o, s = num[t == arm], den[t == arm]
        r = o.sum() / s.sum()
        c = np.cov(o, s, ddof=1)
        out[arm] = (r, (c[0, 0] - 2 * r * c[0, 1] + r ** 2 * c[1, 1]) / (len(o) * s.mean() ** 2))
    d, se = out[1][0] - out[0][0], np.sqrt(out[1][1] + out[0][1])
    return {"control": out[0][0], "treatment": out[1][0], "diff": d, "lo": d - 1.96 * se, "hi": d + 1.96 * se}


# %% [markdown]
# ## 2 · The primary effect (6')
#
# ✏️ **Exercise** · Compute `PRIMARY` as the pre-registration says: orders per triggered customer, adjusted for
# the same metric in the 28 pre-period days, with its 95% interval.

# %%
t = trig.treat.to_numpy()


def primary() -> dict:
    # BEGIN SOLUTION
    return cuped(trig.orders.to_numpy(float), trig.orders_pre.to_numpy(float), t)
    # END SOLUTION


# %%
try:
    PRIMARY = primary()
except NotImplementedError:
    PRIMARY = U.reference("d4_3_primary")
PRIMARY = {k: float(v) for k, v in PRIMARY.items()}
U.keep("d4_3_primary", PRIMARY)
print({k: round(v, 4) for k, v in PRIMARY.items()})
U.check(PRIMARY["lo"] > 0, "the primary interval is above zero")

# %% [markdown]
# ## 3 · The guardrails (6')
#
# ✏️ **Exercise** · Fill `guardrails()`: one dict per pre-registered guardrail with `metric`, `value`,
# `threshold`, `direction` and `holds` (true or false), in the pre-registration's order.

# %%
sr = S["searches"].merge(S["assignments"][["customer_id", "variant"]], on="customer_id")


def guardrails() -> list:
    # BEGIN SOLUTION
    p95 = sr.groupby("variant").latency_ms.quantile(0.95)
    cost = sr.loc[sr.variant == "treatment", "cost_sar"].mean() * 1000
    comp = ratio_diff(trig.complaints.to_numpy(float), trig.orders.to_numpy(float), t)
    rev = cuped(trig.revenue.to_numpy(float), trig.revenue_pre.to_numpy(float), t)
    rev_lo_rel = rev["lo"] / trig.revenue[t == 0].mean()
    values = [p95["treatment"] - p95["control"], cost, comp["hi"] * 1000, rev_lo_rel]
    out = []
    for g, v in zip(PRE["guardrails"], values):
        holds = v <= g["threshold"] if g["direction"] == "at most" else v >= g["threshold"]
        out.append({"metric": g["metric"], "value": float(v), "threshold": g["threshold"],
                    "direction": g["direction"], "harm": bool(g.get("harm", False)), "holds": bool(holds)})
    return out
    # END SOLUTION


# %%
try:
    GUARD = guardrails()
except NotImplementedError:
    GUARD = U.reference("d4_3_guardrails")
U.keep("d4_3_guardrails", GUARD)
print(pd.DataFrame(GUARD)[["metric", "value", "direction", "threshold", "holds"]].round(3).to_string(index=False))
U.check(len(GUARD) == 4 and not GUARD[0]["holds"] and all(g["holds"] for g in GUARD[1:]),
        "the latency guardrail fails; the other three hold")

# %% [markdown]
# ## 4 · The decision rule (4')
#
# ✏️ **Exercise** · Write `decide(primary, guard)` that applies the pre-registration's rule literally and returns
# `launch`, `iterate` or `stop`.

# %%
def decide(primary: dict, guard: list) -> str:
    # BEGIN SOLUTION
    if primary["lo"] <= 0 or any(g["harm"] and not g["holds"] for g in guard):
        return "stop"
    return "launch" if all(g["holds"] for g in guard) else "iterate"
    # END SOLUTION


# %%
try:
    DECISION = decide(PRIMARY, GUARD)
except NotImplementedError:
    DECISION = U.reference("d4_3_decision")
U.keep("d4_3_decision", DECISION)
print("decision:", DECISION.upper())
U.check(DECISION == "iterate", "the rule says iterate: a non-harm guardrail failed")

# %% [markdown]
# ## 5 · The page (6')
#
# ✏️ **Exercise** · Complete `page()`. Order: the decision and why in two sentences; the effect with its interval
# in units a manager uses; the guardrail table; the risks and what would change the decision; the next step.

# %%
def page() -> str:
    # BEGIN SOLUTION
    p = PRIMARY
    fmt = lambda v: f"{v:.0f}" if abs(v) >= 10 else f"{v:.3f}"
    rows = "\n".join(f"| {g['metric']} | {fmt(g['value'])} | {g['direction']} {g['threshold']} | "
                     f"{'holds' if g['holds'] else 'FAILS'} |" for g in GUARD)
    lat = GUARD[0]["value"]
    return f"""# T-101 AI-ranked search: recommendation to the review board

**Decision: {DECISION}.** The AI ranking raises orders among customers who search, but it slows the search screen
beyond the limit we set before the test: p95 latency is {lat:.0f} ms worse against a limit of 300 ms. The
pre-registered rule says iterate: fix the latency, then confirm with a short test.

## Effect
Orders per triggered customer over 28 days rose by {p['diff']:.3f} (95% interval {p['lo']:.3f} to {p['hi']:.3f}),
that is {p['rel']:+.1%}, adjusted for each customer's orders in the 28 days before the test. Triggered customers
are the {trig.shape[0]:,} of {len(pc):,} assigned customers who searched at least once.

## Guardrails
| Guardrail | Value | Limit | Status |
|---|---|---|---|
{rows}

## Risks and what would change this
- The latency is a tail problem (the median rose far less); a faster model or a cache may fix it without losing the
  lift. If latency cannot come under the limit, the decision becomes stop.
- Complaints did not rise beyond the margin; the harm guardrail holds.
- The sample ratio check holds (p = {SRM_P:.2f}), and the trigger rate is equal in both arms (Lab 1.1).

## Next step
Owner: Yazeed Al-Hamdan. Reduce p95 latency by at least {lat - 300:.0f} ms, then run a 14-day confirmation
with the same metrics and rule.
"""
    # END SOLUTION


# %%
try:
    PAGE = page()
except NotImplementedError:
    PAGE = U.reference("d4_3_page")
U.keep("d4_3_page", PAGE)
U.save("T101_recommendation.md", PAGE)
print(PAGE)
U.check(PAGE.lower().count("decision") >= 1 and "interval" in PAGE and len(PAGE.split()) < 450,
        "decision, interval, guardrails, on one page")

# %% [markdown]
# ## ✱ Stretch · Riyadh only
#
# Compute the adjusted effect for Riyadh's triggered customers. It may look bigger or smaller: why does a city
# result, not pre-registered, not change the decision? (Lab 4.2.)

# %% [markdown]
# ## Checkpoint
#
# 1. Why does the page start with the decision? <details><summary>Answer</summary>The reader decides; the evidence
#    follows in the order they need to check it.</details>
# 2. The primary interval is far above zero. Why is the answer not launch? <details><summary>Answer</summary>The
#    pre-registered rule makes every guardrail a condition of launch; latency failed.</details>
# 3. What belongs under risks? <details><summary>Answer</summary>What could make the decision wrong and what would
#    change it, with the checks already done (sample ratio, trigger balance).</details>
#
# **Carry forward.** The capstone's recommendation follows this page.
