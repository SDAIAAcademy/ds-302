# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scipy>=1.13", "statsmodels>=0.14", "duckdb>=1.1", "matplotlib>=3.9"]
# ///
# %% [markdown]
# # Setup check
#
# Run this once before Day 1. It imports every library the labs use, generates the Sufrah event stream and
# runs one SQL query on it. No lab calls a model or downloads one; nothing needs a key.

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

# %%
import importlib
import platform
import time

missing = []
for name in ("numpy", "pandas", "scipy", "statsmodels", "duckdb", "matplotlib"):
    try:
        mod = importlib.import_module(name)
        print(f"{name:12s} {getattr(mod, '__version__', '?')}")
    except ImportError:
        missing.append(name)
print("Python", platform.python_version(), "| missing:", missing or "nothing")

# %%
import sufrah as U

t = time.time()
S = U.stream()
print(f"mode {U.MODE}: {len(S['orders']):,} orders generated in {time.time() - t:.1f} s")
print(U.sql("select variant, count(*) as customers from assignments group by variant order by variant"))
U.check(not missing and len(S["orders"]) > 100_000, "ready for Day 1")
