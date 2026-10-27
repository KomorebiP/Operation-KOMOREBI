#!/usr/bin/env python3
"""Regression check for distinct Lean identifiers ending in apostrophes."""
from pathlib import Path
from tempfile import TemporaryDirectory
import source_audit

def main():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        source_audit.ROOT = root
        path = root / 'ParserRegression.lean'
        path.write_text("namespace Komorebi.ParserRegression\n"
                        "theorem name : True := by trivial\n"
                        "theorem name' : True := by trivial\n"
                        "def name'' : Nat := 0\n"
                        "end Komorebi.ParserRegression\n")
        entries = source_audit.inspect_source(path)['declarations']
        expected = {'Komorebi.ParserRegression.name', 'Komorebi.ParserRegression.name\'',
                    'Komorebi.ParserRegression.name\'\''}
        assert {e['name'] for e in entries} == expected
        log = "'Komorebi.ParserRegression.name' does not depend on any axioms\n" \
              "'Komorebi.ParserRegression.name\'' depends on axioms: [propext,\nClassical.choice]\n" \
              "'Komorebi.ParserRegression.name\'\'' depends on axioms: [Quot.sound]\n"
        parsed = source_audit.parse_audits(log, expected)
        assert parsed["Komorebi.ParserRegression.name'"] == ['Classical.choice', 'propext']
        for invalid in (log + log, log.replace("name''", "wrong"),
                        log.replace('Quot.sound', 'sorryAx')):
            try:
                source_audit.parse_audits(invalid, expected)
            except ValueError:
                pass
            else:
                raise AssertionError('Parser accepted a duplicated, mismatched, or forbidden-axiom report')
    print('PASS: declaration and axiom parsers retain apostrophes; reject duplicates, mismatches, forbidden axioms')

if __name__ == '__main__':
    main()
