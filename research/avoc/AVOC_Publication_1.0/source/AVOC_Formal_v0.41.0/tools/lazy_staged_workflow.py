#!/usr/bin/env python3
"""Recoverable selected-operation workflow for the lazy staged affine controller.

The planner sees only quotes.  Only its selected setup artifact is opened.  A
checked transition is committed before acknowledgement; resume rechecks the
retained certificate and acknowledges without rerunning candidate generation.
"""
from __future__ import annotations
import argparse, contextlib, fcntl, hashlib, json, os, sqlite3, sys, tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from run_lazy_staged import run as lean_run  # type: ignore

SCHEMA = 1

def canonical(x: Any) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"))

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def load_json(path: Path) -> Any:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 4_194_304:
        raise ValueError(f"invalid JSON input: {path}")
    return json.loads(path.read_text())

def resolve_artifact(config_path: Path, value: str | None) -> Path | None:
    if value is None:
        return None
    p = Path(value)
    if not p.is_absolute():
        p = config_path.parent / p
    return p.resolve()

def db_connect(run_dir: Path) -> sqlite3.Connection:
    db = sqlite3.connect(run_dir / "workflow.sqlite3", timeout=30)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA foreign_keys=ON")
    return db

@contextlib.contextmanager
def locked(run_dir: Path):
    lock_path = run_dir / "COORDINATOR_LOCK"
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        try: fcntl.flock(fd, fcntl.LOCK_UN)
        finally: os.close(fd)

def init_db(db: sqlite3.Connection, config: dict[str, Any], config_path: Path) -> None:
    db.executescript("""
    CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
    CREATE TABLE checkpoint(
      id INTEGER PRIMARY KEY CHECK(id=1), state_json TEXT NOT NULL,
      warm_json TEXT, cold_json TEXT, next_seq INTEGER NOT NULL,
      remaining_horizon INTEGER NOT NULL, status TEXT NOT NULL,
      planner_calls INTEGER NOT NULL, warm_calls INTEGER NOT NULL,
      cold_calls INTEGER NOT NULL, transition_calls INTEGER NOT NULL,
      recovery_rechecks INTEGER NOT NULL);
    CREATE TABLE operations(
      seq INTEGER PRIMARY KEY, phase TEXT NOT NULL, action TEXT NOT NULL,
      before_state TEXT NOT NULL, outcome TEXT,
      after_state TEXT, request_json TEXT, response_json TEXT,
      new_warm_json TEXT, new_cold_json TEXT,
      remaining_after INTEGER, committed_at TEXT DEFAULT CURRENT_TIMESTAMP,
      acknowledged_at TEXT);
    """)
    frozen = dict(config)
    frozen["_config_path"] = str(config_path.resolve())
    frozen["_coordinator_sha256"] = sha256_bytes(Path(__file__).read_bytes())
    for k, v in {
        "schema": str(SCHEMA),
        "config": canonical(frozen),
        "config_sha256": sha256_bytes(canonical(frozen).encode()),
    }.items():
        db.execute("INSERT INTO meta(key,value) VALUES(?,?)", (k, v))
    budget = int(config["budget"])
    horizon = int(config["horizon"])
    state = ["untried", "untried", budget, 0, budget, False]
    db.execute("""INSERT INTO checkpoint VALUES
      (1,?,?,?,?,?,?,0,0,0,0,0)""",
      (canonical(state), None, None, 0, horizon, "running"))
    db.commit()

def frozen_config(db: sqlite3.Connection) -> dict[str, Any]:
    row = db.execute("SELECT value FROM meta WHERE key='config'").fetchone()
    if row is None: raise ValueError("missing frozen config")
    c = json.loads(row[0])
    if c.get("_coordinator_sha256") != sha256_bytes(Path(__file__).read_bytes()):
        raise ValueError("coordinator source changed")
    return c

def checkpoint(db: sqlite3.Connection) -> sqlite3.Row:
    row = db.execute("SELECT * FROM checkpoint WHERE id=1").fetchone()
    if row is None: raise ValueError("missing checkpoint")
    return row

def request_path(run_dir: Path, name: str, payload: Any) -> Path:
    d = run_dir / "requests"; d.mkdir(exist_ok=True)
    p = d / name
    p.write_text(json.dumps(payload, indent=2) + "\n")
    return p

def quote_config(c: dict[str, Any]):
    return c["source"], int(c["calls"]), c["warm_quote"], c["cold_quote"]

def plan_request(c: dict[str, Any], state: list[Any], h: int):
    src, calls, wq, cq = quote_config(c)
    return ["lazy-staged-plan-f5-v1", src, calls, wq, cq, state, h]

def transition_request(c: dict[str, Any], state: list[Any], action: str,
                       outcome: str, warm: Any, cold: Any, result: Any):
    src, calls, wq, cq = quote_config(c)
    return ["lazy-staged-transition-f5-v1", src, calls, wq, cq, state,
            action, outcome, warm, cold, result, int(c.get("cold_generation", 0))]

def call_lean(run_dir: Path, seq: int, kind: str, payload: Any,
              timeout: float) -> dict[str, Any]:
    p = request_path(run_dir, f"{seq:04d}_{kind}.json", payload)
    return lean_run(p, timeout)

def artifact_path(c: dict[str, Any], which: str) -> Path | None:
    value = c.get(f"{which}_artifact")
    return resolve_artifact(Path(c["_config_path"]), value)

def selected_result(c: dict[str, Any], action: str) -> tuple[str, Any]:
    if action == "inspect_warm":
        mode = c.get("warm_mode", "success")
        if mode == "reject": return "rejected", None
        if mode == "fault": raise RuntimeError("injected warm operational fault")
        p = artifact_path(c, "warm")
    elif action == "generate_cold":
        mode = c.get("cold_mode", "success")
        if mode == "reject": return "rejected", None
        if mode == "fault": raise RuntimeError("injected cold operational fault")
        p = artifact_path(c, "cold")
    else:
        return "local", None
    if p is None or not p.is_file() or p.is_symlink():
        raise RuntimeError(f"selected artifact unavailable: {p}")
    return "success", load_json(p)

def insert_intent(db: sqlite3.Connection, seq: int, action: str, before: Any) -> None:
    db.execute("INSERT INTO operations(seq,phase,action,before_state) VALUES(?,?,?,?)",
               (seq, "intent", action, canonical(before)))
    db.commit()

def commit_result(db: sqlite3.Connection, seq: int, outcome: str,
                  after: Any, req: Any, response: Any, warm: Any, cold: Any,
                  remaining_after: int) -> None:
    with db:
        cur = db.execute("""UPDATE operations SET phase='committed', outcome=?, after_state=?,
          request_json=?, response_json=?, new_warm_json=?, new_cold_json=?,
          remaining_after=? WHERE seq=? AND phase='intent'""",
          (outcome, canonical(after), canonical(req), canonical(response),
           None if warm is None else canonical(warm),
           None if cold is None else canonical(cold), remaining_after, seq))
        if cur.rowcount != 1: raise ValueError("intent commit failed")

def acknowledge(db: sqlite3.Connection, seq: int, rechecked: bool = False) -> None:
    op = db.execute("SELECT * FROM operations WHERE seq=?", (seq,)).fetchone()
    if op is None or op["phase"] not in ("committed", "acknowledged"):
        raise ValueError("operation is not committed")
    if op["phase"] == "acknowledged": return
    cp = checkpoint(db)
    if int(cp["next_seq"]) != seq:
        raise ValueError("checkpoint sequence mismatch")
    if cp["state_json"] != op["before_state"]:
        raise ValueError("checkpoint pre-state mismatch")
    with db:
        db.execute("""UPDATE checkpoint SET state_json=?,warm_json=?,cold_json=?,
          next_seq=?,remaining_horizon=?,status=?,recovery_rechecks=recovery_rechecks+?
          WHERE id=1""",
          (op["after_state"], op["new_warm_json"], op["new_cold_json"], seq+1,
           op["remaining_after"],
           "complete" if json.loads(op["after_state"])[5] else
             ("horizon_exhausted" if int(op["remaining_after"]) == 0 else "running"),
           1 if rechecked else 0))
        db.execute("UPDATE operations SET phase='acknowledged',acknowledged_at=CURRENT_TIMESTAMP WHERE seq=?", (seq,))

def recover_committed(db: sqlite3.Connection, run_dir: Path, c: dict[str, Any], timeout: float) -> str:
    cp = checkpoint(db)
    seq = int(cp["next_seq"])
    op = db.execute("SELECT * FROM operations WHERE seq=?", (seq,)).fetchone()
    if op is None: return "none"
    if op["phase"] == "intent": return "unfinished"
    if op["phase"] == "acknowledged": return "none"
    req = json.loads(op["request_json"])
    response = call_lean(run_dir, seq, "recovery_recheck", req, timeout)
    if canonical(response) != op["response_json"]:
        raise ValueError("rechecked transition differs from committed result")
    if canonical(response["after"]) != op["after_state"]:
        raise ValueError("rechecked post-state mismatch")
    acknowledge(db, seq, True)
    return "recovered"

def one_step(db: sqlite3.Connection, run_dir: Path, c: dict[str, Any], timeout: float,
             crash_after_commit: int | None) -> str:
    cp = checkpoint(db)
    if cp["status"] != "running": return cp["status"]
    h = int(cp["remaining_horizon"])
    if h <= 0:
        db.execute("UPDATE checkpoint SET status='horizon_exhausted' WHERE id=1"); db.commit()
        return "horizon_exhausted"
    state = json.loads(cp["state_json"])
    seq = int(cp["next_seq"])
    plan = call_lean(run_dir, seq, "plan", plan_request(c, state, h), timeout)
    db.execute("UPDATE checkpoint SET planner_calls=planner_calls+1 WHERE id=1"); db.commit()
    action = plan["choice"]
    insert_intent(db, seq, action, state)
    try:
        outcome, result = selected_result(c, action)
    except Exception:
        # The unresolved intent is retained.  It is not a negative model report.
        db.execute("UPDATE checkpoint SET status='aborted_uncommitted' WHERE id=1"); db.commit()
        raise
    warm = json.loads(cp["warm_json"]) if cp["warm_json"] else None
    cold = json.loads(cp["cold_json"]) if cp["cold_json"] else None
    req = transition_request(c, state, action, outcome, warm, cold, result)
    try:
        response = call_lean(run_dir, seq, "transition", req, timeout)
    except Exception:
        db.execute("UPDATE checkpoint SET status='aborted_uncommitted' WHERE id=1"); db.commit()
        raise
    if action == "inspect_warm":
        db.execute("UPDATE checkpoint SET warm_calls=warm_calls+1 WHERE id=1")
        new_warm = result if outcome == "success" else None
        new_cold = cold
    elif action == "generate_cold":
        db.execute("UPDATE checkpoint SET cold_calls=cold_calls+1 WHERE id=1")
        new_cold = result if outcome == "success" else None
        new_warm = warm
    else:
        new_warm, new_cold = warm, cold
    db.execute("UPDATE checkpoint SET transition_calls=transition_calls+1 WHERE id=1"); db.commit()
    after = response["after"]
    commit_result(db, seq, outcome, after, req, response, new_warm, new_cold, h-1)
    if crash_after_commit is not None and seq == crash_after_commit:
        os._exit(97)
    acknowledge(db, seq, False)
    return "acknowledged"

def run_loop(db: sqlite3.Connection, run_dir: Path, c: dict[str, Any], timeout: float,
             crash_after_commit: int | None = None, recover_only: bool = False) -> dict[str, Any]:
    recovery = recover_committed(db, run_dir, c, timeout)
    if recovery == "unfinished":
        return summary(db, "aborted_uncommitted")
    if recover_only:
        return summary(db, recovery)
    for _ in range(32):
        cp = checkpoint(db)
        if cp["status"] != "running": break
        one_step(db, run_dir, c, timeout, crash_after_commit)
    return summary(db, "finished")

def summary(db: sqlite3.Connection, event: str) -> dict[str, Any]:
    cp = checkpoint(db)
    ops = [dict(r) for r in db.execute("SELECT seq,phase,action,outcome,before_state,after_state FROM operations ORDER BY seq")]
    return {
      "event": event, "status": cp["status"], "state": json.loads(cp["state_json"]),
      "next_seq": cp["next_seq"], "remaining_horizon": cp["remaining_horizon"],
      "warm_present": cp["warm_json"] is not None, "cold_present": cp["cold_json"] is not None,
      "planner_calls": cp["planner_calls"], "warm_calls": cp["warm_calls"],
      "cold_calls": cp["cold_calls"], "transition_calls": cp["transition_calls"],
      "recovery_rechecks": cp["recovery_rechecks"], "operations": ops,
    }

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start"); s.add_argument("config", type=Path); s.add_argument("--run-dir", type=Path, required=True)
    r = sub.add_parser("resume"); r.add_argument("--run-dir", type=Path, required=True); r.add_argument("--recover-only", action="store_true")
    i = sub.add_parser("inspect"); i.add_argument("--run-dir", type=Path, required=True)
    for p in (s, r):
        p.add_argument("--timeout", type=float, default=180.0)
        p.add_argument("--crash-after-commit", type=int, default=None)
    ns = ap.parse_args()
    try:
        run_dir = ns.run_dir.resolve()
        if ns.cmd == "start":
            if run_dir.exists(): raise ValueError("run directory must be new")
            run_dir.mkdir(parents=True, mode=0o700)
        elif not run_dir.is_dir(): raise ValueError("run directory does not exist")
        with locked(run_dir):
            db = db_connect(run_dir)
            try:
                if ns.cmd == "start":
                    config_path = ns.config.resolve(strict=True)
                    config = load_json(config_path)
                    init_db(db, config, config_path)
                    c = frozen_config(db)
                    result = run_loop(db, run_dir, c, ns.timeout, ns.crash_after_commit)
                elif ns.cmd == "resume":
                    c = frozen_config(db)
                    result = run_loop(db, run_dir, c, ns.timeout, ns.crash_after_commit, ns.recover_only)
                else:
                    result = summary(db, "inspect")
                print(json.dumps(result, indent=2, sort_keys=True))
                return 0 if result["status"] in ("complete","horizon_exhausted","running") else 2
            finally: db.close()
    except Exception as exc:
        print(f"lazy staged workflow failed: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
