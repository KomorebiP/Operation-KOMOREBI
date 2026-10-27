"""Execute the Python example printed in Chapter 11, using the manuscript itself."""
from __future__ import annotations

import ast
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    source = ROOT / 'manuscript' / 'chapters' / '11_atlas.tex'
    try:
        blocks = re.findall(
            r'\\begin\{lstlisting\}(?:\[[^\]]*\])?\s*\n(.*?)\\end\{lstlisting\}',
            source.read_text(encoding='utf-8'), re.DOTALL,
        )
        selected = [block for block in blocks if 'from fractions import Fraction' in block]
        if len(selected) != 1:
            raise ValueError(f'Expected one arithmetic example, found {len(selected)}.')
        code = selected[0]
        tree = ast.parse(code, filename=str(source))
        assertion_count = sum(isinstance(node, ast.Assert) for node in ast.walk(tree))
        sys.path.insert(0, str(ROOT))
        exec(compile(tree, str(source), 'exec'), {'__name__': '__main__'})
    except (OSError, ValueError, SyntaxError, AssertionError, ImportError) as exc:
        print(f'FAIL: printed example replay: {exc}', file=sys.stderr)
        return 1
    print(f'PASS: Chapter 11 example extracted and executed ({assertion_count} assertions).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
