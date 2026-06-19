import argparse
import csv
import json
import math
import os
import platform
import re
import statistics
import subprocess
import sys
import time
from decimal import Decimal, getcontext
from pathlib import Path


TASK_NAMES = (
    "int_loop",
    "function_calls",
    "list_dict",
    "json_regex",
    "decimal_math",
    "class_attr",
)


def bench_int_loop():
    total = 0
    for i in range(3_000_000):
        total += (i % 17) - (i % 11)
    return total


def _tiny_func(a, b):
    return (a ^ b) + (a & 7) - (b & 3)


def bench_function_calls():
    total = 0
    for i in range(1_200_000):
        total = (total + _tiny_func(i, total)) & 0xFFFFFFFF
    return total


def bench_list_dict():
    values = [(i, (i * 37) % 10_003) for i in range(220_000)]
    mapping = {key: value for key, value in values}
    selected = [mapping[i] for i in range(0, 220_000, 3)]
    return sum(selected) ^ len(mapping)


def bench_json_regex():
    payload = {
        "items": [
            {
                "id": i,
                "name": f"item-{i:05d}",
                "enabled": i % 3 == 0,
                "score": (i * 19) % 997,
            }
            for i in range(12_000)
        ]
    }
    encoded = json.dumps(payload, separators=(",", ":"))
    decoded = json.loads(encoded)
    matches = re.findall(r"item-\d{5}", encoded)
    return len(decoded["items"]) + len(matches) + len(encoded)


def bench_decimal_math():
    getcontext().prec = 38
    value = Decimal("1.0000001")
    step = Decimal("0.9999997")
    total = Decimal("0")
    for i in range(90_000):
        value = (value * step) + Decimal(i % 97) / Decimal("1000003")
        total += value
    return int(total)


class Point:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        return self.x - self.y


def bench_class_attr():
    points = [Point(i, -i) for i in range(80_000)]
    total = 0
    for round_index in range(9):
        for point in points:
            total += point.move(round_index & 7, round_index % 5)
    return total


TASKS = {
    "int_loop": bench_int_loop,
    "function_calls": bench_function_calls,
    "list_dict": bench_list_dict,
    "json_regex": bench_json_regex,
    "decimal_math": bench_decimal_math,
    "class_attr": bench_class_attr,
}


def jit_state():
    if not hasattr(sys, "_jit"):
        return {"has_jit": False, "jit_available": False, "jit_enabled": False}
    return {
        "has_jit": True,
        "jit_available": bool(sys._jit.is_available()),
        "jit_enabled": bool(sys._jit.is_enabled()),
    }


def run_worker(repeats, warmups):
    results = {
        "executable": sys.executable,
        "version": sys.version,
        "platform": platform.platform(),
        "jit": jit_state(),
        "tasks": {},
    }
    for name in TASK_NAMES:
        func = TASKS[name]
        for _ in range(warmups):
            func()
        durations = []
        checksum = None
        for _ in range(repeats):
            start = time.perf_counter()
            checksum = func()
            durations.append(time.perf_counter() - start)
        results["tasks"][name] = {
            "durations_seconds": durations,
            "median_seconds": statistics.median(durations),
            "min_seconds": min(durations),
            "checksum": str(checksum),
        }
    print(json.dumps(results, indent=2, sort_keys=True))


def scenario_env(jit_enabled, native_jit=False):
    env = os.environ.copy()
    root = Path("G:/Dx/python")
    temp = root / "artifacts" / "temp"
    temp.mkdir(parents=True, exist_ok=True)
    env["TEMP"] = str(temp)
    env["TMP"] = str(temp)
    env["PYTHONHASHSEED"] = "0"
    if jit_enabled:
        env["PYTHON_JIT"] = "1"
    else:
        env.pop("PYTHON_JIT", None)
    if native_jit:
        env["PYTHON_NATIVE_JIT"] = "1"
    else:
        env.pop("PYTHON_NATIVE_JIT", None)
    return env


def time_startup(exe, cwd, jit_enabled, native_jit, runs):
    env = scenario_env(jit_enabled, native_jit)
    durations = []
    for _ in range(runs):
        start = time.perf_counter()
        completed = subprocess.run(
            [exe, "-c", "pass"],
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        durations.append(time.perf_counter() - start)
        if completed.returncode != 0:
            raise RuntimeError(
                f"startup failed for {exe}: {completed.stderr.strip()}"
            )
    return {
        "durations_seconds": durations,
        "median_seconds": statistics.median(durations),
        "min_seconds": min(durations),
    }


def run_worker_process(exe, cwd, jit_enabled, native_jit, repeats, warmups, worker_script):
    env = scenario_env(jit_enabled, native_jit)
    completed = subprocess.run(
        [
            exe,
            str(worker_script),
            "--worker",
            "--repeats",
            str(repeats),
            "--warmups",
            str(warmups),
        ],
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"worker failed for {exe}: {completed.stderr.strip()}"
        )
    return json.loads(completed.stdout)


def pct_slower(current, baseline):
    if baseline <= 0:
        return math.nan
    return ((current / baseline) - 1.0) * 100.0


def write_summary_csv(run_dir, results):
    csv_path = run_dir / "summary.csv"
    official_default = results["scenarios"]["official-default"]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "scenario",
                "metric",
                "median_seconds",
                "min_seconds",
                "pct_slower_vs_official_default_median",
            ]
        )
        baseline_startup = official_default["startup"]["median_seconds"]
        for name, scenario in results["scenarios"].items():
            startup = scenario["startup"]
            writer.writerow(
                [
                    name,
                    "startup",
                    f"{startup['median_seconds']:.9f}",
                    f"{startup['min_seconds']:.9f}",
                    f"{pct_slower(startup['median_seconds'], baseline_startup):.3f}",
                ]
            )
        for task in TASK_NAMES:
            baseline = official_default["worker"]["tasks"][task]["median_seconds"]
            for name, scenario in results["scenarios"].items():
                item = scenario["worker"]["tasks"][task]
                writer.writerow(
                    [
                        name,
                        task,
                        f"{item['median_seconds']:.9f}",
                        f"{item['min_seconds']:.9f}",
                        f"{pct_slower(item['median_seconds'], baseline):.3f}",
                    ]
                )
    return csv_path


def run_driver(args):
    root = Path("G:/Dx/python")
    run_dir = root / "benchmarks" / "runs" / time.strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    worker_script = Path(__file__).resolve()
    scenarios = {
        "official-default": {
            "exe": args.official,
            "cwd": str(run_dir),
            "jit": False,
            "native_jit": False,
        },
        "official-jit": {
            "exe": args.official,
            "cwd": str(run_dir),
            "jit": True,
            "native_jit": False,
        },
        "local-default": {
            "exe": args.local,
            "cwd": args.local_cwd,
            "jit": False,
            "native_jit": False,
        },
        "local-jit": {
            "exe": args.local,
            "cwd": args.local_cwd,
            "jit": True,
            "native_jit": False,
        },
        "local-native-jit": {
            "exe": args.local,
            "cwd": args.local_cwd,
            "jit": True,
            "native_jit": True,
        },
    }
    results = {
        "run_dir": str(run_dir),
        "driver": sys.version,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "repeats": args.repeats,
        "warmups": args.warmups,
        "startup_runs": args.startup_runs,
        "scenarios": {},
    }
    for name, scenario in scenarios.items():
        scenario_dir = run_dir / name
        scenario_dir.mkdir(parents=True, exist_ok=True)
        startup = time_startup(
            scenario["exe"],
            scenario["cwd"],
            scenario["jit"],
            scenario["native_jit"],
            args.startup_runs,
        )
        worker = run_worker_process(
            scenario["exe"],
            scenario["cwd"],
            scenario["jit"],
            scenario["native_jit"],
            args.repeats,
            args.warmups,
            worker_script,
        )
        results["scenarios"][name] = {
            "exe": scenario["exe"],
            "cwd": scenario["cwd"],
            "jit_requested": scenario["jit"],
            "native_jit_requested": scenario["native_jit"],
            "startup": startup,
            "worker": worker,
        }
        with (scenario_dir / "worker.json").open("w", encoding="utf-8") as f:
            json.dump(worker, f, indent=2, sort_keys=True)
        with (scenario_dir / "startup.json").open("w", encoding="utf-8") as f:
            json.dump(startup, f, indent=2, sort_keys=True)
    with (run_dir / "results.json").open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, sort_keys=True)
    csv_path = write_summary_csv(run_dir, results)
    print(json.dumps({"run_dir": str(run_dir), "summary_csv": str(csv_path)}))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--official")
    parser.add_argument("--local")
    parser.add_argument("--local-cwd", default="G:/Dx/python/cpython")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--startup-runs", type=int, default=12)
    return parser.parse_args()


def main():
    args = parse_args()
    if args.worker:
        run_worker(args.repeats, args.warmups)
        return
    if not args.official or not args.local:
        raise SystemExit("--official and --local are required")
    run_driver(args)


if __name__ == "__main__":
    main()
