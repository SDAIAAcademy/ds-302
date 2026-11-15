# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2"]
# ///
# %% [markdown]
# # Lab 1.3 · A metric spec for AI-ranked search
#
# Day 1 · Session 3 (Metrics for AI features) · 25 min.
#
# Yazeed Al-Hamdan, Sufrah's search product manager, wants to replace keyword ranking with an AI ranking that
# calls a model on every search. Before T-101 starts, you write its metric spec: one primary metric, and
# guardrails for what an AI feature adds (latency, cost and harm), with thresholds taken from the 7-day ramp.
# Then Waleed Al-Sharif, the data protection officer, asks which fields the analysis will read.
#
# **AI policy: AI-tutor.** The choices are yours; an assistant may challenge them.
#
# **Reference state.** `U.ramp()` (searches of the ramp, 5% on the new ranking) and `data/data_inventory.csv`.
# Nothing from another lab.
#
# **Tasks**
# - [ ] 1 · Baselines from the ramp: latency, cost, conversion, complaints (6')
# - [ ] 2 · The primary metric and its unit (4')
# - [ ] 3 · Three guardrails with thresholds and directions (6')
# - [ ] 4 · The data inventory: which fields the test may use (6')
# - [ ] 5 · Save the metric spec (3')
# - [ ] ✱ Stretch · Add a guardrail that protects small restaurants and say how you would measure it

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

ramp = U.ramp()
print(ramp.groupby("variant").size())

# %% [markdown]
# ## 1 · Baselines from the ramp (6')
#
# ✏️ **Exercise** · Write `baselines(ramp)`: one row per variant with `p50_ms` and `p95_ms` (search latency),
# `cost_per_1000` (SAR per 1,000 searches), `order_rate` (share of searches followed by an order in the same
# session) and `complaints_per_1000_orders`.

# %%
def baselines(ramp: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    g = ramp.groupby("variant")
    return pd.DataFrame({
        "p50_ms": g.latency_ms.quantile(0.50),
        "p95_ms": g.latency_ms.quantile(0.95),
        "cost_per_1000": g.cost_sar.mean() * 1000,
        "order_rate": g.ordered.mean(),
        "complaints_per_1000_orders": g.complaint.sum() / g.ordered.sum() * 1000,
    })
    # END SOLUTION


# %%
try:
    base = baselines(ramp)
except NotImplementedError:
    base = U.reference("d1_3_baselines")
U.keep("d1_3_baselines", base)
print(base.round(3))
U.check(base.loc["treatment", "p95_ms"] > base.loc["control", "p95_ms"], "the AI ranking is slower at the tail")

# %% [markdown]
# 🔍 **Look at** the order rate. On a few thousand ramp searches the difference is noise; the ramp is for latency and
# cost, which are visible at once. The effect on orders needs the test.
#
# ## 2 · The primary metric (4')
#
# The primary metric answers the decision ("launch the AI ranking or not") and can be moved by the change in 28
# days. It is computed per **randomisation unit** (the customer) over the **triggered** population.
#
# ✏️ **Exercise** · Fill `primary()`: a dict with `name`, `unit`, `population`, `window_days` and `why` (one
# sentence).

# %%
def primary() -> dict:
    # BEGIN SOLUTION
    return {"name": "orders per customer", "unit": "customer", "population": "triggered: searched at least once",
            "window_days": 28,
            "why": "Orders are what the ranking is meant to change, and orders per customer is far less noisy than "
                   "revenue per customer, which group orders dominate."}
    # END SOLUTION


# %%
try:
    PRIMARY = primary()
except NotImplementedError:
    PRIMARY = U.reference("d1_3_primary")
U.keep("d1_3_primary", PRIMARY)
print(json.dumps(PRIMARY, indent=1))
U.check(PRIMARY["unit"] == "customer" and "trigger" in PRIMARY["population"], "per customer, over the triggered")

# %% [markdown]
# ## 3 · Guardrails (6')
#
# A guardrail is not a second primary metric: it is a line the change must not cross, whatever the primary
# says. Each has a metric, a direction, a threshold you can defend from the baselines, and whether it measures
# harm (the review board stops a test whose harm guardrail worsens).
#
# ✏️ **Exercise** · Fill `guardrails()`: a list of at least three dicts with `metric`, `kind` (`latency`, `cost`
# or `harm`), `threshold` (a number), `direction` (`at most` or `at least`) and `harm` (true or false).

# %%
def guardrails() -> list:
    # BEGIN SOLUTION
    return [
        {"metric": "search latency p95 (ms), treatment minus control", "kind": "latency", "threshold": 300,
         "direction": "at most", "harm": False,
         "why": "Ramp shows about +400 ms at p95; the app's own budget for a search screen is +300 ms"},
        {"metric": "inference cost per 1,000 searches (SAR), treatment", "kind": "cost", "threshold": 8.0,
         "direction": "at most", "harm": False, "why": "Ramp shows about 5.8; 8 leaves room for longer queries"},
        {"metric": "complaints per 1,000 orders, upper 95% bound of the difference", "kind": "harm",
         "threshold": 1.0, "direction": "at most", "harm": True,
         "why": "Baseline is about 4.5 per 1,000 orders; a rise above 1 would be a fifth more complaints"},
    ]
    # END SOLUTION


# %%
try:
    GUARDRAILS = guardrails()
except NotImplementedError:
    GUARDRAILS = U.reference("d1_3_guardrails")
U.keep("d1_3_guardrails", GUARDRAILS)
print(pd.DataFrame(GUARDRAILS)[["kind", "metric", "direction", "threshold", "harm"]])
kinds = {g["kind"] for g in GUARDRAILS}
U.check({"latency", "cost", "harm"} <= kinds and all(isinstance(g["threshold"], (int, float)) for g in GUARDRAILS),
        "latency, cost and harm, each with a numeric threshold")
U.check(any(g["harm"] for g in GUARDRAILS), "at least one guardrail is marked as harm")

# %% [markdown]
# ## 4 · Which fields may the test use? (6')
#
# The Personal Data Protection Law lets a controller process personal data for the purposes for which it was
# collected, and asks that the content be limited to the minimum necessary for that purpose. Sufrah labels its
# fields with the four levels of the NDMO Data Classification Policy (Top Secret, Secret, Restricted, Public),
# and its privacy notice lists "product improvement" as a purpose of collection.
#
# ✏️ **Exercise** · Fill `allowed_fields(inventory)` with the set of fields the T-101 analysis may read: the
# fields collected for product improvement that the metric spec needs, and nothing more sensitive than needed.

# %%
inventory = U.csv("data_inventory")
print(inventory.to_string(index=False))


def allowed_fields(inventory: pd.DataFrame) -> set:
    # BEGIN SOLUTION
    return set(inventory.loc[inventory.collected_for.str.contains("product improvement")
                             & (inventory.classification != "Secret"), "field"])
    # END SOLUTION


# %%
try:
    ALLOWED = allowed_fields(inventory)
except NotImplementedError:
    ALLOWED = set(U.reference("data_allowed"))
expected = set(json.loads((U.REF / f"data_allowed.{U.MODE}.json").read_text(encoding="utf-8")))
print("allowed:", sorted(ALLOWED))
print("missing:", sorted(expected - ALLOWED), "| not needed or not allowed:", sorted(ALLOWED - expected))
U.check(ALLOWED == expected, "the same fields as the data protection officer's answer")

# %% [markdown]
# 🔍 **Look at** what you left out. The search text and the complaint text were collected to serve the customer,
# not to analyse a test, and the categories carry what the metrics need. Exact coordinates are more than the
# minimum: the city is enough. The allergy profile is health data.
#
# ## 5 · Save the spec (3')

# %%
spec = {"test_id": "T-101", "primary": PRIMARY, "guardrails": GUARDRAILS, "fields": sorted(ALLOWED),
        "baselines": base.round(4).to_dict(orient="index")}
U.save("T101_metric_spec.json", json.dumps(spec, indent=1, ensure_ascii=False))
U.check(len(spec["fields"]) >= 5, "the spec is saved with its fields")

# %% [markdown]
# ## ✱ Stretch · A guardrail for small restaurants
#
# An AI ranking may push small restaurants down the list. Write the guardrail: the metric (for example the share
# of orders going to restaurants with fewer than 20 orders a day), its unit, its threshold and why. Which table
# would it need that T-101's stream does not have?

# %% [markdown]
# ## Checkpoint
#
# 1. The AI ranking lifts orders by 3% and adds 450 ms at p95 against a threshold of 300. What does the spec
#    say? <details><summary>Answer</summary>The guardrail fails: not a launch as is, whatever the primary says.
#    The decision rule says what follows (here: iterate).</details>
# 2. Why is "revenue per customer" a weaker primary than "orders per customer" here? <details><summary>Answer
#    </summary>Group orders make revenue far noisier, so the same test detects a much larger effect only.</details>
# 3. Why may the analysis not read the search text, though it is Restricted like the city? <details><summary>
#    Answer</summary>Classification sets how data is protected; purpose and minimum necessity set whether this use
#    is allowed. The text is not needed for any metric.</details>
#
# **Carry forward.** Lab 4.3 reads the pre-registration of T-101, which uses the same guardrails.
