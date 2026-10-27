#!/usr/bin/env python3
"""Execute the Lean affine normalizer. Read-only; no native-code deployment."""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def reject_constant(s: str):
    raise ValueError(f"Non-finite JSON number: {s}")

def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"Duplicate object key: {key}")
        out[key] = value
    return out

def environment() -> tuple[Path, dict[str, str]]:
    kit = Path(os.environ.get("AVOC_LEAN_KIT", "/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2"))
    lean = kit / "toolchain/bin/lean"
    if not lean.is_file():
        raise FileNotFoundError("Set AVOC_LEAN_KIT to the pinned portable runtime.")
    output = ROOT / ".lake/build/lib/lean"
    if not (output / "AVOC/AffineCodec.olean").is_file():
        raise FileNotFoundError("Compile the affine modules first; see REPRODUCE.md.")
    # Refuse stale source/output pairs. Fingerprints are not external authentication.
    for rel in ["AVOC/AffineSignature.lean", "AVOC/TypedAffineProgram.lean", "AVOC/AffineFusion.lean", "AVOC/AffineCodec.lean", "tools/AffineMain.lean"]:
        src = ROOT / rel
        obj = output / Path(rel).with_suffix(".olean")
        records = [ROOT / "results/v0.28.0" / ("clean_" + src.stem + ".json"), ROOT / "results/v0.28.0" / (src.stem + ".json")]
        current = False
        for record in records:
            if not record.is_file() or not obj.is_file():
                continue
            rec = json.loads(record.read_text())
            deps = {}
            for name in re.findall(r"^import\s+(AVOC(?:\.\w+)*)\s*$", src.read_text(), re.M):
                dep = output / Path(name.replace(".", "/")).with_suffix(".olean")
                deps[name] = hashlib.sha256(dep.read_bytes()).hexdigest() if dep.is_file() else None
            if (rec.get("returncode") == 0 and not rec.get("timed_out") and rec.get("source_unchanged")
                and rec.get("imports_unchanged") and rec.get("import_outputs") == deps
                and rec.get("source_sha256") == hashlib.sha256(src.read_bytes()).hexdigest()
                and rec.get("output_sha256") == hashlib.sha256(obj.read_bytes()).hexdigest()):
                current = True
                break
        if not current:
            raise ValueError(f"Missing or stale current compilation record: {rel}")
    paths = [output] + [p / ".lake/build/lib/lean" for p in (kit / "workspace/.lake/packages").iterdir() if p.is_dir()]
    env = os.environ.copy()
    env["LEAN_PATH"] = ":".join(map(str, paths))
    env["PATH"] = str(kit / "toolchain/bin") + ":" + env.get("PATH", "")
    return lean, env

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("request", type=Path)
    ap.add_argument("--batch", action="store_true")
    ap.add_argument("--timeout", type=float, default=45.0)
    args = ap.parse_args()
    try:
        if not 0 < args.timeout <= 120:
            raise ValueError("timeout must be in (0,120]")
        path = args.request.resolve(strict=True)
        if path.stat().st_size > 4_194_304:
            raise ValueError("input byte cap")
        json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant, object_pairs_hook=unique_object)
        lean, env = environment()
        cmd = [str(lean), "--run", str(ROOT / "tools/AffineMain.lean")]
        if args.batch:
            cmd.append("--batch")
        cmd.append(str(path))
        proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=args.timeout)
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return proc.returncode
    except (OSError, ValueError, RecursionError, subprocess.TimeoutExpired) as exc:
        print(f"Affine execution failed: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
