#!/usr/bin/env python3
"""Audit archived citation syntax and speedup arithmetic; never time a device."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_FLOOR
import hashlib
import json
from pathlib import Path
import re


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def braced(text: str, start: int) -> tuple[str, int]:
    assert text[start] == "{"
    depth = 1
    cursor = start + 1
    while cursor < len(text):
        c = text[cursor]
        if c == "{" and (cursor == 0 or text[cursor - 1] != "\\"):
            depth += 1
        elif c == "}" and (cursor == 0 or text[cursor - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return text[start + 1:cursor], cursor + 1
        cursor += 1
    raise ValueError("unclosed BibTeX brace")


def parse_bib(text: str) -> list[dict]:
    records = []
    cursor = 0
    while match := re.search(r"@(\w+)\s*\{", text[cursor:]):
        start = cursor + match.end() - 1
        body, end = braced(text, start)
        key, remainder = body.split(",", 1)
        fields = {}
        position = 0
        while field := re.search(r"(\w+)\s*=\s*", remainder[position:]):
            beginning = position + field.end()
            if remainder[beginning] != "{":
                raise ValueError("this audit expects braced field values")
            value, position = braced(remainder, beginning)
            name = field.group(1).lower()
            if name in fields:
                raise ValueError("duplicate field " + name)
            fields[name] = value
        records.append({"type": match.group(1), "key": key.strip(), "fields": fields})
        cursor = end
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    source = arguments.source
    bibpath = source / "PSC_Paper_VIII_Strengthened_Annals_Edition.bib"
    texpath = source / "PSC_Paper_VIII_Strengthened_Annals_Edition.tex"
    datapath = source / "verification/benchmark_results_sanitized.json"
    records = parse_bib(bibpath.read_text())
    keys = [r["key"] for r in records]
    citations = set()
    for group in re.findall(r"\\cite(?:\w*)?(?:\[[^]]*\])*\{([^}]+)\}", texpath.read_text()):
        citations.update(k.strip() for k in group.split(","))
    assert len(keys) == len(set(keys)) == 26
    assert citations == set(keys)
    for record in records:
        assert all(k in record["fields"] for k in ("title", "year", "author"))
        if doi := record["fields"].get("doi"):
            assert re.fullmatch(r"10\.\d{4,9}/\S+", doi)
    data = json.loads(datapath.read_text())
    rows = data["results"]
    assert len(rows) == 154
    assert len(set(r["suite"] for r in rows)) == 16
    assert all(r["status"] == "measured" for r in rows)
    groups = defaultdict(list)
    for number, row in enumerate(rows):
        groups[row["case_id"], row["output_contract"]].append((number, row))
    ratio_records = []
    role_aliases = {
        "cpu_dense": {"cpu_full_svd"},
        "gpu_dense": set(),
        "cpu_packet": {"cpu_randomized_svd", "cpu_float32_iterative_refinement"},
        "gpu_packet": {"gpu_float32_iterative_refinement"},
    }
    for number, row in enumerate(rows):
        candidates = groups[row["case_id"], row["output_contract"]]
        for baseline in ("cpu_dense", "gpu_dense", "cpu_packet", "gpu_packet"):
            field = "speedup_vs_" + baseline
            if row.get(field) is None:
                continue
            matching = [(i, r) for i, r in candidates
                        if (str(r["method"]).startswith(baseline) or r["method"] in role_aliases[baseline])
                        and abs(float(r["median_ms"]) / float(row["median_ms"])
                                - float(row[field])) <= 1e-10 * max(1., abs(float(row[field])))]
            # Some precision sweeps contain several dense GPU methods; the
            # successful numerical baseline is reported, without inventing
            # a unique reference implementation or source-value fingerprint.
            assert matching, (number, baseline, row[field])
            ratio_records.append({
                "row_index_zero_based": number,
                "suite": row["suite"],
                "method": row["method"],
                "field": field,
                "recorded_ratio": row[field],
                "candidate_baseline_indices": [i for i, _ in matching],
                "arithmetic_consistent": True,
                "same_raw_timing_scope": any(r["timing_scope"] == row["timing_scope"] for _, r in matching),
                "baseline_scopes": sorted(set(r["timing_scope"] for _, r in matching)),
                "row_scope": row["timing_scope"],
                "complete_fair_match_authenticated": False,
            })
    thresholds = []
    for row in rows:
        if row["structure_discovery_ms"] is None:
            continue
        baseline = next(r for _, r in groups[row["case_id"], row["output_contract"]]
                        if r["method"] == "cpu_dense_numpy")
        discovery = Decimal(str(row["structure_discovery_ms"]))
        gap = Decimal(str(baseline["median_ms"])) - Decimal(str(row["median_ms"]))
        threshold = int((discovery / gap).to_integral_value(rounding=ROUND_FLOOR)) + 1
        assert threshold == row["reuse_count"]
        assert discovery + Decimal(threshold) * Decimal(str(row["median_ms"])) < Decimal(threshold) * Decimal(str(baseline["median_ms"]))
        assert discovery + Decimal(threshold - 1) * Decimal(str(row["median_ms"])) >= Decimal(threshold - 1) * Decimal(str(baseline["median_ms"]))
        thresholds.append({"case_id": row["case_id"], "threshold": threshold,
                           "interpretation": "exact for the archived decimal medians, not a probabilistic timing guarantee"})
    canonical_rows = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    report = {
        "audit_date_utc": "2026-10-06",
        "scope": "bibliography syntax and archived benchmark arithmetic; no device timing or complete fair-match authentication",
        "source_sha256": {str(p.relative_to(source)): digest(p) for p in (bibpath, texpath, datapath)},
        "bibliography": {"records": len(records), "all_records_cited": True,
                         "missing_citations": [], "uncited_records": [], "entries": records},
        "corpus": {"rows": len(rows), "suites": dict(sorted(Counter(r["suite"] for r in rows).items())),
                   "devices": dict(Counter(r["device"] for r in rows)),
                   "scopes": dict(Counter(r["timing_scope"] for r in rows)),
                   "canonical_rows_sha256": hashlib.sha256(canonical_rows.encode()).hexdigest(),
                   "nonnull_counts": {field: sum(r.get(field) is not None for r in rows) for field in
                                      ("compile_ms", "structure_discovery_ms", "reuse_count", "peak_memory_bytes", "relative_error", "residual_error")},
                   "absent_fields": ["source_values", "source_values_hash", "correctness_reference", "reference_computation", "timer_implementation", "raw_repeat_samples"],
                   "ratios_replayed": len(ratio_records),
                   "arithmetic_failures": 0,
                   "ratios_with_same_raw_scope": sum(r["same_raw_timing_scope"] for r in ratio_records),
                   "ratios_with_different_raw_scope": sum(not r["same_raw_timing_scope"] for r in ratio_records),
                   "thresholds": thresholds,
                   "ratio_records": ratio_records},
        "limits": ["status=measured is an archived label, not fresh measurement evidence",
                   "seeds and case IDs do not authenticate source arrays or reference executions",
                   "stored timing ratios may compare different scopes or precisions",
                   "medians and quantiles lack raw samples for independent uncertainty estimation",
                   "speedup replay establishes arithmetic only, never complete execution matching"],
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"bibliography_records": len(records), "rows": len(rows),
                      "ratios_replayed": len(ratio_records), "same_raw_scope": report["corpus"]["ratios_with_same_raw_scope"],
                      "different_raw_scope": report["corpus"]["ratios_with_different_raw_scope"],
                      "thresholds": thresholds, "output": str(arguments.output)}, indent=2))


if __name__ == "__main__":
    main()
