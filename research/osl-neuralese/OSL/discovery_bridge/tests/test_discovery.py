from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from osl_discovery import (
    ProposalError,
    RegistryError,
    append_admission,
    digest_object,
    emit_osl,
    quotient_classes,
    synthesize,
    verify_certificate,
    verify_registry,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def load(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


class DiscoveryTests(unittest.TestCase):
    def test_flip_both_is_admitted(self) -> None:
        certificate = synthesize(load("flip_both_proposal.json"))
        self.assertEqual(certificate["status"], "ADMITTED")
        self.assertEqual(certificate["decision"], "admit")
        self.assertEqual(certificate["representative"], ["flip_left", "flip_right"])
        self.assertGreaterEqual(certificate["equivalent_program_count"], 2)
        self.assertTrue(all(item["passed"] for item in certificate["law_results"]))

    def test_equivalent_spellings_share_one_transformation(self) -> None:
        certificate = synthesize(load("flip_both_proposal.json"))
        programs = certificate["equivalent_programs"]
        self.assertIn(["flip_left", "flip_right"], programs)
        self.assertIn(["flip_right", "flip_left"], programs)

    def test_one_demonstration_is_quarantined_as_ambiguous(self) -> None:
        certificate = synthesize(load("ambiguous_proposal.json"))
        self.assertEqual(certificate["status"], "AMBIGUOUS")
        self.assertEqual(certificate["decision"], "quarantine")
        self.assertGreater(certificate["compatible_quotient_count"], 1)
        self.assertEqual(certificate["witness"]["kind"], "separating_state")

    def test_conflicting_demonstrations_are_rejected(self) -> None:
        certificate = synthesize(load("inconsistent_proposal.json"))
        self.assertEqual(certificate["status"], "UNSATISFIABLE")
        self.assertEqual(certificate["decision"], "reject")
        self.assertEqual(certificate["witness"]["kind"], "conflicting_demonstrations")

    def test_false_law_returns_a_witness(self) -> None:
        proposal = load("flip_both_proposal.json")
        proposal["claimed_laws"] = [
            {
                "law_id": "false_idempotence",
                "left": ["$candidate", "$candidate"],
                "right": ["$candidate"],
            }
        ]
        certificate = synthesize(proposal)
        self.assertEqual(certificate["status"], "REJECTED_FALSE_LAW")
        self.assertIsNotNone(certificate["witness"])
        self.assertNotEqual(
            certificate["witness"]["left_output"],
            certificate["witness"]["right_output"],
        )

    def test_primitive_alias_is_rejected_as_nonnovel(self) -> None:
        proposal = load("flip_both_proposal.json")
        proposal["candidate"]["name"] = "renamed_flip_left"
        proposal["max_depth"] = 1
        proposal["demonstrations"] = [
            {
                "input": {"left": left, "right": right},
                "output": {"left": not left, "right": right},
            }
            for left in (False, True)
            for right in (False, True)
        ]
        proposal["claimed_laws"] = []
        certificate = synthesize(proposal)
        self.assertEqual(certificate["status"], "REJECTED_NONNOVEL")
        self.assertEqual(certificate["witness"]["shortest_representative"], ["flip_left"])

    def test_unknown_primitive_is_a_malformed_proposal(self) -> None:
        proposal = load("flip_both_proposal.json")
        proposal["claimed_laws"][0]["left"] = ["teleport"]
        with self.assertRaises(ProposalError):
            synthesize(proposal)

    def test_illegal_world_state_is_a_malformed_proposal(self) -> None:
        proposal = load("flip_both_proposal.json")
        proposal["demonstrations"][0]["input"] = {"cap": 0}
        with self.assertRaises(ProposalError):
            synthesize(proposal)

    def test_deterministic_replay_and_integrity(self) -> None:
        proposal = load("flip_both_proposal.json")
        first = synthesize(proposal)
        second = synthesize(proposal)
        self.assertEqual(first, second)
        self.assertTrue(verify_certificate(proposal, first)["valid"])

    def test_certificate_tampering_is_detected(self) -> None:
        proposal = load("flip_both_proposal.json")
        certificate = synthesize(proposal)
        certificate["representative"] = ["flip_left"]
        report = verify_certificate(proposal, certificate)
        self.assertFalse(report["valid"])
        self.assertFalse(report["integrity_valid"])

    def test_malformed_embedded_proposal_fails_closed(self) -> None:
        certificate = synthesize(load("flip_both_proposal.json"))
        certificate["proposal"]["candidate"]["world"] = "unknown_world"
        certificate.pop("certificate_digest")
        certificate["certificate_digest"] = digest_object(certificate)
        report = verify_certificate(None, certificate)
        self.assertFalse(report["valid"])
        self.assertIsNotNone(report["error"])

    def test_registry_chain_and_tamper_detection(self) -> None:
        certificate = synthesize(load("flip_both_proposal.json"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.jsonl"
            append_admission(path, certificate)
            self.assertTrue(verify_registry(path)["valid"])
            text = path.read_text(encoding="utf-8").replace("flip_both", "flip_both_tampered", 1)
            path.write_text(text, encoding="utf-8")
            self.assertFalse(verify_registry(path)["valid"])

    def test_registry_rejects_nonadmitted_candidate(self) -> None:
        certificate = synthesize(load("ambiguous_proposal.json"))
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(RegistryError):
                append_admission(Path(directory) / "registry.jsonl", certificate)

    def test_registry_rejects_duplicate_transformation(self) -> None:
        certificate = synthesize(load("flip_both_proposal.json"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.jsonl"
            append_admission(path, certificate)
            with self.assertRaises(RegistryError):
                append_admission(path, certificate)

    def test_registry_rejects_rehashed_forged_admission(self) -> None:
        certificate = synthesize(load("flip_both_proposal.json"))
        certificate["representative"] = ["flip_left"]
        certificate.pop("certificate_digest")
        certificate["certificate_digest"] = digest_object(certificate)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(RegistryError):
                append_admission(Path(directory) / "registry.jsonl", certificate)

    def test_registry_tip_anchor_detects_suffix_truncation(self) -> None:
        certificate = synthesize(load("flip_both_proposal.json"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.jsonl"
            entry = append_admission(path, certificate)
            self.assertTrue(verify_registry(path, expected_tip=entry["entry_digest"])["valid"])
            self.assertFalse(verify_registry(path, expected_tip="f" * 64)["valid"])

    def test_quotient_counts_are_deterministic(self) -> None:
        first = quotient_classes("algebra", 3)
        second = quotient_classes("algebra", 3)
        self.assertEqual(first, second)
        self.assertGreater(len(first), 1)

    def test_adapter_emits_each_boundary_decision(self) -> None:
        admitted = emit_osl(load("flip_both_proposal.json"), synthesize(load("flip_both_proposal.json")))
        ambiguous = emit_osl(load("ambiguous_proposal.json"), synthesize(load("ambiguous_proposal.json")))
        rejected = emit_osl(load("inconsistent_proposal.json"), synthesize(load("inconsistent_proposal.json")))
        self.assertIn("admit flip_both", admitted)
        self.assertIn("status provisional", ambiguous)
        self.assertIn("reject_candidate contradictory_operator", rejected)

    def test_adapter_rejects_a_tampered_certificate(self) -> None:
        proposal = load("flip_both_proposal.json")
        certificate = synthesize(proposal)
        certificate["decision"] = "reject"
        with self.assertRaises(ProposalError):
            emit_osl(proposal, certificate)


@unittest.skipUnless(os.environ.get("OSL_CORE_REFERENCE"), "set OSL_CORE_REFERENCE for integration replay")
class OSLCoreIntegrationTests(unittest.TestCase):
    def test_all_emitted_decisions_execute_in_osl_core_0_3(self) -> None:
        reference = Path(os.environ["OSL_CORE_REFERENCE"])
        sys.path.insert(0, str(reference))
        try:
            from osl_core import OSLRuntime

            for proposal_name in (
                "flip_both_proposal.json",
                "ambiguous_proposal.json",
                "inconsistent_proposal.json",
            ):
                proposal = load(proposal_name)
                certificate = synthesize(proposal)
                state = OSLRuntime().run_text(emit_osl(proposal, certificate))
                self.assertEqual(state.assertions, 2)
        finally:
            sys.path.pop(0)


if __name__ == "__main__":
    unittest.main()
