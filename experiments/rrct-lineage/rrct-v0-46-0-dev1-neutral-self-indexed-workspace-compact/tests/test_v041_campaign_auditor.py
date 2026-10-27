from __future__ import annotations

import ast
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDITOR_PATH = ROOT / "validation" / "audit_v041_campaign.py"
REPLAY_PATH = ROOT / "validation" / "audit_v041_development_matrix.py"


def _load_auditor():
    name = "_test_v041_campaign_auditor"
    spec = importlib.util.spec_from_file_location(name, AUDITOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


AUDITOR = _load_auditor()


def _make_exact_topology(root: Path, seeds: list[int]) -> None:
    for name in ("pairs", "_seed_claims", "_condition_claims", "_attempt_claims"):
        (root / name).mkdir(parents=True)
    for seed in seeds:
        (root / "_seed_claims" / f"seed-{seed}.json").touch()
        for condition in AUDITOR.CONDITIONS:
            condition_root = root / "pairs" / f"seed-{seed}" / condition
            condition_root.mkdir(parents=True)
            for filename in AUDITOR.CONDITION_FILES:
                (condition_root / filename).touch()
            (root / "_condition_claims" / f"seed-{seed}--{condition}.json").touch()
            (root / "_attempt_claims" / f"attempt-{seed}-{condition}.json").touch()


class CampaignAuditorTests(unittest.TestCase):
    def test_independent_auditors_do_not_import_rrct(self) -> None:
        for path in (AUDITOR_PATH, REPLAY_PATH):
            with self.subTest(path=path.name):
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
                imported: list[str] = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported.extend(alias.name for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module is not None:
                        imported.append(node.module)
                self.assertFalse(
                    any(name == "rrct" or name.startswith("rrct.") for name in imported)
                )

    def test_topology_requires_exact_four_by_six_without_extras(self) -> None:
        seeds = [101, 102, 103, 104]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _make_exact_topology(root, seeds)
            topology = AUDITOR.verify_topology(root, seeds)
            self.assertEqual(topology["attempt_claim_count"], 24)

            (root / "pairs" / "seed-101" / "UNDECLARED_ARM").mkdir()
            with self.assertRaises(AUDITOR.CampaignAuditError):
                AUDITOR.verify_topology(root, seeds)

    def test_topology_rejects_dangling_attempt_claim(self) -> None:
        seeds = [101, 102, 103, 104]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _make_exact_topology(root, seeds)
            (root / "_attempt_claims" / "dangling.json").touch()
            with self.assertRaises(AUDITOR.CampaignAuditError):
                AUDITOR.verify_topology(root, seeds)

    def test_cohort_decision_is_exact_all_four_conjunction(self) -> None:
        seeds = [101, 102, 103, 104]
        passing = [{"seed": seed, "all_primary_endpoints_met": True} for seed in seeds]
        decision = AUDITOR.cohort_decision(
            passing,
            seeds,
            topology_valid=True,
            campaign_claim_chain_valid=True,
        )
        self.assertTrue(all(decision.values()))

        one_failed = [dict(record) for record in passing]
        one_failed[-1]["all_primary_endpoints_met"] = False
        decision = AUDITOR.cohort_decision(
            one_failed,
            seeds,
            topology_valid=True,
            campaign_claim_chain_valid=True,
        )
        self.assertFalse(decision["C04_all_four_seeds_meet_every_primary_endpoint"])

        decision = AUDITOR.cohort_decision(
            passing[:3],
            seeds,
            topology_valid=True,
            campaign_claim_chain_valid=True,
        )
        self.assertFalse(decision["C01_exact_four_registered_seeds"])
        self.assertFalse(decision["C04_all_four_seeds_meet_every_primary_endpoint"])


if __name__ == "__main__":
    unittest.main()
