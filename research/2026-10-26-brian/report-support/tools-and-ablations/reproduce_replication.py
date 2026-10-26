"""Explicit fresh-run command; original observations are never overwritten."""
import importlib.util
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'runs/replicated-selection/run_replication.py'
spec=importlib.util.spec_from_file_location('bounded_replication',source)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
fresh=ROOT/'runs/replicated-selection'/('reproduction-'+str(time.time_ns()))
fresh.mkdir(exist_ok=False)
module.RUN=fresh
module.main()
