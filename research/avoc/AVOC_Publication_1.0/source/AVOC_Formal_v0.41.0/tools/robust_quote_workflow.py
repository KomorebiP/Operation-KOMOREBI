#!/usr/bin/env python3
"""Protected one-operation robust-quote workflow with transactional commit/ack recovery.

This adapter is bounded implementation evidence.  The Lean transition and recovery
checks remain the source of the formal guarantees; SQLite/Python/host integrity are
explicit trust boundaries.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sqlite3, subprocess, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "tools/run_robust_quote.py"


def canonical(x: Any) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def load_json(path: Path) -> Any:
    path = path.resolve(strict=True)
    if path.is_symlink() or path.stat().st_size > 4_194_304:
        raise ValueError(f"invalid JSON file: {path}")
    return json.loads(path.read_text())


def lean_call(req: list, run_dir: Path, label: str, timeout: float) -> dict:
    request_dir = run_dir / "requests"; request_dir.mkdir(parents=True, exist_ok=True)
    path = request_dir / f"{label}.json"
    path.write_text(canonical(req)+"\n")
    env = os.environ.copy()
    env.setdefault("AVOC_LEAN_KIT", "/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2")
    cp = subprocess.run([sys.executable, str(WRAPPER), str(path), "--timeout", str(timeout)],
                        cwd=ROOT, env=env, text=True, capture_output=True,
                        timeout=timeout+30)
    (request_dir/f"{label}.stdout").write_text(cp.stdout)
    (request_dir/f"{label}.stderr").write_text(cp.stderr)
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip() or f"Lean call {label} failed")
    return json.loads(cp.stdout)


def init_db(db: sqlite3.Connection, config: dict, config_text: str) -> None:
    db.executescript("""
      PRAGMA journal_mode=WAL;
      PRAGMA synchronous=FULL;
      CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
      CREATE TABLE operations(
        sequence INTEGER PRIMARY KEY,
        action TEXT NOT NULL,
        intent_json TEXT NOT NULL,
        transition_request TEXT,
        transition_result TEXT,
        recovery_request TEXT,
        recovery_result TEXT,
        committed INTEGER NOT NULL DEFAULT 0,
        acknowledged INTEGER NOT NULL DEFAULT 0
      );
      CREATE TABLE counters(kind TEXT PRIMARY KEY, calls INTEGER NOT NULL);
    """)
    db.execute("INSERT INTO meta VALUES('schema','avoc-v0.38-robust-workflow-v1')")
    db.execute("INSERT INTO meta VALUES('config_sha256',?)", (digest_text(config_text),))
    db.execute("INSERT INTO meta VALUES('config_json',?)", (canonical(config),))
    db.execute("INSERT INTO meta VALUES('status','initialized')")
    db.execute("INSERT INTO counters VALUES('warm',0)")
    db.execute("INSERT INTO counters VALUES('cold',0)")
    db.commit()


def plan_request(c: dict) -> list:
    return ["robust-quote-plan-f5-v1", c["source"], c["calls"], c["warm_quote"],
            c["cold_quote"], c["state"], c["continuation_horizon"]]


def selected_artifact(c: dict, action: str) -> tuple[str, dict]:
    if action == "inspect_warm":
        kind, key = "warm", "warm_artifact"
    elif action == "generate_cold":
        kind, key = "cold", "cold_artifact"
    else:
        raise ValueError(f"workflow expects a selected setup operation, got {action}")
    # Crucially, only the selected path is resolved/opened.
    raw = c.get(key)
    if not isinstance(raw, str):
        raise ValueError(f"missing selected artifact path: {key}")
    data = load_json(Path(raw))
    for field in ("identity","artifact","generation","outcome"):
        if field not in data:
            raise ValueError(f"selected artifact missing {field}")
    return kind, data


def transition_request(c: dict, action: str, art: dict) -> list:
    return ["robust-quote-transition-f5-v1", c["source"], c["calls"],
            c["warm_quote"], c["cold_quote"], c["state"], action,
            art["outcome"], art["identity"], art["artifact"], art["generation"]]


def recovery_request(c: dict, action: str, art: dict) -> list:
    return ["robust-quote-recover-f5-v1", c["source"], c["calls"],
            c["warm_quote"], c["cold_quote"], c["state"][4], action,
            art["outcome"], art["identity"], art["artifact"], art["generation"],
            c["warm_quote"], c["cold_quote"]]


def summary(db: sqlite3.Connection) -> dict:
    status = db.execute("SELECT value FROM meta WHERE key='status'").fetchone()[0]
    counters = dict(db.execute("SELECT kind,calls FROM counters"))
    op = db.execute("SELECT sequence,action,committed,acknowledged,transition_result,recovery_result FROM operations ORDER BY sequence DESC LIMIT 1").fetchone()
    return {"schema":"avoc-v0.38-robust-workflow-summary-v1","status":status,
            "external_calls":counters,
            "operation": None if op is None else {
                "sequence":op[0],"action":op[1],"committed":bool(op[2]),
                "acknowledged":bool(op[3]),
                "transition":None if op[4] is None else json.loads(op[4]),
                "recovery":None if op[5] is None else json.loads(op[5])}}


def start(config_path: Path, run_dir: Path, timeout: float, inject_after_commit: bool) -> dict:
    if run_dir.exists():
        raise ValueError("run directory already exists")
    run_dir.mkdir(parents=True)
    config_text = config_path.resolve(strict=True).read_text()
    c = json.loads(config_text)
    db = sqlite3.connect(run_dir/"workflow.sqlite3")
    init_db(db,c,config_text)
    plan = lean_call(plan_request(c),run_dir,"plan",timeout)
    action = plan["robust_choice"]
    kind, art = selected_artifact(c,action)
    intent = {"sequence":0,"state":c["state"],"action":action,
              "warm_quote":c["warm_quote"],"cold_quote":c["cold_quote"]}
    with db:
        db.execute("INSERT INTO operations(sequence,action,intent_json) VALUES(0,?,?)",
                   (action,canonical(intent)))
        db.execute("UPDATE meta SET value='intent' WHERE key='status'")
    trans_req=transition_request(c,action,art)
    trans=lean_call(trans_req,run_dir,"selected_transition",timeout)
    rec_req=recovery_request(c,action,art)
    # Publish selected-result record and call count atomically.
    with db:
        db.execute("UPDATE operations SET transition_request=?,transition_result=?,recovery_request=?,committed=1 WHERE sequence=0",
                   (canonical(trans_req),canonical(trans),canonical(rec_req)))
        db.execute("UPDATE counters SET calls=calls+1 WHERE kind=?",(kind,))
        db.execute("UPDATE meta SET value='committed' WHERE key='status'")
    if inject_after_commit:
        raise SystemExit(97)
    rec=lean_call(rec_req,run_dir,"acknowledge",timeout)
    with db:
        db.execute("UPDATE operations SET recovery_result=?,acknowledged=1 WHERE sequence=0",
                   (canonical(rec),))
        db.execute("UPDATE meta SET value='acknowledged' WHERE key='status'")
    out=summary(db); (run_dir/"summary.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    return out


def resume(run_dir: Path, timeout: float) -> dict:
    dbpath=run_dir/"workflow.sqlite3"
    if not dbpath.is_file(): raise ValueError("missing workflow database")
    db=sqlite3.connect(dbpath)
    row=db.execute("SELECT committed,acknowledged,recovery_request FROM operations WHERE sequence=0").fetchone()
    if row is None: raise ValueError("unfinished intent has no durable selected result")
    committed,acknowledged,req=row
    if not committed: raise ValueError("unfinished intent has no durable selected result")
    if not acknowledged:
        rec=lean_call(json.loads(req),run_dir,"recovery_acknowledge",timeout)
        with db:
            db.execute("UPDATE operations SET recovery_result=?,acknowledged=1 WHERE sequence=0",
                       (canonical(rec),))
            db.execute("UPDATE meta SET value='acknowledged' WHERE key='status'")
    out=summary(db); (run_dir/"summary.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    return out


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    sub=ap.add_subparsers(dest="cmd",required=True)
    a=sub.add_parser("start"); a.add_argument("config",type=Path); a.add_argument("--run-dir",type=Path,required=True); a.add_argument("--timeout",type=float,default=300); a.add_argument("--inject-after-commit",action="store_true")
    a=sub.add_parser("resume"); a.add_argument("--run-dir",type=Path,required=True); a.add_argument("--timeout",type=float,default=300)
    a=sub.add_parser("inspect"); a.add_argument("--run-dir",type=Path,required=True)
    ns=ap.parse_args()
    try:
        if ns.cmd=="start": out=start(ns.config,ns.run_dir,ns.timeout,ns.inject_after_commit)
        else:
            db=sqlite3.connect(ns.run_dir/"workflow.sqlite3")
            out=summary(db) if ns.cmd=="inspect" else resume(ns.run_dir,ns.timeout)
        print(json.dumps(out,sort_keys=True)); return 0
    except Exception as exc:
        print(f"robust quote workflow failed: {exc}",file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
