# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2"]
# ///
"""Write the small, committed files of the Sufrah case study into labs/data/ (fixed seeds).

    uv run python prepare_data.py

The large tables (the T-101 event stream, the Luqma test, the simulators) are not files: sufrah.py
generates them on the fly with fixed seeds. This script writes what the labs read as files:
the three tests of Lab 1.2, the data inventory of Lab 1.3, the pre-registration of T-101 (Lab 4.3),
the 20 segment results of Lab 4.2, the five write-ups of Lab 4.4 and the capstone changes.
Running it twice gives the same bytes.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent / "data"


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def write_csv(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, lineterminator="\n")


def registry() -> None:
    write_json(DATA / "tests_registry.json", {"tests": [
        {"id": "T-101", "name": "AI-ranked search", "owner": "Yazeed Al-Hamdan", "unit": "customer",
         "split": "50/50", "days": 28, "labs": ["1.1", "1.3", "1.4", "2.1", "2.2", "2.3", "2.4", "4.3"]},
        {"id": "T-201", "name": "Home page A/A", "owner": "Rawan Al-Mubarak", "unit": "customer", "split": "50/50",
         "days": 14, "labs": ["1.2"]},
        {"id": "T-202", "name": "Reorder button", "owner": "Ruba Kamal", "unit": "customer", "split": "50/50",
         "days": 14, "labs": ["1.2"]},
        {"id": "T-203", "name": "New checkout page", "owner": "Ruba Kamal", "unit": "customer", "split": "50/50",
         "days": 14, "labs": ["1.2"]},
        {"id": "T-205", "name": "Menu photos", "owner": "Ruba Kamal", "unit": "customer", "split": "50/50",
         "days": 21, "labs": ["4.2"]},
        {"id": "T-301", "name": "Priority dispatch", "owner": "Joud Al-Fahad", "unit": "customer, then city-hour",
         "split": "50/50", "days": 14, "labs": ["3.3", "3.4"]},
        {"id": "T-401", "name": "Luqma chat assistant", "owner": "Rawan Al-Mubarak", "unit": "customer",
         "split": "50/50", "days": 28, "labs": ["4.1"]},
    ]})


def srm_tests() -> None:
    """Daily assignment logs of three tests. T-203 loses treatment users on Android build 7.4."""
    rng = np.random.default_rng(1202)
    rows = []
    builds = {"ios": ["17.2", "17.3"], "android": ["7.3", "7.4"], "web": ["web"]}
    share = {"ios": 0.45, "android": 0.45, "web": 0.10}
    for test in ("T-201", "T-202", "T-203"):
        for day in range(14):
            daily = rng.poisson(7200)
            for platform, builds_p in builds.items():
                for b in builds_p:
                    n = rng.binomial(daily, share[platform] / len(builds_p))
                    t = rng.binomial(n, 0.5)
                    c = n - t
                    if test == "T-203" and b == "7.4":
                        t = rng.binomial(t, 0.86)        # the new checkout crashes before it logs
                    rows += [(test, day, platform, b, "control", c), (test, day, platform, b, "treatment", t)]
    write_csv(DATA / "srm_tests.csv", pd.DataFrame(rows, columns=["test_id", "day", "platform", "app_build",
                                                                  "variant", "users"]))


def inventory() -> None:
    """Fields the T-101 analysis could use, with Sufrah's classification and the purpose of collection."""
    rows = [
        ("customer_id", "Pseudonymous customer key", "Restricted", "service delivery; product improvement", "yes"),
        ("city", "City of the delivery address", "Restricted", "service delivery; product improvement", "yes"),
        ("platform", "App platform and build", "Public", "product improvement", "yes"),
        ("order_value", "Basket value in SAR", "Restricted", "service delivery; product improvement", "yes"),
        ("search_latency_ms", "Time to show search results", "Public", "product improvement", "yes"),
        ("inference_cost_sar", "Model cost per search", "Restricted", "product improvement", "yes"),
        ("complaint_category", "Category of a complaint", "Restricted", "customer support; product improvement", "yes"),
        ("search_query_text", "The words a customer typed", "Restricted", "service delivery", "no"),
        ("complaint_text", "Free text of a complaint", "Restricted", "customer support", "no"),
        ("delivery_lat_lon", "Exact delivery coordinates", "Restricted", "service delivery", "no"),
        ("phone_number", "Customer phone number", "Restricted", "service delivery", "no"),
        ("allergy_profile", "Allergies the customer declared", "Secret", "service delivery (health data)", "no"),
    ]
    df = pd.DataFrame(rows, columns=["field", "description", "classification", "collected_for", "_allowed"])
    write_csv(DATA / "data_inventory.csv", df.drop(columns="_allowed"))
    write_json(DATA / "reference" / "data_allowed.full.json", sorted(df.field[df._allowed == "yes"]))
    write_json(DATA / "reference" / "data_allowed.quick.json", sorted(df.field[df._allowed == "yes"]))


def preregistration() -> None:
    write_json(DATA / "preregistration_T101.json", {
        "test_id": "T-101",
        "change": "AI-ranked search results in place of the keyword ranking",
        "decision": "Launch the AI ranking to all customers, or not",
        "unit": "customer, randomised 50/50 on day 0",
        "population": "triggered customers: those who searched at least once during the test",
        "duration_days": 28,
        "primary": {"metric": "orders per triggered customer over the 28 days", "mde_relative": 0.02,
                    "analysis": "difference in means with regression adjustment on the same metric over the 28 pre-period days; 95% interval"},
        "guardrails": [
            {"metric": "search latency p95 (ms), treatment minus control", "threshold": 300, "direction": "at most"},
            {"metric": "inference cost per 1,000 searches (SAR), treatment", "threshold": 8.0, "direction": "at most"},
            {"metric": "complaints per 1,000 orders, upper 95% bound of the difference", "threshold": 1.0,
             "direction": "at most", "harm": True},
            {"metric": "revenue per triggered customer, lower 95% bound of the relative difference",
             "threshold": -0.01, "direction": "at least"},
        ],
        "decision_rule": "Launch if the primary interval is above zero and every guardrail holds. Iterate if the primary "
                         "interval is above zero and a non-harm guardrail fails. Stop if the primary interval includes "
                         "zero or falls below it, or if the harm guardrail fails.",
        "owner": "Yazeed Al-Hamdan", "reviewer": "Rawan Al-Mubarak",
    })


SEGMENTS = ["Burgers", "Shawarma", "Mandi", "Pizza", "Coffee", "Kabsa", "Sushi", "Grills", "Desserts", "Bakery",
            "Indian", "Chinese", "Healthy", "Seafood", "Breakfast", "Juices", "Lebanese", "Turkish", "Italian",
            "Groceries"]


def _segment_rows(seed: int) -> list:
    rng = np.random.default_rng(seed)
    rows = []
    for s in SEGMENTS:
        n_c, n_t = rng.integers(2500, 9000), 0
        n_t = int(rng.binomial(2 * n_c, 0.5))
        n_c = int(2 * n_c - n_t)
        base = rng.uniform(3.0, 6.0)
        lift = 0.07 if s in ("Mandi", "Coffee") else 0.0
        yc = rng.poisson(rng.gamma(0.9, base / 0.9, n_c))
        yt = rng.poisson(rng.gamma(0.9, base * (1 + lift) / 0.9, n_t))
        rows.append((s, n_c, n_t, round(yc.mean(), 4), round(yt.mean(), 4), round(yc.std(ddof=1), 4),
                     round(yt.std(ddof=1), 4)))
    return rows


def segments(seed: int = 2205) -> None:
    """T-205, menu photos: 20 cuisine segments; only Mandi and Coffee have a true lift (7%).

    The seed is the first from 2205 whose uncorrected tests show two false wins beside the two true
    ones: the situation the lab is about. The search is deterministic.
    """
    from math import erf, sqrt
    while True:
        rows = _segment_rows(seed)
        p = {}
        for s, n_c, n_t, mc, mt, sc, st in rows:
            z = (mt - mc) / sqrt(sc ** 2 / n_c + st ** 2 / n_t)
            p[s] = 1 - erf(abs(z) / sqrt(2))
        wins = {s for s, v in p.items() if v < 0.05}
        false_p = [v for s, v in p.items() if s in wins - {"Mandi", "Coffee"}]
        if {"Mandi", "Coffee"} <= wins and len(wins) == 4 and max(p["Mandi"], p["Coffee"]) < 0.004 and min(false_p) > 0.012:
            break
        seed += 1
    write_csv(DATA / "segments_T205.csv", pd.DataFrame(rows, columns=["segment", "n_control", "n_treatment",
                                                                      "mean_control", "mean_treatment",
                                                                      "sd_control", "sd_treatment"]))


WRITEUPS = {
    "W1": ("One-tap reorder banner", "Ruba Kamal",
           "The banner raised orders per customer by 2.1% (95% interval 0.9% to 3.3%) over 14 days. We recommend "
           "launch. Assignment: 50/50 by customer. Users: control 49,088, treatment 50,912.",
           {"users": {"control": 49088, "treatment": 50912}, "lift": 0.021, "ci": [0.009, 0.033]},
           "iterate", "sample ratio mismatch: 50,912 against 49,088 has a chi-square p-value far below 0.001; the "
           "result cannot be trusted until the cause is found and the test is rerun"),
    "W2": ("Dish of the day carousel", "Ruba Kamal",
           "We checked the dashboard every morning. On day 9 the lift in orders per customer reached p = 0.03, so we "
           "stopped the test and recommend launch. The pre-registration planned 28 days.",
           {"daily_z": None, "stopped_day": 9, "planned_days": 28}, "stop",
           "peeking: a stop on the first daily p below 0.05 is not the pre-registered test; the day-28 analysis "
           "planned in the pre-registration shows no effect"),
    "W3": ("Personalised home feed", "Ruba Kamal",
           "Over four weeks orders per customer rose by 3.0% (95% interval 1.6% to 4.4%). Guardrails held. We "
           "recommend launch.",
           {"weekly_lift": [0.071, 0.028, 0.009, 0.002], "weekly_se": [0.008, 0.008, 0.008, 0.008]}, "iterate",
           "novelty decay: the lift falls from 7.1% in week 1 to 0.2% in week 4; the settled effect is not shown "
           "to be above zero, so run longer before deciding"),
    "W4": ("Faster restaurant pages", "Ruba Kamal",
           "Pages load 30% faster. Orders per customer rose by 1.2% (95% interval 0.5% to 1.9%), adjusted with 28 "
           "pre-period days. Sample ratio p = 0.62. Latency, cost and complaint guardrails held. We recommend launch.",
           {"users": {"control": 61210, "treatment": 61105}, "lift": 0.012, "ci": [0.005, 0.019]}, "launch",
           "clean: trustworthy assignment, pre-registered analysis, guardrails held"),
    "W5": ("Tighter courier batching", "Joud Al-Fahad",
           "Batching two orders per trip cut delivery cost per order by 6% (95% interval 4% to 8%) in a city-by-hour "
           "switchback. Courier earnings per online hour fell by 4.2% (95% interval -5.9% to -2.5%); the guardrail "
           "allowed -2%. We recommend launch because the cost saving is large.",
           {"cost_change": -0.06, "earnings_change": -0.042, "earnings_ci": [-0.059, -0.025], "earnings_threshold": -0.02},
           "stop", "harm guardrail: courier earnings fell beyond the pre-registered threshold; the board stops a "
           "test whose harm guardrail worsens"),
}


def writeups() -> None:
    rng = np.random.default_rng(4404)
    decisions = {}
    for wid, (title, author, text, data, decision, reason) in WRITEUPS.items():
        if wid == "W2":   # a null test monitored daily: z drifts, crosses 1.96 once around day 9
            for _ in range(200_000):   # the first null path that crosses on day 9 only and ends near zero
                z = np.cumsum(rng.standard_normal(28)) / np.sqrt(np.arange(1, 29))
                if 2.1 < z[8] < 2.4 and (np.abs(z[:8]) < 1.96).all() and abs(z[-1]) < 0.8:
                    break
            data = dict(data, daily_z=[round(float(v), 3) for v in z])
        md = (f"# {wid} · {title}\n\nAuthor: {author}. Test unit: customer.\n\n## Summary\n\n{text}\n\n"
              f"## Data\n\nThe numbers behind this write-up are in `{wid}.json`.\n")
        (DATA / "writeups").mkdir(parents=True, exist_ok=True)
        (DATA / "writeups" / f"{wid}.md").write_text(md, encoding="utf-8", newline="\n")
        write_json(DATA / "writeups" / f"{wid}.json", data)
        decisions[wid] = {"decision": decision, "fault": reason}
    for mode in ("full", "quick"):
        write_json(DATA / "reference" / f"review_decisions.{mode}.json", decisions)


def capstone_changes() -> None:
    write_json(DATA / "capstone_changes.json", {"changes": [
        {"id": "C1", "name": "AI-written dish descriptions", "owner": "Yazeed Al-Hamdan",
         "goal": "more orders from menus that had no description", "customers": 160000,
         "harm": "a description that names an ingredient the dish does not have"},
        {"id": "C2", "name": "Luqma with an allergen checker", "owner": "Rawan Al-Mubarak",
         "goal": "keep Luqma's lift without the wrong-information complaints of T-401", "customers": 120000,
         "harm": "a wrong ingredient or allergen answer"},
        {"id": "C3", "name": "AI-ranked restaurant list on the home page", "owner": "Yazeed Al-Hamdan",
         "goal": "more first orders in a session", "customers": 200000,
         "harm": "small restaurants pushed off the first screen (share of orders to restaurants under 20 orders a day)"},
    ]})


if __name__ == "__main__":
    registry()
    srm_tests()
    inventory()
    preregistration()
    segments()
    writeups()
    capstone_changes()
    for p in sorted(DATA.rglob("*")):
        if p.is_file() and "reference" not in p.parts:
            print(f"{p.relative_to(DATA.parent)}  {p.stat().st_size:,} bytes")
