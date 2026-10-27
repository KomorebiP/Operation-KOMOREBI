"""Check the delivered 1.6.0 source contracts, visuals and inherited Lean evidence.

This checks identity and finite examples, not a fresh Lean compilation. Run the
manifest verifier before this command, which writes its own dated report.
"""
from __future__ import annotations
import csv
import hashlib
import itertools
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from proof_path_theory import __version__, analyze_affine_realizations, load_proof_field, unique_and_dag_certificate


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def main() -> int:
    report = {"publication_edition": "1.6.0", "technical_package_version": __version__,
              "fresh_lean_compilation": False, "status": "RUNNING"}
    try:
        import fitz
        require(__version__ == "1.4.0", "Wrong technical source version")
        tex = (ROOT / "docs/Proof_Path_Theory.tex").read_text()
        labels = re.findall(r"\\label\{([^}]+)\}", tex)
        require(len(labels) == len(set(labels)), "Duplicate source labels")
        refs = re.findall(r"\\(?:ref|eqref|pageref|autoref)\{([^}]+)\}", tex)
        require(set(refs) <= set(labels), "Missing source reference")
        cites = re.findall(r"\\cite\{([^}]+)\}", tex)
        bibs = set(re.findall(r"\\bibitem\{([^}]+)\}", tex))
        require({key for c in cites for key in c.split(",")} <= bibs, "Missing bibliography key")
        expected_ids = [f"PPT-{i:03d}" for i in range(1, 34)]
        claims = list(csv.DictReader((ROOT / "data/claim_ledger.csv").open()))
        require([c["claim_id"] for c in claims] == expected_ids, "Result ledger IDs changed")
        require(re.findall(r"^(PPT-\d+)\s*&", tex, re.M) == expected_ids, "Printed ledger mismatch")
        report["result_groups"] = 33
        baseline = json.loads((ROOT / "editorial/finalization_baseline_1.5.0.json").read_text())
        approved = json.loads((ROOT / "editorial/approved_finalization_changes_1.6.0.json").read_text())
        for prefix, changed in [("src/", {"src/proof_path_theory/__init__.py", "src/proof_path_theory/versioning.py"}),
                                ("tests/", set()), ("formal/", set()), ("evidence/lean/", set())]:
            paths = {p: h for p, h in baseline["files"].items() if p.startswith(prefix)}
            for name, value in paths.items():
                expected = approved["modified_source_hashes"][name] if name in changed else value
                require(sha(ROOT / name) == expected, "Unexpected source change: " + name)
            report[prefix.rstrip("/").replace("/", "_") + "_baseline_files"] = len(paths)
        pattern = re.compile(r"\\begin\{(theorem|proposition|lemma|corollary|definition|example|problem|warning|remark|proof)\}(.*?)\\end\{\1\}", re.S)
        envs = [(m[1], hashlib.sha256(m[2].encode()).hexdigest()) for m in pattern.finditer(tex)]
        require(len(envs) == 131, "Unexpected mathematical environment count")
        altered = []
        for i, (kind, h) in enumerate(envs):
            prior = baseline["environments"][i]
            require(kind == prior["kind"], "Mathematical environment kind changed")
            if h != prior["sha256"]:
                require(approved["modified_environment_hashes"].get(str(i)) == h,
                        "Unapproved mathematical edit at index " + str(i))
                altered.append(i)
        require(set(map(str, altered)) == set(approved["modified_environment_hashes"]), "Approved edits not all present")
        report["mathematical_environments"] = {"total": 131, "unchanged": 131-len(altered), "changed_indices": altered}
        for required in [r"R_d=\pi_d\circ R_{d+1}", "complete assumption context", r"L=\varnothing", "upquote=true"]:
            require(required in tex, "Missing corrected contract: " + required)
        require("Verification is a closure property" not in tex, "Old validity overstatement remains")
        contracts = json.loads((ROOT / "data/visual_contracts_1.6.0.json").read_text())
        previous = json.loads((ROOT / "data/visual_contracts_1.5.0.json").read_text())
        require(contracts["checks"] == previous["checks"], "Underlying visual example data changed")
        numbered = [k for k in contracts["figures"] if k.startswith("fig_")]
        require(len(numbered) == 22, "Wrong figure count")
        for name in contracts["figures"]:
            for ext in ("pdf", "png"):
                require((ROOT / "docs/figures" / (name+"."+ext)).is_file(), "Missing visual " + name)
            require(name+".pdf" in tex, "Unused diagram: " + name)
        field = load_proof_field(ROOT / "examples/and_dag.json")
        require(sorted(unique_and_dag_certificate(field).node_ids) == contracts["checks"]["and_dag_core"], "Core mismatch")
        points = list(itertools.product((0, 1), repeat=3))
        require(sum(sum(p)%2 == 0 for p in points) == 4, "Parity count")
        require([p for p in points if sum(p)%2 == 0 and p[0] == 0] == [(0,0,0),(0,1,1)], "Protected fiber")
        require(sum(not(p[0] and p[1]) or p[2] for p in points) == 7, "Rule-model count")
        gains = [analyze_affine_realizations(dimension=3, compatibility=[[1,1,1]], protected=[[1,0,0]], candidate=[0,0,0], observation=q).observation_gain_bits
                 for q in ([[1,0,0]], [[0,1,0]], [[0,1,0],[0,1,0]])]
        require(gains == [0,1,1], "Observation ranks")
        negative = analyze_affine_realizations(dimension=3, compatibility=[[1,1,0]], protected=[[1,0,0],[0,1,0]], candidate=[0,1,0], observation=[[0,0,1]])
        require(not negative.feasible and tuple(negative.obstruction_witness) == (1,1,1), "Negative certificate")
        report["numbered_figures"] = 22
        report["visual_data_unchanged"] = True
        pdf = fitz.open(ROOT / "docs/Proof_Path_Theory.pdf")
        pages = [p.get_text() for p in pdf]
        require("Monograph edition 1.6.0" in pages[0], "Stale PDF cover")
        require(len(pdf) == approved["pdf_pages"], "Unexpected PDF pagination")
        report["pdf_pages"] = len(pdf)
        require(sum(len(p.get_images()) for p in pdf) == 0, "Rasterized figure in PDF")
        violations = []
        for i, page in enumerate(pdf):
            for b in page.get_text("blocks"):
                if b[0] < -1 or b[1] < -1 or b[2] > page.rect.width+1 or b[3] > page.rect.height+1:
                    violations.append(i+1)
        require(not violations, "Text outside PDF bounds")
        all_text = "\n".join(pages)
        require(set(map(int, re.findall(r"Figure\s+(\d+)\.", all_text))) == set(range(1,23)), "Incomplete figure captions")
        for command in ["python scripts/design_figures.py", "python -m pytest -o addopts='' -q", 'python -m pip install -e ".[release]" --no-build-isolation']:
            require(command in all_text, "Damaged copied command: " + command)
        require("pythonscripts/design_figures.py" not in all_text, "Missing command space")
        questions = ["What is the exact claim identifier?", "What is its current status and scope?",
                     "Which justifications depend on it?", "Which evidence records support or challenge it?",
                     "Which versions and compiled documents contain it?"]
        require(any(all(q in text for q in questions) for text in pages), "Five ledger questions split across pages")
        require(not any(len(text.split()) < 60 for text in pages[1:]), "Unexpected near-empty text page")
        report["pdf_checks"] = {"raster_images": 0, "page_bound_violations": 0, "copyable_commands": True,
                                "ledger_questions_kept_together": True, "captions": list(range(1,23))}
        report["pdf_sha256"] = sha(ROOT / "docs/Proof_Path_Theory.pdf")
        require(not any(ROOT.rglob("*.ttf")) and not any(ROOT.rglob("*.otf")), "Standalone font file in package")
        report["status"] = "PASS"
    except Exception as exc:
        report["status"] = "FAIL"
        report["failure"] = str(exc)
    output = ROOT / "data/publication_verification_1.6.0.json"
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
