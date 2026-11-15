# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2"]
# ///
# %% [markdown]
# # Lab 4.1 · The Luqma chat-assistant test
#
# Day 4 · Session 1 (Testing AI features) · 25 min.
#
# T-401 gave half of Sufrah's customers Luqma, an in-app chat assistant for ordering help and support, in place of
# the old help menu, for four weeks. Customers order more. You analyse the test against its pre-registration: the
# primary metric, the latency and cost guardrails of an AI feature, complaints and the harm guardrail
# (wrong ingredient or allergen information), the lift week by week, and the decision.
#
# **AI policy: AI-tutor.** An assistant may explain; the analysis and the decision are yours.
#
# **Reference state.** `U.luqma()`: weekly orders and conversations per customer, one row per conversation
# (latency, cost) and one row per order (complaint flags). The analysis reads logs only; nothing calls a model.
#
# **Tasks**
# - [ ] 1 · The primary metric with its interval (5')
# - [ ] 2 · Latency and cost guardrails (5')
# - [ ] 3 · Complaints and wrong-information complaints (6')
# - [ ] 4 · The lift by week: novelty (5')
# - [ ] 5 · The decision and its reason (4')
# - [ ] ✱ Stretch · Find the city where the harm is largest and say what you would ask the Luqma team

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

L = U.luqma()
weekly, convs, orders = L["weekly"], L["conversations"], L["orders"]
print(weekly.groupby("variant").customer_id.nunique(), "\n", len(convs), "conversations;", len(orders), "orders")

# The pre-registration of T-401 (written before the test)
PREREG = {
    "primary": "orders per customer over 4 weeks; launch needs the 95% interval above zero",
    "latency_p95_s_max": 5.0,          # Luqma's p95 response time, seconds
    "cost_per_conversation_max": 0.12,  # SAR, treatment
    "complaints_upper_max": 1.0,        # per 1,000 orders, upper 95% bound of the difference
    "wrong_info_upper_max": 0.3,        # per 1,000 orders, upper 95% bound of the difference: the HARM guardrail
    "rule": "Stop if the harm guardrail fails. Otherwise launch if the primary interval is above zero and every "
            "guardrail holds; iterate if a non-harm guardrail fails.",
}

# %% [markdown]
# ## 1 · The primary metric (5')
#
# ✏️ **Exercise** · Write `primary(weekly)`: orders per customer over the four weeks, treatment minus control,
# with its 95% interval and the relative lift. Return a dict with `diff`, `lo`, `hi`, `rel`.

# %%
def diff_ci(a: np.ndarray, b: np.ndarray) -> dict:
    d = a.mean() - b.mean()
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return {"diff": float(d), "lo": float(d - 1.96 * se), "hi": float(d + 1.96 * se), "rel": float(d / b.mean())}


def primary(weekly: pd.DataFrame) -> dict:
    # BEGIN SOLUTION
    per = weekly.groupby(["customer_id", "variant"]).orders.sum().reset_index()
    return diff_ci(per.orders[per.variant == "treatment"].to_numpy(float),
                   per.orders[per.variant == "control"].to_numpy(float))
    # END SOLUTION


# %%
try:
    PRIMARY = primary(weekly)
except NotImplementedError:
    PRIMARY = U.reference("d4_1_primary")
U.keep("d4_1_primary", PRIMARY)
print({k: round(v, 4) for k, v in PRIMARY.items()})
U.check(PRIMARY["diff"] > 0, "customers with Luqma order more (full mode: the interval is above zero)")

# %% [markdown]
# ## 2 · Latency and cost (5')
#
# ✏️ **Exercise** · Fill `ops(convs)`: one row per variant with the p50 and p95 response time in seconds and the
# mean cost per conversation in SAR.

# %%
def ops(convs: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    g = convs.groupby("variant")
    return pd.DataFrame({"p50_s": g.latency_s.quantile(0.5), "p95_s": g.latency_s.quantile(0.95),
                         "cost_per_conversation": g.cost_sar.mean(), "escalated": g.escalated.mean()})
    # END SOLUTION


# %%
try:
    OPS = ops(convs)
except NotImplementedError:
    OPS = U.reference("d4_1_ops")
U.keep("d4_1_ops", OPS)
print(OPS.round(3))
latency_ok = OPS.loc["treatment", "p95_s"] <= PREREG["latency_p95_s_max"]
cost_ok = OPS.loc["treatment", "cost_per_conversation"] <= PREREG["cost_per_conversation_max"]
U.check(latency_ok and cost_ok, "latency and cost guardrails hold")

# %% [markdown]
# 🔍 **Look at** `escalated`: the share of conversations handed to a human agent. Luqma escalates less. That is
# good for cost, and it is also how a wrong answer can reach a customer without a person in between.
#
# ## 3 · Complaints and wrong-information complaints (6')
#
# Complaints are counted per order, but customers were randomised: compute the rate per 1,000 orders as a ratio
# metric over customers, with the delta method of Lab 2.3.
#
# ✏️ **Exercise** · Write `rate_diff(flag)`: for an order-level flag column, the treatment minus control rate per
# 1,000 orders, with a delta-method 95% interval over customers.

# %%
per_c = orders.groupby(["customer_id", "variant"]).agg(n=("complaint", "size"), complaint=("complaint", "sum"),
                                                       wrong_info=("wrong_info_complaint", "sum")).reset_index()


def rate_diff(flag: str) -> dict:
    # BEGIN SOLUTION
    out = {}
    for arm in ("treatment", "control"):
        d = per_c[per_c.variant == arm]
        o, s = d[flag].to_numpy(float), d.n.to_numpy(float)
        r = o.sum() / s.sum()
        c = np.cov(o, s, ddof=1)
        out[arm] = (r, (c[0, 0] - 2 * r * c[0, 1] + r ** 2 * c[1, 1]) / (len(o) * s.mean() ** 2))
    diff = (out["treatment"][0] - out["control"][0]) * 1000
    se = np.sqrt(out["treatment"][1] + out["control"][1]) * 1000
    return {"control": out["control"][0] * 1000, "treatment": out["treatment"][0] * 1000,
            "diff": float(diff), "lo": float(diff - 1.96 * se), "hi": float(diff + 1.96 * se)}
    # END SOLUTION


# %%
try:
    HARM = {"complaint": rate_diff("complaint"), "wrong_info": rate_diff("wrong_info")}
except NotImplementedError:
    HARM = U.reference("d4_1_harm")
U.keep("d4_1_harm", HARM)
print(pd.DataFrame(HARM).T.round(3))
complaints_ok = HARM["complaint"]["hi"] <= PREREG["complaints_upper_max"]
harm_ok = HARM["wrong_info"]["hi"] <= PREREG["wrong_info_upper_max"]
print("complaints guardrail holds:", complaints_ok, "| harm guardrail holds:", harm_ok)
U.check(not harm_ok, "the wrong-information guardrail fails")

# %% [markdown]
# ## 4 · The lift week by week (5')
#
# ✏️ **Exercise** · Write `by_week(weekly)`: one row per week with the relative lift in orders per customer and
# its 95% interval.

# %%
def by_week(weekly: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    rows = {}
    for w, d in weekly.groupby("week"):
        r = diff_ci(d.orders[d.variant == "treatment"].to_numpy(float), d.orders[d.variant == "control"].to_numpy(float))
        base = d.orders[d.variant == "control"].mean()
        rows[w] = {"rel": r["rel"], "rel_lo": r["lo"] / base, "rel_hi": r["hi"] / base}
    return pd.DataFrame(rows).T
    # END SOLUTION


# %%
try:
    WEEKS = by_week(weekly)
except NotImplementedError:
    WEEKS = U.reference("d4_1_weeks")
U.keep("d4_1_weeks", WEEKS)
print(WEEKS.round(4))
U.check(WEEKS.rel.iloc[0] > 2 * max(WEEKS.rel.iloc[-1], 0.001), "the lift fades: novelty")

# %% [markdown]
# ## 5 · The decision (4')
#
# ✏️ **Exercise** · Apply the pre-registered rule and fill `decision()` with `decision` (launch, iterate or stop)
# and a `reason` of two sentences that names the guardrail and the novelty finding.

# %%
def decision() -> dict:
    # BEGIN SOLUTION
    w = HARM["wrong_info"]
    return {"decision": "stop",
            "reason": f"Wrong ingredient or allergen complaints rose from {w['control']:.2f} to {w['treatment']:.2f} per "
                      f"1,000 orders (upper bound +{w['hi']:.2f} against a limit of +0.30), so the harm guardrail fails "
                      f"and the rule says stop. The orders lift is real but fades from {WEEKS.rel.iloc[0]:.1%} in week 1 "
                      f"to {WEEKS.rel.iloc[-1]:.1%} in week 4, so even without the harm it would not justify launch "
                      f"on four weeks of data."}
    # END SOLUTION


# %%
try:
    DECISION = decision()
except NotImplementedError:
    DECISION = U.reference("d4_1_decision")
U.keep("d4_1_decision", DECISION)
print(DECISION["decision"].upper(), "|", DECISION["reason"])
U.check(DECISION["decision"] == "stop", "harm overrides the primary metric")

# %% [markdown]
# ## ✱ Stretch · Where is the harm?
#
# Merge the city from `weekly` into the orders and compute the wrong-information rate by city and arm. Is the harm
# everywhere, or concentrated? Write the one question you would put to the Luqma team.

# %% [markdown]
# ## Checkpoint
#
# 1. Why is the harm guardrail judged on the upper bound, not the estimate? <details><summary>Answer</summary>The
#    test must show the harm is below the limit; "not significantly worse" is not evidence of safety.</details>
# 2. The lift is 5.8% in week 1 and -0.5% in week 4. What do you report? <details><summary>Answer</summary>The
#    weekly pattern, and the settled effect of the last weeks as the long-run estimate, not the four-week
#    average.</details>
# 3. Which national reference asks for this kind of monitoring of a generative AI feature? <details><summary>
#    Answer</summary>The SDAIA Generative AI Guidelines, which name misinformation among the risks to assess and
#    call for monitoring and human supervision.</details>
#
# **Carry forward.** Capstone change C2 is Luqma with an allergen checker.
