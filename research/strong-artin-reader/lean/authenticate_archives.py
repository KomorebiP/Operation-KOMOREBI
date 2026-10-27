#!/usr/bin/env python3
"""Authenticate retained archives and inspect production-source trust markers.

This is a byte and static-source audit. It never compiles Lean and must not be
reported as a fresh theorem replay.
"""
import argparse
import hashlib
import io
import json
import re
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

EXPECTED = "d5f065bcb05ee02465082804dfb14800f82b86f43a8838eded2e3d3519abcb9a"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def mask_lean(raw):
    """Mask nested block comments, line comments and string contents."""
    out = list(raw)
    i = 0
    depth = 0
    while i < len(raw):
        if depth:
            if raw.startswith("/-", i):
                out[i:i+2] = "  "; depth += 1; i += 2
            elif raw.startswith("-/", i):
                out[i:i+2] = "  "; depth -= 1; i += 2
            else:
                if raw[i] != "\n": out[i] = " "
                i += 1
        elif raw.startswith("/-", i):
            out[i:i+2] = "  "; depth = 1; i += 2
        elif raw.startswith("--", i):
            while i < len(raw) and raw[i] != "\n": out[i] = " "; i += 1
        elif raw[i] == '"':
            out[i] = " "; i += 1
            while i < len(raw):
                if raw[i] == "\\":
                    out[i:i+2] = "  "; i += 2
                elif raw[i] == '"':
                    out[i] = " "; i += 1; break
                else:
                    if raw[i] != "\n": out[i] = " "
                    i += 1
        else:
            i += 1
    if depth: raise ValueError("Unterminated Lean comment")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archive", type=Path, required=True)
    ap.add_argument("--historical-replay", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    archive = args.archive.read_bytes()
    assert digest(archive) == EXPECTED, "Wrong v0.38 archive identity"
    records = []
    seen = set()
    production = {}
    failures = []

    def visit(blob, name):
        sha = digest(blob)
        if sha in seen: return
        seen.add(sha)
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            names = z.namelist()
            assert z.testzip() is None, (name, "CRC failure")
            manifests = [n for n in names if n.endswith("/SHA256SUMS.txt")]
            verified = 0
            mismatches = []
            for manifest in manifests:
                prefix = manifest[:-len("SHA256SUMS.txt")]
                for line in z.read(manifest).decode().splitlines():
                    match = re.fullmatch(r"([0-9a-f]{64})\s+\*?(.+)", line)
                    if not match: continue
                    h, rel = match.groups()
                    relative = Path(rel)
                    if relative.is_absolute():
                        # Early archives recorded absolute scratch locations.
                        # Anchor to this manifest's own archived directory name.
                        anchor = Path(prefix).name
                        positions = [i for i, value in enumerate(relative.parts) if value == anchor]
                        if not positions:
                            mismatches.append({"manifest": manifest, "member": rel, "error": "unresolved historical absolute path"})
                            continue
                        relative = Path(*relative.parts[positions[-1]+1:])
                    member = str(Path(prefix) / relative)
                    if member not in names:
                        mismatches.append({"manifest": manifest, "member": member, "error": "missing"})
                    elif digest(z.read(member)) != h:
                        mismatches.append({"manifest": manifest, "member": member, "error": "hash mismatch"})
                    else:
                        verified += 1
            failures.extend({"archive": name, **x} for x in mismatches)
            records.append({"archive_name": name, "sha256": sha, "bytes": len(blob),
                            "crc_passed": True, "manifest_entries_verified": verified,
                            "manifest_mismatches": mismatches})
            for n in names:
                parts = Path(n).parts
                if n.endswith(".lean") and "src" in parts and not any(x in parts for x in ["verification", "development", "development_logs", "base_v0.9"]):
                    b = z.read(n); h = digest(b)
                    code = mask_lean(b.decode())
                    markers = re.findall(r"\b(sorry|admit|axiom|opaque|sorryAx|native_decide|unsafe)\b", code)
                    if h not in production:
                        production[h] = {"sha256": h, "module": Path(n).stem, "first_archive": name,
                                         "member": n, "static_markers": markers}
                if n.endswith(".zip"):
                    visit(z.read(n), Path(n).name)

    visit(archive, args.archive.name)
    replay = json.loads(args.historical_replay.read_text())
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        prefix = "Strong_Artin_v0.38_Effective_Matrix_Hensel/"
        matches = {m: digest(z.read(prefix+"src/"+m+".lean")) == h
                   for m, h in replay["source_hashes"].items()}
        declarations = json.loads(z.read(prefix+"DECLARATIONS.json"))
        assert declarations == replay["declarations"], "Declaration inventory differs"
    assert all(matches.values()), "Historical replay authenticates different source bytes"
    markers = [x for x in production.values() if x["static_markers"]]
    report = {"generated_utc": datetime.now(timezone.utc).isoformat(),
              "status": "PASS" if not failures and not markers else "FINDINGS",
              "scope": "Archive CRC/hash authentication and static production-source screening only",
              "fresh_lean_replay": False,
              "archive_sha256": EXPECTED, "unique_archives": len(records),
              "archives": records, "manifest_findings": failures,
              "production_source_records": list(production.values()),
              "forbidden_marker_records": markers,
              "current_source_hashes_match_historical_replay": matches,
              "current_named_declaration_count": len(declarations),
              "current_named_declaration_kinds": dict(Counter(d["kind"] for d in declarations)),
              "historical_replay_started_utc": replay["started_utc"],
              "historical_replay_status": replay["status"],
              "historical_replay_sha256": digest(args.historical_replay.read_bytes()),
              "non_claims": ["No fresh Lean compilation", "No combined build of historical versions",
                             "No inference from theorem counts to conjecture completion",
                             "No general arithmetic realization or Strong Artin proof"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({k: report[k] for k in ["status", "unique_archives", "current_named_declaration_count", "current_named_declaration_kinds"]}))
    if failures: print("Manifest findings:", len(failures))
    if markers: print("Static trust-marker findings:", len(markers))


if __name__ == "__main__":
    main()
