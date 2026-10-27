"""Read-only heartbeat for the two external Block17 scanner processes."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time

WORKSPACE = Path(__file__).resolve().parents[2]
OUTPUT = WORKSPACE / "arc-evidence/fullbank-public-evaluation"
CENSUS = OUTPUT / "census.json"
SCANNERS = ("run_scan.py", "supplement_block17_scan.py")

while True:
    processes = {name: [] for name in SCANNERS}
    assumed_cwd = []
    for entry in Path("/proc").glob("[0-9]*"):
        try:
            argv = (entry / "cmdline").read_bytes().split(b"\0")
            names = {Path(os.fsdecode(part)).name for part in argv[1:] if part}
            matching = False
            for index, part in enumerate(argv):
                if part == b"--output" and index + 1 < len(argv):
                    value = Path(os.fsdecode(argv[index + 1]))
                    if not value.is_absolute():
                        try:
                            value = (entry / "cwd").resolve(strict=True) / value
                        except OSError:
                            value = WORKSPACE / value  # Known launch cwd supplied by the owning agent.
                            assumed_cwd.append(int(entry.name))
                    matching = value.resolve() == CENSUS.resolve()
                    break
            for name in processes:
                if name in names and matching:
                    processes[name].append(int(entry.name))
        except (OSError, ProcessLookupError):
            continue
    checkpoints = list(CENSUS.with_suffix(".tasks").glob("*.json"))
    stats = [p.stat().st_size for p in checkpoints]
    events = {k: int(v) for k, v in (line.split() for line in Path("/sys/fs/cgroup/memory.events").read_text().splitlines())}
    fs = os.statvfs(WORKSPACE)
    row = {"utc": datetime.now(timezone.utc).isoformat(), "census_exists": CENSUS.is_file(),
           "completed_checkpoints": len(checkpoints), "checkpoint_bytes": sum(stats),
           "largest_checkpoint_bytes": max(stats, default=0), "scanner_processes": processes,
           "known_launch_cwd_assumed_for_pids": assumed_cwd,
           "oom_kill_count": events["oom_kill"],
           "memory_current_bytes": int(Path("/sys/fs/cgroup/memory.current").read_text()),
           "filesystem_unused_block_bytes": fs.f_bfree * fs.f_frsize,
           "filesystem_available_unprivileged_bytes": fs.f_bavail * fs.f_frsize}
    print(json.dumps(row, sort_keys=True), flush=True)
    with (OUTPUT / "monitor_observations.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, sort_keys=True) + "\n")
    if not any(processes.values()):
        break
    time.sleep(45)
