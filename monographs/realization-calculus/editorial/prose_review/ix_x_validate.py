#!/usr/bin/env python3
"""Compare protected TeX regions and reconstruct the prose edits from their journal."""
from pathlib import Path
import difflib
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "editorial/prose_review"
PATTERNS = {
    "math": r"(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$(?!\$).*?(?<!\\)\$|(?<!\\)\\\(.*?(?<!\\)\\\)|(?<!\\)\\\[.*?(?<!\\)\\\]|\\begin\{(?:equation\*?|align\*?|alignat\*?|gather\*?|multline\*?|displaymath|math)\}.*?\\end\{(?:equation\*?|align\*?|alignat\*?|gather\*?|multline\*?|displaymath|math)\}",
    "literal_environments": r"\\begin\{(?:Verbatim|verbatim|lstlisting|minted|alltt)\}.*?\\end\{(?:Verbatim|verbatim|lstlisting|minted|alltt)\}",
    "figures": r"\\begin\{(?:figure\*?|tikzpicture)\}.*?\\end\{(?:figure\*?|tikzpicture)\}",
    "labels": r"\\(?:label|hypertarget|input|include|includegraphics|bibitem|cite|cref|Cref|ref|eqref|pageref)\s*(?:\[[^\]]*\])?\{[^{}]*\}",
    "code_and_paths": r"\\(?:code|lean|mcode|target|source|path|url|nolinkurl|VerbatimInput)\s*(?:\[[^\]]*\])?\{[^{}]*\}",
    "href_targets": r"\\href\{[^{}]*\}",
    "caption_text": r"\\caption(?:text)?(?:\[[^\]]*\])?\{(?:[^{}]|\{[^{}]*\})*\}",
    "environment_sequence": r"\\(?:begin|end)\{[^{}]+\}",
    "includegraphics": r"\\includegraphics(?:\[[^\]]*\])?\{[^{}]*\}",
}
CAPTION_EDITS = [
    ("At prime power radix its reduction is confined", "At a prime power radix, its reduction is confined"),
    ("proved in this paper are separated", "proved in this chapter are separated"),
]


def main():
    journal = json.loads((REPORT / "ix_x_journal.json").read_text())
    files = json.loads((REPORT / "ix_x_manifest.json").read_text())
    rows, patch, failures = [], [], []
    for name in files:
        before = (REPORT / "ix_x_before" / name).read_text()
        after = (ROOT / name).read_text()
        row = {"file": name, "raw_words_before": len(before.split()), "raw_words_after": len(after.split()),
               "changed": before != after, "before_sha256": hashlib.sha256(before.encode()).hexdigest(),
               "after_sha256": hashlib.sha256(after.encode()).hexdigest(), "comparisons": {}}
        for key, pattern in PATTERNS.items():
            old, new = re.findall(pattern, before, re.S), re.findall(pattern, after, re.S)
            comparison = {"before_regions": len(old), "after_regions": len(new), "identical": old == new}
            if old != new and key in ("figures", "caption_text"):
                normalized = old[:]
                for source, target in CAPTION_EDITS:
                    normalized = [item.replace(source, target) for item in normalized]
                comparison["identical_after_authorized_caption_prose_edits"] = normalized == new
            row["comparisons"][key] = comparison
            if not comparison["identical"] and not comparison.get("identical_after_authorized_caption_prose_edits"):
                failures.append((name, key))
        replay = before
        for entry in (entry for entry in journal if entry["file"] == name):
            assert entry["old"] in replay, (name, entry["old"])
            replay = replay.replace(entry["old"], entry["new"], 1)
        row["journal_reconstructs_final_exactly"] = replay == after
        row["brace_balance_unchanged"] = before.count("{") - before.count("}") == after.count("{") - after.count("}")
        assert row["journal_reconstructs_final_exactly"] and row["brace_balance_unchanged"], name
        rows.append(row)
        patch.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile="before/" + name, tofile=name))
    assert not failures, failures
    (REPORT / "ix_x_validation.json").write_text(json.dumps(rows, indent=2) + "\n")
    (REPORT / "ix_x_changes.patch").write_text("".join(patch))
    path = REPORT / "ix_x_report.json"
    report = json.loads(path.read_text())
    report.update(status="SEALED", edits=len(journal), changed_files=sum(row["changed"] for row in rows))
    report["validation"]["caption_changes"] = "Two root-reviewed caption prose edits: article/comma at a prime power radix, and ordinary paper-to-chapter reference. Image assets, formulas, labels, and visual code unchanged."
    report["validation"]["remaining_comparison_failures"] = []
    report["validation"]["reproduction_command"] = "python editorial/prose_review/ix_x_validate.py"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": "SEALED", "edits": len(journal), "changed_files": report["changed_files"], "protected_comparison_failures": failures}))


if __name__ == "__main__":
    main()
