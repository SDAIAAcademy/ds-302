"""Shared helpers for the labs of Online Experiments and A/B Testing (SDAIA Academy, DS-302).

Sufrah is a fictional food-delivery marketplace in six Saudi cities. Everything here is synthetic
and deterministic: the same seed gives the same customers, orders and simulations on every run.

    import sufrah as U
    S = U.stream()          # the event stream of test T-101 (AI-ranked search), as DataFrames
    U.sql("select count(*) from orders", S)

Quick mode (SUFRAH_QUICK=1) shrinks the customer base and the number of simulations, so every
solution runs in a few minutes on a laptop processor. Numbers on the slides come from full mode.
"""

from __future__ import annotations

import json
import math
import os
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

LABS = Path(__file__).resolve().parent
DATA = LABS / "data"
REF = DATA / "reference"
ART = LABS / "artifacts"

QUICK = os.environ.get("SUFRAH_QUICK", "0") == "1"
MODE = "quick" if QUICK else "full"
STRICT = os.environ.get("SUFRAH_STRICT", "0") == "1"      # solution runs: a failed check stops the run
WRITE_REF = os.environ.get("SUFRAH_WRITE_REF", "0") == "1"  # the trainer's run that writes data/reference/

CITIES = ["Riyadh", "Jeddah", "Dammam", "Makkah", "Madinah", "Abha"]
CITY_SHARE = np.array([0.32, 0.24, 0.14, 0.12, 0.10, 0.08])
CITY_RATE = np.array([0.205, 0.190, 0.175, 0.160, 0.150, 0.135])   # orders per customer per day
CITY_VALUE = np.array([66.0, 60.0, 56.0, 50.0, 48.0, 44.0])        # median basket, SAR
PLATFORMS = ["ios", "android", "web"]
DAYS = 28                       # pre-period and test period, days each
N_FULL, N_QUICK = 200_000, 30_000


def pick(full, quick):
    """The full value, or the small one in quick mode."""
    return quick if QUICK else full


def check(ok: bool, what: str) -> bool:
    """Print a self-check. In a solution run (SUFRAH_STRICT=1) a failed check stops the run."""
    print(("✅ " if ok else "❌ ") + what)
    if STRICT and not ok:
        raise AssertionError(what)
    return bool(ok)


def _jsonable(v):
    if isinstance(v, dict):
        return {str(k): _jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, np.ndarray):
        return [_jsonable(x) for x in v.tolist()]
    if isinstance(v, pd.DataFrame):
        return {"__frame__": json.loads(v.to_json(orient="split"))}
    return v


def _unjson(v):
    if isinstance(v, dict) and "__frame__" in v:
        f = v["__frame__"]
        return pd.DataFrame(f["data"], index=f["index"], columns=f["columns"])
    if isinstance(v, dict):
        return {k: _unjson(x) for k, x in v.items()}
    return v


def keep(name: str, value):
    """Record a result of the solution run as the reference for the safety nets (trainer run only)."""
    if WRITE_REF:
        REF.mkdir(parents=True, exist_ok=True)
        path = REF / f"{name}.{MODE}.json"
        path.write_text(json.dumps(_jsonable(value), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return value


def reference(name: str):
    """The reference result of an exercise, for a participant who skipped it."""
    path = REF / f"{name}.{MODE}.json"
    print(f"↪ using the reference result for {name} (data/reference/{path.name})")
    return _unjson(json.loads(path.read_text(encoding="utf-8")))


def save(name: str, text: str) -> Path:
    """Write a lab's output (a memo, a log) to labs/artifacts/."""
    ART.mkdir(exist_ok=True)
    path = ART / name
    path.write_text(text, encoding="utf-8")
    print("wrote", path.relative_to(LABS))
    return path


def js(name: str):
    """A JSON file from labs/data/."""
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


def csv(name: str) -> pd.DataFrame:
    """A CSV file from labs/data/."""
    return pd.read_csv(DATA / f"{name}.csv")


def style():
    """Matplotlib with the course's defaults; returns pyplot."""
    import matplotlib
    try:
        get_ipython()  # noqa: F821  (inside a notebook: keep its backend)
    except NameError:
        matplotlib.use("Agg")       # run as a script: draw to nothing
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.figsize": (8, 3.6), "axes.spines.top": False, "axes.spines.right": False,
                         "axes.grid": True, "grid.alpha": 0.3, "font.size": 10})
    return plt


def sql(query: str, tables: dict | None = None) -> pd.DataFrame:
    """Run a DuckDB query over DataFrames (by default the T-101 stream) and return a DataFrame."""
    import duckdb
    con = duckdb.connect()
    for name, frame in (tables if tables is not None else stream()).items():
        if isinstance(frame, pd.DataFrame):
            con.register(name, frame)
    out = con.execute(query).df()
    con.close()
    return out


# ---------------------------------------------------------------------------------------------
# Customers and the T-101 event stream (AI-ranked search)
# ---------------------------------------------------------------------------------------------

def _basket_values(rng, mu, size_like=None):
    """Order values in SAR: a lognormal basket, and about one order in a hundred a group order."""
    n = len(mu)
    v = np.exp(mu + 0.55 * rng.standard_normal(n))
    group = rng.random(n) < 0.010
    v[group] *= 4.0 * (1.0 + rng.pareto(1.6, group.sum()))
    return np.round(np.minimum(v, 30_000.0), 2)


@lru_cache(maxsize=None)
def customers(n: int | None = None, seed: int = 302) -> pd.DataFrame:
    """The active customer base: city, platform and the latent habits that drive orders."""
    n = n or pick(N_FULL, N_QUICK)
    rng = np.random.default_rng(seed)
    city = rng.choice(6, n, p=CITY_SHARE)
    rate = rng.gamma(0.8, CITY_RATE[city] / 0.8)                 # orders per day
    conv = rng.beta(4, 12, n)                                     # orders per session
    searcher = rng.random(n) < 0.60
    p_search = np.where(searcher, rng.beta(1.2, 4.0, n), 0.0)     # share of sessions with a search
    return pd.DataFrame({
        "customer_id": np.arange(100001, 100001 + n),
        "city": np.array(CITIES)[city],
        "platform": rng.choice(PLATFORMS, n, p=[0.45, 0.45, 0.10]),
        "tenure_days": rng.integers(30, 1500, n),
        "_city": city,
        "_sessions_per_day": rate / conv,
        "_conv": conv,
        "_mu": np.log(CITY_VALUE[city]) + 0.35 * rng.standard_normal(n),
        "_p_search": p_search,
    })


@lru_cache(maxsize=None)
def stream(n: int | None = None, seed: int = 101, lift: float = 0.04) -> dict:
    """Test T-101, AI-ranked search: 28 pre-period days (days -28 to -1) and 28 test days (0 to 27).

    Customers are randomised 50/50 on day 0. A customer is exposed (triggered) at their first search
    of the test period. The new ranking raises the chance that a session ends in an order by `lift`
    for exposed customers after their exposure, and does nothing for anyone else.

    Returns a dict of DataFrames: customers, assignments, searches, sessions, orders. Columns that
    start with an underscore are the generator's latent values; the analysis never uses them.
    """
    c = customers(n)
    n = len(c)
    rng = np.random.default_rng(seed)
    variant = np.where(rng.random(n) < 0.5, "treatment", "control")
    treat = variant == "treatment"
    sp, conv, mu, ps = (c[k].to_numpy() for k in ("_sessions_per_day", "_conv", "_mu", "_p_search"))

    # pre-period
    s_pre = rng.poisson(DAYS * sp)
    o_pre = rng.binomial(s_pre, conv)
    # test period: sessions, searches, first search (exposure)
    s_test = rng.poisson(DAYS * sp)
    k_search = rng.binomial(s_test, ps)
    trig = k_search > 0
    u = rng.random(n)
    first = np.where(trig, np.floor(DAYS * (1 - (1 - u) ** (1 / np.maximum(k_search, 1)))), DAYS).astype(int)
    first = np.minimum(first, DAYS - 1)
    s_before = np.where(trig, rng.binomial(s_test, first / DAYS), s_test)
    s_after = s_test - s_before
    o_before = rng.binomial(s_before, conv)
    o_after0 = rng.binomial(s_after, conv)
    q = np.clip(conv * lift / (1 - conv), 0, 1)                   # coupling: extra orders under treatment
    o_extra = np.where(trig, rng.binomial(s_after - o_after0, q), 0)

    # order rows: segment 0 = pre, 1 = before exposure (or whole test), 2 = after exposure, 3 = extra
    seg_counts = np.stack([o_pre, o_before, o_after0, o_extra], axis=1)
    cust_idx = np.repeat(np.repeat(np.arange(n), 4), seg_counts.ravel())
    seg = np.repeat(np.tile(np.arange(4), n), seg_counts.ravel())
    lo = np.select([seg == 0, seg == 1], [-DAYS, 0], default=first[cust_idx])
    hi = np.select([seg == 0, seg == 1], [0, np.where(trig[cust_idx], first[cust_idx], DAYS)], default=DAYS)
    hi = np.maximum(hi, lo + 1)
    day = lo + np.floor(rng.random(len(seg)) * (hi - lo)).astype(int)
    value = _basket_values(rng, mu[cust_idx])
    complaint = rng.random(len(seg)) < 0.0045
    observed = (seg != 3) | treat[cust_idx]

    # potential outcomes per customer, test period (the generator's knowledge, for Lab 2.1)
    test_rows = seg >= 1
    y0 = np.bincount(cust_idx[test_rows & (seg != 3)], weights=value[test_rows & (seg != 3)], minlength=n)
    y1 = y0 + np.bincount(cust_idx[seg == 3], weights=value[seg == 3], minlength=n)

    ids = c["customer_id"].to_numpy()
    orders = pd.DataFrame({
        "order_id": 0, "customer_id": ids[cust_idx], "day": day, "value": value, "complaint": complaint,
    })[observed].sort_values(["day", "customer_id"], kind="stable").reset_index(drop=True)
    orders["order_id"] = np.arange(5_000_001, 5_000_001 + len(orders))

    # search events: the first at the exposure day, the rest after it
    ks = k_search[trig]
    s_idx = np.repeat(np.flatnonzero(trig), ks)
    rank = np.concatenate([np.arange(k) for k in ks]) if len(ks) else np.array([], int)
    s_day = np.where(rank == 0, first[s_idx],
                     first[s_idx] + np.floor(rng.random(len(s_idx)) * (DAYS - first[s_idx])).astype(int))
    t_s = treat[s_idx]
    latency = np.where(t_s, np.exp(np.log(540) + 0.42 * rng.standard_normal(len(s_idx))),
                       np.exp(np.log(380) + 0.35 * rng.standard_normal(len(s_idx))))
    cost = np.where(t_s, 0.0058, 0.0002) * (0.6 + 0.8 * rng.random(len(s_idx)))
    searches = pd.DataFrame({"search_id": np.arange(7_000_001, 7_000_001 + len(s_idx)),
                             "customer_id": ids[s_idx], "day": s_day, "latency_ms": np.round(latency).astype(int),
                             "cost_sar": np.round(cost, 5)}).sort_values(["day", "search_id"]).reset_index(drop=True)

    public = c[["customer_id", "city", "platform", "tenure_days"]].copy()
    assignments = pd.DataFrame({"customer_id": ids, "test_id": "T-101", "variant": variant, "assigned_day": 0})
    sessions = pd.DataFrame({"customer_id": ids, "sessions_pre": s_pre, "sessions_test": s_test})
    truth = pd.DataFrame({"customer_id": ids, "triggered": trig, "y0": np.round(y0, 2), "y1": np.round(y1, 2)})
    return {"customers": public, "assignments": assignments, "searches": searches, "sessions": sessions,
            "orders": orders, "_truth": truth}


def per_customer(S: dict | None = None) -> pd.DataFrame:
    """One row per T-101 customer: variant, city, platform, triggered, and pre and test totals."""
    S = S or stream()
    o = S["orders"]
    pre = o[o.day < 0].groupby("customer_id").agg(orders_pre=("order_id", "size"), revenue_pre=("value", "sum"))
    test = o[o.day >= 0].groupby("customer_id").agg(orders=("order_id", "size"), revenue=("value", "sum"),
                                                  complaints=("complaint", "sum"))
    first = S["searches"].groupby("customer_id").day.min().rename("exposed_day")
    df = (S["assignments"][["customer_id", "variant"]]
          .merge(S["customers"], on="customer_id")
          .merge(S["sessions"], on="customer_id")
          .merge(pre, on="customer_id", how="left").merge(test, on="customer_id", how="left")
          .merge(first, on="customer_id", how="left"))
    for col in ("orders_pre", "revenue_pre", "orders", "revenue", "complaints"):
        df[col] = df[col].fillna(0)
    df["triggered"] = df.exposed_day.notna()
    df["treat"] = (df.variant == "treatment").astype(int)
    return df


def ramp(seed: int = 7) -> pd.DataFrame:
    """Search events of the 7-day ramp before T-101: 5% of searches on the new ranking."""
    rng = np.random.default_rng(seed)
    n = pick(120_000, 40_000)
    treat = rng.random(n) < 0.05
    latency = np.where(treat, np.exp(np.log(540) + 0.42 * rng.standard_normal(n)),
                       np.exp(np.log(380) + 0.35 * rng.standard_normal(n)))
    cost = np.where(treat, 0.0058, 0.0002) * (0.6 + 0.8 * rng.random(n))
    ordered = rng.random(n) < np.where(treat, 0.262, 0.255)
    complaint = ordered & (rng.random(n) < 0.0045)
    return pd.DataFrame({"day": rng.integers(-7, 0, n), "variant": np.where(treat, "treatment", "control"),
                         "latency_ms": np.round(latency).astype(int), "cost_sar": np.round(cost, 5),
                         "ordered": ordered, "complaint": complaint})


# ---------------------------------------------------------------------------------------------
# Day 3: the daily-peeking simulator and the marketplace simulator
# ---------------------------------------------------------------------------------------------

def peek_sim(effect: float = 0.0, sims: int | None = None, days: int = DAYS, n_per_day: int = 3000,
             sd: float = 6.0, base: float = 5.0, seed: int = 31) -> dict:
    """Daily monitoring of a test on orders per customer (mean 5.0, sd 6.0).

    Each day `n_per_day` new customers join each arm. `effect` is the relative lift (0.016 is 1.6%).
    Returns {"est": sims x days cumulative difference in means, "se": its standard error per day,
    "z": est / se, "n": customers per arm by day}.
    """
    sims = sims or pick(4000, 1000)
    rng = np.random.default_rng(seed)
    daily_se = sd * math.sqrt(2.0 / n_per_day)
    d = effect * base + daily_se * rng.standard_normal((sims, days))
    k = np.arange(1, days + 1)
    est = np.cumsum(d, axis=1) / k
    se = daily_se / np.sqrt(k)
    return {"est": est, "se": se, "z": est / se, "n": n_per_day * k, "sd": sd, "base": base}


HOURS = 14              # operating hours per day in the marketplace simulator
HOUR_PROFILE = np.array([0.55, 0.85, 1.25, 1.10, 0.75, 0.60, 0.65, 0.85, 1.25, 1.55, 1.50, 1.15, 0.80, 0.55])


def dispatch_sim(assign: str = "customer", days: int = 14, seed: int = 33, p_treat: float = 0.5,
                 gain: float = 0.04, carry: float = 0.3, block_hours: int = 1, rng=None) -> pd.DataFrame:
    """The marketplace simulator: six cities, 14 operating hours a day, couriers shared by everyone.

    The dispatch change gives treated orders priority for the next free courier (a queue jump), and
    when a whole city-hour runs it, batching nearby orders adds `gain` to courier capacity.
    `assign` is "customer" (each order treated with probability p_treat), "all", "none" or
    "switchback" (each city and block of `block_hours` hours treated or not, at random).
    Wait spills over into the next hour by `carry`.

    Returns one row per city-hour and arm: city, day, hour, arm, sessions, orders, delivery_min
    (mean minutes from order to door), share_treated (of that city-hour's orders).
    """
    rng = rng or np.random.default_rng(seed)
    rows = []
    base_sessions = np.array([520, 430, 300, 260, 220, 170])        # per hour at profile 1.0
    couriers = np.round(base_sessions * 0.24 / 0.55 / 2.2)          # about 55% busy at an average hour
    for ci in range(6):
        backlog = 0.0
        blocks = rng.random((days, math.ceil(HOURS / block_hours))) < 0.5
        for d in range(days):
            for h in range(HOURS):
                if assign == "customer":
                    f = p_treat
                elif assign == "all":
                    f = 1.0
                elif assign == "none":
                    f = 0.0
                else:
                    f = 1.0 if blocks[d, h // block_hours] else 0.0
                sessions = rng.poisson(base_sessions[ci] * HOUR_PROFILE[h] * (1 + 0.08 * (d % 7 in (3, 4))))
                demand = sessions * 0.24
                capacity = couriers[ci] * 2.2 * (1 + gain * f * f) * (0.93 + 0.14 * rng.random())
                rho = min(demand / capacity, 0.96)
                r = 6.0 * rho                                       # mean residual work, minutes
                w_hi = r / (1 - f * rho) if f > 0 else 0.0
                w_lo = r / ((1 - f * rho) * (1 - rho))
                spill = carry * backlog
                for arm, share, w in (("treatment", f, w_hi), ("control", 1 - f, w_lo)):
                    if share <= 0:
                        continue
                    n_s = rng.binomial(sessions, share)
                    eta = 18 + w + spill
                    conv = 0.27 * math.exp(-(eta - 22) / 70)
                    n_o = rng.binomial(n_s, min(conv, 0.95))
                    mins = eta + (rng.normal(0, 6 / math.sqrt(max(n_o, 1))) if n_o else 0.0)
                    rows.append((CITIES[ci], d, h, arm, n_s, n_o, round(mins, 2) if n_o else np.nan, f))
                backlog = (f * w_hi + (1 - f) * w_lo) if f < 1 else w_hi
    return pd.DataFrame(rows, columns=["city", "day", "hour", "arm", "sessions", "orders", "delivery_min",
                                       "share_treated"])


# ---------------------------------------------------------------------------------------------
# Day 4: the Luqma chat-assistant test (T-401)
# ---------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def luqma(n: int | None = None, seed: int = 401) -> dict:
    """Test T-401: Luqma, the in-app chat assistant, against the old help menu, four weeks.

    Returns {"weekly": one row per customer and week (orders, conversations), "conversations": one row
    per conversation with the assistant or the help menu (latency, cost, escalated), "orders": one row
    per order with complaint flags}.
    """
    n = n or pick(120_000, 30_000)
    rng = np.random.default_rng(seed)
    city = rng.choice(6, n, p=CITY_SHARE)
    rate = rng.gamma(0.8, CITY_RATE[city] / 0.8) * 7               # orders per week
    treat = rng.random(n) < 0.5
    lift_by_week = np.array([0.055, 0.030, 0.015, 0.005])            # novelty: the lift fades
    ids = np.arange(400001, 400001 + n)
    weekly = []
    for w in range(4):
        orders = rng.poisson(rate * (1 + lift_by_week[w] * treat))
        convs = rng.poisson(np.where(treat, 0.55, 0.35) * (1 + 0.3 * (w == 0) * treat))
        weekly.append(pd.DataFrame({"customer_id": ids, "week": w + 1, "orders": orders, "conversations": convs}))
    weekly = pd.DataFrame(pd.concat(weekly, ignore_index=True))
    weekly["variant"] = np.where(np.tile(treat, 4), "treatment", "control")
    weekly["city"] = np.tile(np.array(CITIES)[city], 4)

    conv = weekly.loc[weekly.conversations > 0, ["customer_id", "week", "variant", "conversations"]]
    conv = conv.loc[conv.index.repeat(conv.conversations)].drop(columns="conversations").reset_index(drop=True)
    t = (conv.variant == "treatment").to_numpy()
    m = len(conv)
    conv["latency_s"] = np.round(np.where(t, np.exp(np.log(2.1) + 0.38 * rng.standard_normal(m)),
                                          np.exp(np.log(0.6) + 0.30 * rng.standard_normal(m))), 2)
    conv["cost_sar"] = np.round(np.where(t, 0.07 * (0.5 + rng.random(m)), 0.0), 4)
    conv["escalated"] = rng.random(m) < np.where(t, 0.11, 0.19)

    o = weekly.loc[weekly.orders > 0, ["customer_id", "week", "variant", "orders"]]
    o = o.loc[o.index.repeat(o.orders)].drop(columns="orders").reset_index(drop=True)
    t = (o.variant == "treatment").to_numpy()
    k = len(o)
    o["complaint"] = rng.random(k) < np.where(t, 0.0060, 0.0058)
    o["wrong_info_complaint"] = rng.random(k) < np.where(t, 0.0021, 0.0012)  # wrong ingredient or allergen info
    return {"weekly": weekly, "conversations": conv, "orders": o}


# ---------------------------------------------------------------------------------------------
# The capstone: data for one AI-feature change
# ---------------------------------------------------------------------------------------------

def capstone_data(change: str, seed: int | None = None, n: int | None = None) -> dict:
    """Synthetic pre-period and test data for one of the capstone changes in data/capstone_changes.json.

    Returns {"customers": per-customer pre and test totals and the arm, "daily": per-day totals by arm,
    "guardrails": per-event latency, cost and harm flags}. The assessor may change n (the traffic) or
    the pre-period in the defence: pass them here.
    """
    spec = {c["id"]: c for c in js("capstone_changes")["changes"]}[change]
    rng = np.random.default_rng(seed if seed is not None else spec["seed"])
    n = n or pick(spec["customers"], 30_000)
    city = rng.choice(6, n, p=CITY_SHARE)
    rate = rng.gamma(0.8, CITY_RATE[city] / 0.8)
    mu = np.log(CITY_VALUE[city]) + 0.35 * rng.standard_normal(n)
    treat = rng.random(n) < 0.5
    o_pre = rng.poisson(DAYS * rate)
    o_test = rng.poisson(DAYS * rate * (1 + spec["true_lift"] * treat))
    rev = lambda k: np.bincount(np.repeat(np.arange(n), k), weights=_basket_values(rng, np.repeat(mu, k)),
                                minlength=n)
    cust = pd.DataFrame({"customer_id": np.arange(800001, 800001 + n), "city": np.array(CITIES)[city],
                         "variant": np.where(treat, "treatment", "control"), "orders_pre": o_pre,
                         "revenue_pre": np.round(rev(o_pre), 2), "orders": o_test, "revenue": np.round(rev(o_test), 2)})
    days = np.arange(DAYS)
    daily = pd.DataFrame([(d, v, int(rng.poisson(len(cust) / DAYS / 2))) for d in days for v in ("control", "treatment")],
                         columns=["day", "variant", "new_customers"])
    m = pick(80_000, 20_000)
    tg = rng.random(m) < 0.5
    g = spec["guardrails"]
    guard = pd.DataFrame({
        "variant": np.where(tg, "treatment", "control"),
        "latency_ms": np.round(np.exp(np.log(np.where(tg, g["latency_median_t"], g["latency_median_c"]))
                                      + 0.4 * rng.standard_normal(m))).astype(int),
        "cost_sar": np.round(np.where(tg, g["cost_t"], g["cost_c"]) * (0.6 + 0.8 * rng.random(m)), 5),
        "harm_flag": rng.random(m) < np.where(tg, g["harm_t"], g["harm_c"]),
    })
    return {"customers": cust, "daily": daily, "guardrails": guard}
