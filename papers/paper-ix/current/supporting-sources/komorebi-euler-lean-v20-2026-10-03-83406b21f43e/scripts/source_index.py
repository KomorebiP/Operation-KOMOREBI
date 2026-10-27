#!/usr/bin/env python3
"""Generate an exact declaration index and axiom-audit input from the Lean sources."""
from __future__ import annotations
import json
import re
from pathlib import Path

MODULES = ["Dyadic", "CollisionSeries", "RefinementBudget", "CriticalCharts",
           "DiscriminantReduction", "ResidueCertificates", "HenselLifting",
           "NegativeControls", "RestrictedEvaluation", "RestrictedCalculus",
           "RestrictedHensel", "RestrictedJets", "CollisionAnalytic", "RestrictedExamples",
           "SourceScalars", "SourceNewton", "EulerSource", "SourceRows", "SourceCertificates", "EulerKernel", "EulerPackets", "ReconstructionTail", "EulerFormalKernel", "EulerFormalSource", "EulerIdentification",
           "EulerSequence", "EulerIntegrality", "EulerError",
           "ResidualScalars", "WeightedTranslation", "SourceTranslation", "ResidualSeries", "ResidualEvaluation", "ResidualRows", "ResidualTruncation", "ResidualRecurrence", "ResidualCarry", "ResidualMinimum", "ResidualNormalization", "ResidualReduction", "ResidualError", "ResidualSimpleCases", "RestrictedHigherDerivatives", "ResidualPacketJets", "PacketDerivatives", "PacketDerivativeBounds", "PacketIntegerSlopes", "ResidualSlopeTransport", "ResidualSlopeExamples", 'BinaryWallArithmetic', 'TerminalCoordinates', 'TerminalWallMinimum', 'TerminalShift', 'TerminalLowerSeries', 'TerminalNormalForm', 'TerminalResidues', 'TerminalSlope', 'TerminalConsequences', 'RestrictedAffine', 'SkeletonArithmetic', 'SkeletonLocalPolynomial', 'LocalAnalyticTools', 'SkeletonLocalSeries', 'SkeletonLocalEvaluation', 'LocalRootTransport', 'SkeletonPartition', 'EulerLocalAtlas', 'EulerPointwiseAtlas', 'EulerLocalRows', 'EulerSkeletonExamples']

def without_comments(text: str) -> str:
    # Preserve newlines/positions; Lean block comments can be nested.
    out = list(text)
    i, depth = 0, 0
    while i < len(text):
        if text.startswith('/-', i):
            out[i:i+2] = '  '
            depth += 1
            i += 2
        elif depth and text.startswith('-/', i):
            out[i:i+2] = '  '
            depth -= 1
            i += 2
        elif depth:
            if text[i] != '\n': out[i] = ' '
            i += 1
        elif text.startswith('--', i):
            while i < len(text) and text[i] != '\n':
                out[i] = ' '
                i += 1
        else:
            i += 1
    if depth:
        raise ValueError('Unclosed Lean block comment')
    return ''.join(out)

def generate(root: Path) -> list[dict[str, object]]:
    index = []
    for mod in MODULES:
        path = root / 'Euler' / f'{mod}.lean'
        text = without_comments(path.read_text())
        # These project files have no declaration-like strings or nested namespaces.
        for match in re.finditer(r'\b(theorem|lemma)\s+([\w\u2080-\u2089]+)', text):
            index.append({'name': 'Komorebi.Euler.' + match[2], 'kind': match[1],
                          'source': f'Euler/{mod}.lean',
                          'line': text[:match.start()].count('\n') + 1})
    names = [str(row['name']) for row in index]
    if len(set(names)) != len(names):
        raise ValueError('Duplicate declaration names')
    (root / 'THEOREM_INDEX.json').write_text(json.dumps(index, indent=2) + '\n')
    (root / 'Audit.lean').write_text(
        'module\npublic import Euler\n@[expose] public section\n' +
        ''.join(f'#print axioms {name}\n' for name in names))
    return index

if __name__ == '__main__':
    rows = generate(Path(__file__).resolve().parents[1])
    print(f'Indexed {len(rows)} theorem/lemma declarations.')
