#!/usr/bin/env python3
"""Build the active Paper III statement register.

Use --aux PATH after the final PDF compilation. Only the four active chapters
supply statements and proofs; raw sources and RC1 metadata supply comparisons.
This collector verifies existing Lean receipts. It does not execute Lean.
"""
import argparse
import collections
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript"
MASTER = MANUSCRIPT / "Paper_III_Traditional_Final.tex"
BASE = ROOT / "checkpoint_v0.3.0"
HISTORICAL = BASE / "baseline/editable/traditional"
OUT = ROOT / "metadata"
RESULT_KINDS = {"theorem", "lemma", "proposition", "corollary"}
KINDS = RESULT_KINDS | {
    "standardfact", "definition", "example", "construction",
    "remark", "boundary", "roadmap",
}
CHAPTERS = (
    "01_finite_coordinates.tex", "02_connections_obstructions.tex",
    "03_nonlinear_coordinates.tex", "04_correction_transport.tex",
)
ENV_TOKEN = re.compile(r"\\(begin|end)\{(" + "|".join(sorted(KINDS | {"proof"})) + r")\}")
SECTION = re.compile(r"\\section(\*)?\s*\{")
LABEL = re.compile(r"\\label\s*\{([^{}]+)\}")
STATUS = re.compile(r"\\statuslean(three|prior)\s*\{")
PACKET_PREFIX = "Komorebi.PaperIII.PacketCoordinates."
SECTION17 = {
    "def:packet_jet": (
        "MATCHED_DEFINITION_AND_DERIVATIVE_SPECIALIZATION",
        [PACKET_PREFIX + name for name in (
            "packetJet", "continuousPacketJet", "continuousPacketJet_toMultilinearMap",
            "iteratedPacketJet", "iteratedPacketJet_apply_coe")],
        "Literal projector ranges with inherited norms; continuousPacketJet specializes "
        "to the actual mathlib iteratedFDeriv. Defining the chosen derivative does not "
        "assert differentiability of an arbitrary function."),
    "thm:jet_reconstruction": (
        "MATCHED_RECONSTRUCTION_IDENTITY",
        [PACKET_PREFIX + name for name in (
            "multilinear_packet_reconstruction", "iteratedFDeriv_packet_reconstruction")],
        "Reconstruction of the actual iterated derivative from range-valued packet jets. "
        "The formal identity allows every natural order; the manuscript applies it "
        "at differentiable positive orders."),
    "prop:jet_norm_bound": (
        "PARTIAL_CLAUSE_COVERAGE",
        [PACKET_PREFIX + "continuousPacketJet_norm_le",
         PACKET_PREFIX + "iteratedPacketJet_norm_le",
         "Komorebi.PaperIII.BoundedJet.projectedJet_norm_le"],
        "Formal targets prove the sharper actual-range bound and the ambient extension "
        "bound. The subsequent restricted product-bound corollary and Hilbert norm-one "
        "specialization retain their ordinary proofs; they are not separate matched "
        "Lean declarations. The ordinary proof also explains redundant zero packets."),
    "cor:packet_taylor": (
        "NO_MATCHED_PROJECT_LEAN_FORMALIZATION", [],
        "Ordinary Banach-space Taylor proof, integral remainder, factorial normalization, "
        "and remainder estimate. Finite exact checks support examples and do not "
        "formalize this theorem."),
    "thm:packet_faa": (
        "MATCHED_COMPOSITION_IDENTITY_WITH_NOTATION_TRANSLATION",
        [PACKET_PREFIX + "iteratedPacketJet_comp"],
        "Actual range jets under ContDiffAt assumptions, which the manuscript C^n "
        "assumptions imply. Lean uses OrderedFinpartition with blocks ordered by greatest "
        "element; the prose uses set partitions and least-element ordering. Symmetry "
        "identifies these conventions in ordinary mathematics. This translation does "
        "not supply a Taylor theorem."),
    "prop:faa_term_count": (
        "NO_MATCHED_PROJECT_LEAN_FORMALIZATION", [],
        "Ordinary Stirling/Touchard counting argument for decorated partitions. Exact "
        "finite enumeration supports examples; there is no matched project Lean "
        "counting theorem."),
    "cor:structural_pruning": (
        "MATCHED_VANISHING_AND_SUPPORT_IMPLICATIONS",
        [PACKET_PREFIX + "iteratedPacketJet_comp_eq_zero_of",
         PACKET_PREFIX + "iteratedPacketJet_comp_support"],
        "Formal targets prove vanishing when every decorated summand has a zero "
        "constituent, and that a nonzero composite jet has a decorated witness with "
        "nonzero constituents. This is support containment, with no converse; the "
        "same partition-order translation as in the composition theorem applies."),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def locator(path):
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def file_record(path):
    return {"path": locator(path), "sha256": sha_file(path)}


def mask_comments(text):
    """Blank TeX comments while preserving offsets and newlines."""
    chars = list(text)
    for match in re.finditer(r"%[^\n]*", text):
        before = match.start() - 1
        slashes = 0
        while before >= 0 and text[before] == "\\":
            slashes += 1
            before -= 1
        if slashes % 2 == 0:
            chars[match.start():match.end()] = " " * (match.end() - match.start())
    return "".join(chars)


def group(text, start, opening="{", closing="}"):
    """Read one balanced TeX group with nested and escaped delimiters."""
    while start < len(text) and text[start].isspace():
        start += 1
    require(start < len(text) and text[start] == opening,
            f"Expected {opening!r} at offset {start}")
    depth, cursor = 1, start + 1
    while cursor < len(text):
        char = text[cursor]
        if char == "\\":
            cursor += 2
            continue
        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return text[start + 1:cursor], cursor + 1
        cursor += 1
    raise ValueError(f"Unclosed {opening!r} group at offset {start}")


def parse_environments(path):
    text = path.read_text(encoding="utf-8")
    masked, stack, environments = mask_comments(text), [], []
    for token in ENV_TOKEN.finditer(masked):
        direction, kind = token.groups()
        if direction == "begin":
            require(not stack, f"Nested registered/proof environment in {path}")
            stack.append((kind, token.start(), token.end()))
            continue
        require(bool(stack) and stack[-1][0] == kind,
                f"Unbalanced {kind} environment in {path}")
        _, start, cursor = stack.pop()
        while cursor < len(masked) and masked[cursor].isspace():
            cursor += 1
        title = None
        if cursor < len(masked) and masked[cursor] == "[":
            title, _ = group(text, cursor, "[", "]")
        labels = LABEL.findall(masked[start:token.end()])
        environments.append({
            "kind": kind, "start": start, "end": token.end(),
            "line_start": text.count("\n", 0, start) + 1,
            "line_end": text.count("\n", 0, token.end()) + 1,
            "title": title, "labels": labels,
            "label": labels[0] if labels else None,
            "tex": text[start:token.end()],
        })
    require(not stack, f"Unclosed environment in {path}")
    statements = [env for env in environments if env["kind"] != "proof"]
    proofs = [env for env in environments if env["kind"] == "proof"]
    assigned = 0
    for index, statement in enumerate(statements):
        stop = statements[index + 1]["start"] if index + 1 < len(statements) else len(text)
        following = [p for p in proofs if statement["end"] <= p["start"] < stop]
        require(len(following) <= 1, f"Multiple adjacent proofs for {statement['label']}")
        if following:
            require(not SECTION.search(masked[statement["end"]:following[0]["start"]]),
                    f"Proof crosses a section boundary at {statement['label']}")
        statement["proof"] = following[0] if following else None
        assigned += len(following)
        statement["formal_macros"] = {"three": [], "prior": []}
        tail = masked[statement["end"]:stop]
        for status in STATUS.finditer(tail):
            names, _ = group(tail, status.end() - 1)
            statement["formal_macros"][status[1]].extend(
                name.strip() for name in names.split(";") if name.strip())
    require(assigned == len(proofs), f"Unassociated proof environment in {path}")
    return text, masked, statements


def active_statements():
    master = mask_comments(MASTER.read_text(encoding="utf-8"))
    included = re.findall(r"\\input\{chapters/([^{}]+)\}", master)
    require(tuple(included) == CHAPTERS, "Active chapter list changed; review census scope")
    section, counter = 0, 0
    ordinals, rows, files = collections.Counter(), [], []
    for chapter_index, name in enumerate(included):
        path = MANUSCRIPT / "chapters" / name
        _, masked, statements = parse_environments(path)
        require(not re.search(r"\\(?:setcounter|addtocounter)\{(?:section|theorem)\}", masked),
                f"Explicit counter change requires parser review: {path}")
        branch = "canonical" if chapter_index < 2 else "expanded"
        events = [(m.start(), "section", m) for m in SECTION.finditer(masked) if not m[1]]
        events.extend((row["start"], "statement", row) for row in statements)
        chapter_ordinal = 0
        for _, kind, event in sorted(events, key=lambda x: x[0]):
            if kind == "section":
                section += 1
                counter = 0
                continue
            counter += 1
            chapter_ordinal += 1
            ordinals[branch] += 1
            event.update({
                "branch": branch, "source_ordinal": ordinals[branch],
                "chapter_ordinal": chapter_ordinal, "section": section,
                "source_number": f"{section}.{counter}",
                "source_file": locator(path), "source_file_sha256": sha_file(path),
            })
            rows.append(event)
        files.append(file_record(path))
    return rows, files


def historical_statements():
    cross_path = HISTORICAL / "SOURCE_CROSSWALK.json"
    cross = json.loads(cross_path.read_text(encoding="utf-8"))
    rc1_path = ROOT / "provenance/rc1_release/metadata/MANUSCRIPT_STATEMENT_REGISTER_v1.0.0.json"
    rc1 = json.loads(rc1_path.read_text(encoding="utf-8"))
    rc1_rows = {(r["branch"], r["source_ordinal"]): r for r in rc1["rows"]}
    comparison = {(r["branch"], r["ordinal"]): dict(r) for r in cross["statements"]}
    inputs = [file_record(cross_path), file_record(rc1_path)]
    for branch in ("canonical", "expanded"):
        path = HISTORICAL / "source" / (branch + ".tex")
        _, _, statements = parse_environments(path)
        require(len(statements) == sum(key[0] == branch for key in comparison),
                f"Historical {branch} census disagrees with crosswalk")
        for ordinal, statement in enumerate(statements, 1):
            old = comparison[(branch, ordinal)]
            require(sha_text(statement["tex"]) == old["source_statement_sha256"],
                    f"Historical raw environment hash mismatch: {branch}/{ordinal}")
            old["proof_sha256"] = sha_text(statement["proof"]["tex"]) if statement["proof"] else None
            old["source_file"] = locator(path)
            old["rc1_evidence_class"] = rc1_rows[(branch, ordinal)]["evidence_class"]
        inputs.append(file_record(path))
    return comparison, inputs


def read_aux(path):
    """Read nested newlabel records from the current compiled main aux."""
    if path is None:
        return {}, None
    require(path.is_file(), f"Requested compiled aux does not exist: {path}")
    text, labels = mask_comments(path.read_text(encoding="utf-8")), {}
    for match in re.finditer(r"\\newlabel\s*\{", text):
        label, end = group(text, match.end() - 1)
        if label.endswith("@cref"):
            continue
        payload, _ = group(text, end)
        fields, cursor = [], 0
        while payload[cursor:].strip():
            value, cursor = group(payload, cursor)
            fields.append(value)
        require(len(fields) >= 2, f"Malformed newlabel for {label}")
        value = {
            "number": fields[0], "printed_page": fields[1],
            "title_tex": fields[2] if len(fields) > 2 else None,
            "destination": fields[3] if len(fields) > 3 else None,
        }
        require(label not in labels or labels[label] == value, f"Conflicting aux label: {label}")
        labels[label] = value
    require(bool(labels), "No labels found in requested aux")
    return labels, file_record(path)


def load_formal_evidence():
    """Check receipt/source/log hashes and collect exact audited/replayed names."""
    directory = ROOT / "formal"
    reports, refs = {}, {}
    for phase in ("full", "audit", "replay"):
        path = directory / "verification" / ("final_release_" + phase) / "report.json"
        require(path.is_file(), f"Final formal receipt required: {path}")
        report = json.loads(path.read_text(encoding="utf-8"))
        require(report.get("status") == "PASS", f"Nonpassing formal receipt: {path}")
        for command in report["commands"]:
            require(command.get("accepted") is True and command.get("status") == "PASS"
                    and command.get("exit_code") == 0 and command.get("source_unchanged") is True,
                    f"Unaccepted command in {path}")
            source, log = directory / command["source"], directory / command["log"]
            require(source.is_file() and sha_file(source) == command["source_sha256"],
                    f"Formal source changed since receipt: {source}")
            require(log.is_file() and sha_file(log) == command["log_sha256"],
                    f"Formal log missing or changed: {log}")
        reports[phase] = report
        refs[phase] = {
            **file_record(path), "started_utc": report["started_utc"],
            "status": report["status"], "compiler_sha256": report["compiler_sha256"],
        }
    require(reports["full"].get("own_objects_initially_empty") is True,
            "Final full build must record an empty initial production object directory")
    require(len({report["compiler_sha256"] for report in reports.values()}) == 1,
            "Formal receipts use different compiler hashes")
    require(len({json.dumps(report["upstream_revisions"], sort_keys=True)
                 for report in reports.values()}) == 1, "Formal receipts use different upstream pins")
    compiled = {command["module"]: command for command in reports["full"]["commands"]}
    owned, replayed = {}, {}
    for phase, prefix, table in (("audit", "OWNED ", owned), ("replay", "REPLAY_CHECKED ", replayed)):
        require(len(reports[phase]["commands"]) == 1, f"Unexpected {phase} receipt structure")
        command = reports[phase]["commands"][0]
        log = directory / command["log"]
        lines = log.read_text(encoding="utf-8").splitlines()
        marker = "OWNED_AUDIT_PASS " if phase == "audit" else "REPLAY_CLOSURE_PASS "
        require(any(line.startswith(marker) for line in lines), f"Missing success marker in {log}")
        for line in lines:
            if line.startswith(prefix):
                record = json.loads(line[len(prefix):])
                require(record["name"] not in table, f"Duplicate {phase} inventory name")
                table[record["name"]] = record
        require(bool(table), f"Empty {phase} inventory")
        refs[phase]["log"] = file_record(log)
        refs[phase]["instrumentation_source"] = file_record(directory / command["source"])
    refs["full"]["upstream_revisions"] = reports["full"]["upstream_revisions"]
    refs["full"]["own_objects_initially_empty"] = True
    return compiled, owned, replayed, refs


def formal_target(name, compiled, owned, replayed):
    require(name in owned, f"Mapped declaration absent from current owned audit: {name}")
    record = owned[name]
    require(not record["runtime_only"], f"Runtime helper cannot be a mathematical target: {name}")
    require(name in replayed, f"Mapped declaration absent from current replay: {name}")
    require(record["module"] in compiled, f"Mapped owner module absent from full build: {name}")
    command = compiled[record["module"]]
    require(replayed[name]["module"] in compiled, f"Replay owner absent from full build: {name}")
    return {
        "name": name, "module": record["module"], "kind": record["kind"],
        "source_file": "formal/" + command["source"],
        "source_file_sha256": command["source_sha256"],
        "type_expr_sha256": sha_text(record["type_expr"]), "axioms": record["axioms"],
        "compile_log": "formal/" + command["log"], "compile_log_sha256": command["log_sha256"],
        "compiled_object_sha256_recorded": command["object_sha256"],
        "current_source_matches_compiler_receipt": True,
        "owned_audit_name_present": True, "kernel_replay_name_present": True,
        "replay_owner_module": replayed[name]["module"],
    }


def classify(statement, section16):
    names = list(dict.fromkeys(statement["formal_macros"]["three"]))
    inherited = list(dict.fromkeys(statement["formal_macros"]["prior"]))
    kind, label = statement["kind"], statement["label"]
    if statement["branch"] == "canonical":
        if names:
            evidence, coverage = "PAPER_III_FINITE_MATCHED_FORMAL_SCOPE", "MATCHED_NAMED_FINITE_CONTRACT"
            notes = ("The active Paper III status macro supplies exact targets; current "
                     "source, owned-audit membership, and kernel-replay membership are checked.")
            if inherited:
                evidence = "MIXED_PAPER_III_AND_INHERITED_FORMAL_SCOPE"
                coverage = "MATCHED_PAPER_III_CLAUSES_WITH_INHERITED_BRIDGE"
                notes += (" Additional Papers I–II targets remain explicitly inherited; "
                          "they are not promoted to fresh Paper III replay.")
        elif inherited:
            evidence, coverage = "INHERITED_PAPERS_I_II_FORMAL_CONTRACT", "INHERITED_FORMAL_SCOPE_ONLY"
            notes = ("The active inherited status macro names the Papers I–II contract. "
                     "This register does not report a new replay of those earlier modules.")
        else:
            require(kind not in RESULT_KINDS, f"Canonical result has no status macro: {label}")
            evidence, coverage = "CANONICAL_DEFINITION_EXAMPLE_OR_SCOPE", "NO_INDEPENDENT_RESULT_MAPPING"
            notes = "Census item; not an additional result in the finite completion denominator."
    elif label in section16:
        names = [target["name"] for target in section16[label]["targets"]]
        evidence, coverage = "SECTION16_RESTORED_SOURCE_MATCHED_FORMAL_SCOPE", "MATCHED_EXACT_COORDINATE_SCOPE"
        notes = ("Ordinary exact coordinate mathematics with restored project Lean sources "
                 "and current build/audit/replay evidence. Historical Section 16 correspondence "
                 "supplies exact names, whose identity is checked against current evidence.")
    elif label in SECTION17:
        coverage, names, notes = SECTION17[label]
        evidence = ("SECTION17_PARTIAL_FORMAL_CLAUSES" if coverage == "PARTIAL_CLAUSE_COVERAGE"
                    else "SECTION17_MATCHED_FORMAL_SCOPE" if names
                    else "SECTION17_ORDINARY_PROOF_NO_MATCHED_LEAN")
    elif kind == "standardfact":
        evidence, coverage = "EXTERNAL_STANDARD_FACT_ORDINARY_MATHEMATICS", "NO_MATCHED_PROJECT_LEAN_FORMALIZATION"
        notes = ("Explicit classical input in the ordinary manuscript. No matched expanded "
                 "Paper III Lean declaration is supplied; the census does not add a formal theorem.")
    elif kind in RESULT_KINDS:
        require(statement["section"] >= 18, f"Unmapped early expanded result: {label}")
        evidence, coverage = "SECTIONS18_27_ORDINARY_PROOF_NO_MATCHED_EXPANDED_LEAN", "NO_MATCHED_PROJECT_LEAN_FORMALIZATION"
        notes = ("Ordinary mathematical result with active proof and standing hypotheses "
                 "pinned by source hashes. No matched expanded Lean formalization was recovered.")
    else:
        evidence, coverage = "EXPANDED_DEFINITION_EXAMPLE_OR_SCOPE", "NO_INDEPENDENT_RESULT_MAPPING"
        notes = "Definition, example, remark, or scope item; no independent Lean theorem is inferred."
    return evidence, coverage, notes, names, inherited


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aux", type=Path,
                        help="Current main aux; defaults to the active manuscript aux if present.")
    parser.add_argument("--pdf", type=Path,
                        help="Current PDF to hash; defaults to the PDF beside the selected aux.")
    args = parser.parse_args()
    aux_path = args.aux.expanduser().resolve() if args.aux else MANUSCRIPT / (MASTER.stem + ".aux")
    if not args.aux and not aux_path.is_file():
        aux_path = None
    pdf_path = args.pdf.expanduser().resolve() if args.pdf else (aux_path.with_suffix(".pdf") if aux_path else None)
    if args.pdf:
        require(pdf_path.is_file(), f"Requested PDF does not exist: {pdf_path}")
    elif pdf_path and not pdf_path.is_file():
        pdf_path = None

    statements, source_files = active_statements()
    comparison, comparison_inputs = historical_statements()
    aux, aux_record = read_aux(aux_path)
    compiled, owned, replayed, formal_receipts = load_formal_evidence()
    section16_path = BASE / "coverage/SECTION16_CORRESPONDENCE.json"
    section16_data = json.loads(section16_path.read_text(encoding="utf-8"))
    section16 = {row["manuscript_label"]: row for row in section16_data["rows"] if row.get("manuscript_label")}
    rows, declarations = [], {}
    for statement in statements:
        key = (statement["branch"], statement["source_ordinal"])
        require(key in comparison, f"No historical identity for {key}")
        old = comparison[key]
        require(old["kind"] == statement["kind"] and old.get("source_label") == statement["label"],
                f"Active/historical identity mismatch for {key}; review reorder or relabel")
        digest, proof = sha_text(statement["tex"]), statement["proof"]
        proof_digest = sha_text(proof["tex"]) if proof else None
        label = statement["label"]
        pagination = aux.get(label) if label else None
        if aux and label:
            require(pagination is not None, f"Active statement label absent from aux: {label}")
            require(pagination["number"] == statement["source_number"],
                    f"Aux/source number disagreement for {label}: {pagination['number']} versus {statement['source_number']}")
        evidence, coverage, notes, names, inherited = classify(statement, section16)
        for name in names:
            if name not in declarations:
                declarations[name] = formal_target(name, compiled, owned, replayed)
        rows.append({
            "branch": statement["branch"], "source_ordinal": statement["source_ordinal"],
            "chapter_ordinal": statement["chapter_ordinal"], "kind": statement["kind"],
            "is_result_like": statement["kind"] in RESULT_KINDS,
            "is_external_standard_fact": statement["kind"] == "standardfact",
            "section": statement["section"],
            "number": pagination["number"] if pagination else statement["source_number"],
            "number_source": "CURRENT_COMPILED_AUX" if pagination else "ACTIVE_SOURCE_COUNTER",
            "title": statement["title"], "label": label, "labels": statement["labels"],
            "printed_page": pagination["printed_page"] if pagination else None,
            "page": pagination["printed_page"] if pagination else None,
            "pdf_destination": pagination["destination"] if pagination else None,
            "physical_pdf_page": None,
            "source_file": statement["source_file"], "source_branch_file": statement["source_file"],
            "source_file_sha256": statement["source_file_sha256"],
            "source_line_start": statement["line_start"], "source_line_end": statement["line_end"],
            "statement_sha256": digest, "source_statement_sha256": digest,
            "proof_present": proof is not None, "proof_sha256": proof_digest,
            "proof_line_start": proof["line_start"] if proof else None,
            "proof_line_end": proof["line_end"] if proof else None,
            "evidence_class": evidence, "formal_coverage": coverage, "mapping_notes": notes,
            "finite_contract_count_group": (
                "INHERITED_INVOLVING" if inherited else "PAPER_III_ONLY"
            ) if statement["branch"] == "canonical" and statement["kind"] in RESULT_KINDS else None,
            "accepted_lean_targets": names, "inherited_lean_targets": inherited,
            "new_lean_kernel_replay_this_closeout": bool(names),
            "replay_flag_scope": "Named Paper III targets only; not every clause or inherited target in the environment.",
            "historical_comparison": {
                "branch": old["branch"], "source_ordinal": old["ordinal"],
                "label": old.get("source_label"), "source_file": old["source_file"],
                "statement_sha256": old["source_statement_sha256"], "proof_sha256": old["proof_sha256"],
                "statement_byte_identical": digest == old["source_statement_sha256"],
                "proof_byte_identical": (proof_digest == old["proof_sha256"]
                                        if proof_digest is not None or old["proof_sha256"] is not None else None),
                "number": old.get("number"), "printed_page": old.get("printed_page") or old.get("page"),
                "physical_pdf_page": old.get("physical_pdf_page"), "rc1_evidence_class": old["rc1_evidence_class"],
            },
        })
    result_rows = [row for row in rows if row["is_result_like"]]
    canonical = [row for row in result_rows if row["branch"] == "canonical"]
    counts = {
        "total_environments": len(rows), "non_standard_result_environments": len(result_rows),
        "external_standard_fact_environments": sum(row["is_external_standard_fact"] for row in rows),
        "prooflike_statements_including_external_standard_facts": sum(row["is_result_like"] or row["is_external_standard_fact"] for row in rows),
        "explicit_proof_environments": sum(row["proof_present"] for row in rows),
        "canonical_environments": sum(row["branch"] == "canonical" for row in rows),
        "expanded_environments": sum(row["branch"] == "expanded" for row in rows),
        "canonical_result_environments": len(canonical),
        "canonical_results_with_paper_iii_targets": sum(bool(row["accepted_lean_targets"]) for row in canonical),
        "canonical_results_paper_iii_only": sum(bool(row["accepted_lean_targets"]) and not row["inherited_lean_targets"] for row in canonical),
        "canonical_results_inherited_involving": sum(bool(row["inherited_lean_targets"]) for row in canonical),
        "canonical_results_mixed_scope": sum(bool(row["accepted_lean_targets"]) and bool(row["inherited_lean_targets"]) for row in canonical),
        "canonical_results_inherited_only": sum(not row["accepted_lean_targets"] and bool(row["inherited_lean_targets"]) for row in canonical),
        "section16_result_environments": sum(row["section"] == 16 for row in result_rows),
        "section17_result_environments": sum(row["section"] == 17 for row in result_rows),
        "section17_result_environments_with_matched_clauses": sum(row["section"] == 17 and bool(row["accepted_lean_targets"]) for row in result_rows),
        "section17_result_environments_without_matched_lean": sum(row["section"] == 17 and not row["accepted_lean_targets"] for row in result_rows),
        "later_result_environments_without_matched_expanded_lean": sum(row["section"] >= 18 and not row["accepted_lean_targets"] for row in result_rows),
        "labels_located_in_current_aux": sum(row["number_source"] == "CURRENT_COMPILED_AUX" for row in rows),
        "active_statements_changed_from_raw_source": sum(not row["historical_comparison"]["statement_byte_identical"] for row in rows),
        "active_proofs_changed_from_raw_source": sum(row["historical_comparison"]["proof_byte_identical"] is False for row in rows),
    }
    expected = {
        "total_environments": 167, "non_standard_result_environments": 98,
        "external_standard_fact_environments": 2, "canonical_environments": 66, "expanded_environments": 101,
        "canonical_result_environments": 30, "canonical_results_paper_iii_only": 26,
        "canonical_results_inherited_involving": 4, "canonical_results_inherited_only": 3,
        "canonical_results_mixed_scope": 1, "section16_result_environments": 3,
        "section17_result_environments": 6, "section17_result_environments_with_matched_clauses": 4,
        "section17_result_environments_without_matched_lean": 2,
        "later_result_environments_without_matched_expanded_lean": 59,
    }
    for name, value in expected.items():
        require(counts[name] == value, f"Census changed: {name} = {counts[name]}, expected {value}")
    require(len(comparison) == len(rows), "Historical identities were omitted")
    labels = [row["label"] for row in rows if row["label"]]
    require(len(set(labels)) == len(labels), "Duplicate active statement label")
    manifest = {record["path"]: record["sha256"] for record in [file_record(MASTER)] + source_files}
    output = {
        "schema": "komorebi.paper_iii.manuscript_statement_register/2",
        "status": "ACTIVE_SOURCE_IDENTITY_VERIFIED__FORMAL_SCOPE_RECORDED_PER_CLAUSE", **counts,
        "histogram": dict(sorted(collections.Counter(row["evidence_class"] for row in rows).items())),
        "kinds": dict(sorted(collections.Counter(row["kind"] for row in rows).items())),
        "result_counts_by_section": dict(sorted(collections.Counter(str(row["section"]) for row in result_rows).items(), key=lambda item: int(item[0]))),
        "active_master": file_record(MASTER), "active_chapters": source_files,
        "active_source_manifest_sha256": sha_text(json.dumps(manifest, sort_keys=True, separators=(",", ":"))),
        "builder": file_record(Path(__file__).resolve()),
        "pagination": {
            "status": "CURRENT_AUX_LABELS_VERIFIED" if aux_record else "AWAITING_CURRENT_COMPILED_AUX",
            "aux": aux_record, "pdf": file_record(pdf_path) if pdf_path else None,
            "notes": ("Numbers and printed pages come from the selected current aux where a statement "
                      "has a label. Unlabelled environments use the active section/theorem counter and "
                      "have no invented page. Physical PDF pages are not inferred from archived offsets. "
                      "Rerun with --aux after the final PDF build."),
        },
        "selected_manuscript_sha256": sha_file(pdf_path) if pdf_path else None,
        "hash_semantics": {
            "statement_sha256": ("SHA-256 of the exact UTF-8 active begin/end environment, including title "
                                 "and labels, excluding following proof and status macros. "
                                 "source_statement_sha256 is the same active hash for compatibility."),
            "proof_sha256": ("SHA-256 of the separate exact UTF-8 following proof environment before the "
                             "next registered environment or section. Null means no separate explicit "
                             "proof environment, not an unproved result."),
            "context": ("Whole active master and chapter hashes pin standing hypotheses, adjacent "
                        "explanatory prose, and status macros outside environments. Byte identity "
                        "is a source comparison, not a correctness verdict."),
            "historical_comparison": ("Only comparison fields refer to archived raw statements, "
                                      "proofs, old pages, or RC1 classes; they do not supply selected text."),
        },
        "mapping_notes": (
            "167 environments comprise 98 result-like environments, two external standard facts, and "
            "67 other items. These are manuscript counts, not Lean declaration counts. The finite 30 "
            "results divide into 26 Paper-III-only and four inherited-involving results. Those four "
            "comprise three inherited-only rows and one mixed row (orbit support); hence 27 rows "
            "have at least one Paper III target. Section 16 "
            "has three ordinary results with matched restored sources. Section 17 has four result "
            "environments with matched formal clauses (the norm proposition is partial) and two "
            "ordinary results without a project Lean match. The later 59 results retain ordinary "
            "proof status. Formal declarations, constructions, generated constants, and manuscript "
            "environments have different denominators."),
        "historical_comparison_inputs": comparison_inputs + [file_record(section16_path)],
        "formal_evidence": {
            "receipts": formal_receipts,
            "notes": ("This builder verifies current source and log hashes and exact names in existing "
                      "passing full-build, owned-audit, and kernel-replay records. It does not itself "
                      "execute Lean. Papers I–II targets remain inherited. Object hashes are observations "
                      "in compiler receipts, not fresh object hashing by this builder."),
            "mapped_declarations": dict(sorted(declarations.items())),
        },
        "rows": rows,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    json_path, csv_path = (OUT / ("MANUSCRIPT_STATEMENT_REGISTER_v1.0.0." + extension) for extension in ("json", "csv"))
    json_path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    fields = [
        "branch", "source_ordinal", "chapter_ordinal", "kind", "is_result_like",
        "is_external_standard_fact", "section", "number", "number_source", "title", "label",
        "printed_page", "pdf_destination", "source_file", "source_file_sha256",
        "source_line_start", "source_line_end", "statement_sha256", "proof_present", "proof_sha256",
        "proof_line_start", "proof_line_end", "evidence_class", "formal_coverage", "mapping_notes",
        "finite_contract_count_group",
        "accepted_lean_targets", "inherited_lean_targets", "new_lean_kernel_replay_this_closeout",
        "replay_flag_scope", "historical_source_file", "historical_statement_sha256", "historical_proof_sha256",
        "statement_byte_identical", "proof_byte_identical", "historical_number", "historical_printed_page",
        "historical_physical_pdf_page", "rc1_evidence_class",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            flattened = {field: row.get(field) for field in fields}
            for field in ("accepted_lean_targets", "inherited_lean_targets"):
                flattened[field] = ";".join(row[field])
            old = row["historical_comparison"]
            for field in ("source_file", "statement_sha256", "proof_sha256",
                          "number", "printed_page", "physical_pdf_page"):
                flattened["historical_" + field] = old[field]
            for field in ("statement_byte_identical", "proof_byte_identical", "rc1_evidence_class"):
                flattened[field] = old[field]
            writer.writerow(flattened)
    print(json.dumps({
        "counts": counts, "pagination_status": output["pagination"]["status"],
        "outputs": [file_record(json_path), file_record(csv_path)],
    }, indent=2))


if __name__ == "__main__":
    main()
