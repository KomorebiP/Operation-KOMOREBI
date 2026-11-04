"""Regression checks for accepting only the intended Lean proof evidence.

These fixtures exercise source and diagnostic admission boundaries. They do
not replace the native compiler, axiom audit, or kernel replay of a companion.
"""

import copy
from pathlib import Path
import tempfile
import unittest

from verify_lean_companion import (
    FORBIDDEN_DIAGNOSTICS,
    diagnostics_match,
    explicit_declarations,
    inventory_names,
    parse_axioms,
    source_inventory,
)


class LeanCompanionSourceGuardTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="lean-companion-guard-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.path = "GuardFixture/Main.lean"
        self.source = (
            "namespace Komorebi.GuardFixture\n"
            "theorem good : True := True.intro\n"
            "end Komorebi.GuardFixture\n"
        )
        self.write(self.path, self.source)
        self.write("GuardFixture.lean", "import GuardFixture.Main\n")
        self.config = {
            "library": "GuardFixture",
            "production": [self.path],
            "declarations": [
                {
                    "name": "Komorebi.GuardFixture.good",
                    "kind": "theorem",
                    "source": self.path,
                }
            ],
        }

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def test_valid_named_proof_and_exact_root_import_are_accepted(self):
        source_inventory(self.root, self.config)
        self.assertEqual(inventory_names(self.config), ["Komorebi.GuardFixture.good"])

    def test_private_axiom_and_hidden_false_proof_are_rejected(self):
        self.write(
            self.path,
            "namespace Komorebi.GuardFixture\n"
            "private axiom untrusted : False\n"
            "theorem good : True := True.intro\n"
            "private theorem hidden_false : False := untrusted\n"
            "end Komorebi.GuardFixture\n",
        )
        with self.assertRaises(ValueError):
            source_inventory(self.root, self.config)

    def test_positive_control_cannot_admit_a_custom_axiom(self):
        path = "Controls/CustomAxiom.lean"
        self.write(
            path,
            "namespace Komorebi.GuardControls\n"
            "axiom untrusted : False\n"
            "theorem false_control : False := untrusted\n"
            "end Komorebi.GuardControls\n",
        )
        with self.assertRaises(ValueError):
            explicit_declarations(self.root, path)

    def test_positive_control_cannot_use_an_admission_or_native_decision(self):
        path = "Controls/Admission.lean"
        for proof in ("by sorry", "by admit", "by native_decide"):
            with self.subTest(proof=proof):
                self.write(
                    path,
                    "namespace Komorebi.GuardControls\n"
                    f"theorem unchecked : True := {proof}\n"
                    "end Komorebi.GuardControls\n",
                )
                with self.assertRaises(ValueError):
                    explicit_declarations(self.root, path)

    def test_positive_control_can_discuss_rejected_forms_in_comments_and_strings(self):
        path = "Controls/Explanation.lean"
        self.write(
            path,
            "/- These are rejected: private axiom, sorry.\n"
            "   /- nested comment: opaque, native_decide -/ still a comment. -/\n"
            "namespace Komorebi.GuardControls\n"
            'def explanation : String := "axiom sorry native_decide"\n'
            "-- private theorem is mentioned only in this comment.\n"
            "theorem checked : True := True.intro\n"
            "end Komorebi.GuardControls\n",
        )
        names = {row["name"] for row in explicit_declarations(self.root, path)}
        self.assertEqual(
            names,
            {"Komorebi.GuardControls.explanation", "Komorebi.GuardControls.checked"},
        )

    def test_library_root_cannot_hide_an_unlisted_declaration(self):
        self.write(
            "GuardFixture.lean",
            "import GuardFixture.Main\n"
            "axiom hidden_root_axiom : False\n",
        )
        with self.assertRaises(ValueError):
            source_inventory(self.root, self.config)

    def test_library_root_must_import_each_selected_module_once_and_only_once(self):
        for imports in (
            "",
            "import GuardFixture.Main\nimport GuardFixture.Unselected\n",
            "import GuardFixture.Main\nimport GuardFixture.Main\n",
        ):
            with self.subTest(imports=imports):
                self.write("GuardFixture.lean", imports)
                with self.assertRaises(ValueError):
                    source_inventory(self.root, self.config)

    def test_source_inventory_rejects_missing_extra_and_mislabelled_names(self):
        cases = []
        missing = copy.deepcopy(self.config)
        missing["declarations"] = []
        cases.append(missing)
        extra = copy.deepcopy(self.config)
        extra["declarations"].append(
            {"name": "Komorebi.GuardFixture.unwritten", "kind": "theorem", "source": self.path}
        )
        cases.append(extra)
        wrong_kind = copy.deepcopy(self.config)
        wrong_kind["declarations"][0]["kind"] = "def"
        cases.append(wrong_kind)
        wrong_source = copy.deepcopy(self.config)
        wrong_source["declarations"][0]["source"] = "GuardFixture/Elsewhere.lean"
        cases.append(wrong_source)
        for config in cases:
            with self.subTest(declarations=config["declarations"]):
                with self.assertRaises(ValueError):
                    source_inventory(self.root, config)

    def test_duplicate_inventory_cannot_inflate_an_audited_count(self):
        self.config["declarations"].append(copy.deepcopy(self.config["declarations"][0]))
        with self.assertRaises(ValueError):
            inventory_names(self.config)


class LeanCompanionRejectionGuardTests(unittest.TestCase):
    false_diagnostic = (
        "Controls/Reject.lean:6:57: error: Tactic `decide` proved that the proposition\n"
        "  (project 2 0) (fun x => 1) 1 = 1\n"
        "is false\n"
    )

    def accepts(self, text):
        return diagnostics_match(
            text,
            required="is false",
            forbidden=FORBIDDEN_DIAGNOSTICS,
            expected_errors=1,
        )

    def test_single_intended_false_proposition_is_a_valid_rejection(self):
        self.assertTrue(self.accepts(self.false_diagnostic))

    def test_expected_rejection_plus_missing_constant_is_not_valid_evidence(self):
        mixed = self.false_diagnostic + (
            "Controls/Reject.lean:7:7: error(lean.unknownIdentifier): "
            "Unknown constant `Nat.noSuchConstantForAudit`\n"
        )
        self.assertFalse(self.accepts(mixed))

    def test_second_plain_error_is_not_valid_evidence(self):
        mixed = self.false_diagnostic + "Controls/Reject.lean:7:5: error: unrelated error\n"
        self.assertFalse(self.accepts(mixed))

    def test_second_categorized_error_is_also_not_valid_evidence(self):
        mixed = self.false_diagnostic + (
            "Controls/Reject.lean:7:5: error(lean.invalidField): "
            "Invalid field `unexpectedField`\n"
        )
        self.assertFalse(self.accepts(mixed))

    def test_unlocated_failure_text_does_not_count_as_a_rejected_theorem(self):
        self.assertFalse(self.accepts("a proposition is false\n"))


class LeanCompanionAxiomOutputTests(unittest.TestCase):
    def test_mixed_axiom_output_keeps_empty_standard_and_untrusted_dependencies(self):
        output = (
            "'Reader.general' depends on axioms: [propext,\n Classical.choice,\n Quot.sound]\n"
            "'Controls.exact' does not depend on any axioms\n"
            "'Controls.untrusted' depends on axioms: [Untrusted.bad]\n"
        )
        rows = parse_axioms(output)
        self.assertEqual(len(rows), 3)
        self.assertEqual(
            {row["name"]: row["axioms"] for row in rows},
            {
                "Reader.general": ["propext", "Classical.choice", "Quot.sound"],
                "Controls.exact": [],
                "Controls.untrusted": ["Untrusted.bad"],
            },
        )


if __name__ == "__main__":
    unittest.main()
