"""Check monograph source consistency and identity of inherited formal evidence.

This is a source/publication check. It does not invoke Lean or replace the
separate pytest, exhaustive finite checks, or LaTeX compilation commands.
"""
from __future__ import annotations
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from proof_path_theory import load_proof_field, ProofFieldViews, __version__


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    report = {"version": "1.3.0", "status": "RUNNING",
              "started_utc": datetime.now(timezone.utc).isoformat(),
              "fresh_lean_compilation": False}
    try:
        require(__version__ == "1.3.0", "Package version does not match monograph")
        tex = (ROOT / "docs/Proof_Path_Theory.tex").read_text()
        labels = re.findall(r"\\label\{([^}]+)\}", tex)
        require(len(labels) == len(set(labels)), "Duplicate TeX labels")
        refs = re.findall(r"\\(?:ref|eqref|autoref|pageref)\{([^}]+)\}", tex)
        require(set(refs) <= set(labels), "Unresolved source references: " + str(set(refs)-set(labels)))
        citekeys = {key.strip() for group in re.findall(r"\\cite\{([^}]+)\}", tex) for key in group.split(',')}
        bibkeys = set(re.findall(r"\\bibitem(?:\[[^]]*\])?\{([^}]+)\}", tex))
        require(citekeys <= bibkeys, "Missing bibliography keys")
        require(tex.count("\\monographpart{") == 5, "Expected five parts")
        require("\\begin{abstract}" not in tex, "Article abstract remains")
        graphics = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", tex)
        require(len(graphics) == 14 and len(set(graphics)) == 14, "Expected fourteen distinct figures")
        for name in graphics:
            require((ROOT / "docs/figures" / name).is_file(), "Missing figure: " + name)
        report["manuscript"] = {"parts": 5, "labels": len(labels), "references": len(refs),
                                 "bibliography_items": len(bibkeys), "figures": len(graphics),
                                 "tex_sha256": digest(ROOT / "docs/Proof_Path_Theory.tex")}
        rows = list(csv.DictReader((ROOT / "data/claim_ledger.csv").open()))
        ids = [r["claim_id"] for r in rows]
        expected = [f"PPT-{n:03d}" for n in range(1,34)]
        require(ids == expected, "The 33 stable result identifiers are not preserved in order")
        md = (ROOT / "docs/THEOREM_LEDGER.md").read_text()
        require(re.findall(r"^\| (PPT-\d+) \|", md, re.M) == expected,
                "Human and machine-readable ledger IDs disagree")
        require(re.findall(r"^(PPT-\d+)\s*&", tex, re.M) == expected,
                "Printed ledger IDs disagree with CSV")
        report["stable_result_groups"] = len(ids)
        baseline = json.loads((ROOT / "editorial/formal_baseline_v1.2.0.json").read_text())
        for key in ("formal_source_hashes", "inherited_lean_evidence_hashes"):
            records = baseline[key]
            for rel, expected_hash in records.items():
                require((ROOT/rel).is_file() and digest(ROOT/rel) == expected_hash,
                        "Inherited source/evidence identity changed: " + rel)
            report[key.replace("_hashes", "_files_matched")] = len(records)
        example = load_proof_field(ROOT / "examples/minimal_monograph.json")
        require(example.targets <= ProofFieldViews(example).least_model(), "Example closure failed")
        require(len(example.nodes) == 2, "Expected two nodes in complete appendix example")
        report["complete_json_example"] = "PASS"
        require(not any(ROOT.rglob("*.ttf")) and not any(ROOT.rglob("*.otf")),
                "Standalone font files must not be distributed")
        report["status"] = "PASS"
    except Exception as exc:
        report["status"] = "FAIL"
        report["failure"] = str(exc)
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    target = ROOT / "data/editorial_source_checks.json"
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
