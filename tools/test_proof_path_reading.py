"""Source-fidelity and parser regressions for the Proof Path Theory reader."""
import unittest
from pathlib import Path

from proof_path_reading import (BOOK, CHAPTERS, MAIN, WORK, normalize, source_specs)
from readable_chapters import (Chapter, chapter_text, manuscript_macros,
                               original_math)


ROOT = Path(__file__).resolve().parents[1]


class ProofPathReadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = (ROOT / MAIN).read_text(encoding="utf-8-sig")
        cls.macros = manuscript_macros(cls.main, BOOK["required_macros"])

    def test_all_sections_follow_retained_source(self):
        self.assertEqual(source_specs(lambda path: self.main), CHAPTERS)
        self.assertEqual(len(CHAPTERS), 40)
        self.assertEqual(sum(c["kind"] == "part" for c in CHAPTERS), 5)
        self.assertEqual(CHAPTERS[0]["title"], "Preface")
        self.assertEqual(CHAPTERS[-1]["title"], "A complete minimal proof-field record")
        self.assertEqual(len({c["url"] for c in CHAPTERS}), len(CHAPTERS))
        self.assertEqual(CHAPTERS[0]["start_line"], 187)

    def test_math_and_line_numbers_preserved_everywhere(self):
        state = {"number_floats": True}
        expressions = []
        nodes = []
        for spec in CHAPTERS:
            raw = chapter_text(self.main, spec)
            formatted = normalize(raw)
            self.assertEqual(formatted.count("\n"), raw.count("\n"), spec["title"])
            self.assertEqual(original_math(formatted), original_math(raw), spec["title"])
            chapter = Chapter(formatted, self.macros, state=state, check_refs=False)
            nodes.extend(chapter.nodes)
            expressions.extend(original_math(raw))
            state = {key: getattr(chapter, key)
                     for key in ("section", "appendix", "part", "subsection",
                                 "subsubsection", "counter", "section_prefix",
                                 "figure", "table", "number_floats")}
        self.assertGreater(len(expressions), 100)
        self.assertGreater(sum(n["kind"] == "proof" for n in nodes), 45)
        self.assertGreater(sum(n["kind"] == "figure" for n in nodes), 15)
        self.assertGreater(sum(n["kind"] == "lstlisting" for n in nodes), 8)
        self.assertGreater(sum(n["kind"] == "longtable" for n in nodes), 2)
        self.assertGreater(len(nodes), 150)

    def test_all_part_illustrations_have_receipted_png_source(self):
        for file in BOOK["part_figures"].values():
            self.assertTrue((ROOT / "monographs/proof-path-theory/docs/figures" / file).is_file(), file)

    def test_print_wrappers_removed_without_changing_prose(self):
        spec = next(c for c in CHAPTERS if c["kind"] == "part")
        text = normalize(chapter_text(self.main, spec))
        self.assertIn(r"\part{Proof fields and certificates}", text)
        self.assertNotIn(r"\monographpart", text)
        trace = next(c for c in CHAPTERS if c["title"] == "A checked realization bridge for proof fields")
        converted = normalize(chapter_text(self.main, trace))
        self.assertIn("Visual study 01", converted)
        self.assertIn("The bridge is a restriction map", converted)
        self.assertIn(r"\begin{readerroadmap}", converted)


if __name__ == "__main__":
    unittest.main()
