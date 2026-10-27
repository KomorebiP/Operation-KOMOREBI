#!/usr/bin/env python3
"""Append Continuation VI without modifying the recovered v5 reading record."""
from pathlib import Path
import hashlib
import json
import build_running_document_v5 as builder

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'manuscript'


def cover(appendix: bool) -> str:
    title = 'Terminal Carries and Root Classification' if appendix else 'A Running Research Record'
    description = (
        'Version-6 continuation. Arbitrary-depth carry geometry, uniform odd-multiplier certificates, '
        'and an exact dyadic valuation classification through residual degree 64.'
        if appendix else
        'The complete version-5 reading record, including the recovered earlier proof notes, '
        'with version 6 appended. Exact dyadic tail valuations and the role of binary carries and unit coefficients.'
    )
    result = r'''\hypersetup{pageanchor=false}
\begin{titlepage}
\thispagestyle{empty}
\vspace*{0.65in}
{\sffamily\large OPERATION KOMOREBI\par}
\vspace{0.55in}
{\sffamily\fontsize{31}{36}\selectfont\bfseries Dyadic Euler Tails\par}
\vspace{0.20in}
{\sffamily\fontsize{20}{25}\selectfont ''' + title + r'''\par}
\vspace{0.38in}
{\large ''' + description + r'''\par}
\vspace{0.45in}
\[
\mathcal T_{r-1}(N)=\kappa_r\binom{2N}{2r}\,2^{\mu_r}G_r(N-r)
\]
\[
r=b2^L-j,\qquad b\text{ odd},\qquad j=\deg W_r
\]
\vfill
{\large Komorebi P.\par}
\vspace{0.14in}
{\sffamily Version 6 \textbar\ 26 September 2026\par}
\vspace{0.35in}
\begin{minipage}{0.94\textwidth}
\small
Working research manuscript. Mathematical proofs, whole-ball coefficient certificates and sampled checks are distinguished. No Lean verification or historical-priority assessment is claimed. The larger irregular terminal labels remain outside the completed classification.
\end{minipage}
\end{titlepage}
\pagenumbering{roman}
\hypersetup{pageanchor=true}
\tableofcontents
\clearpage
\pagenumbering{arabic}
'''

    if appendix:
        result = result.replace(r'\tableofcontents', r'\setcounter{tocdepth}{2}'+'\n'+r'\tableofcontents')
    return result


def main() -> None:
    old = DOC / 'Dyadic_Euler_Tails_Running_v5.md'
    previous = old.read_text(encoding='utf-8')
    front = (DOC/'FRONT_MATTER_V6.md').read_text(encoding='utf-8')
    continuation = (DOC/'CONTINUATION_06.md').read_text(encoding='utf-8')
    history_notice = (
        '\\clearpage\n\n# Preserved version-5 reading record\n\n'
        '> **Version boundary.** The complete prior reading record follows. Its "current" '
        'status statements refer to version 5. The current version-6 scope is stated in the '
        'preceding map and proved in the appended Continuation VI.\n\n'
    )
    running = front + '\n\n' + history_notice + previous + '\n\n\\clearpage\n\n' + continuation
    builder.PREAMBLE = builder.PREAMBLE.replace('Research record \\textbar\\ v5',
                                               'Research record \\textbar\\ v6')
    builder.PREAMBLE = builder.PREAMBLE.replace(r'\usepackage{amsmath,amssymb,mathtools}',r'\usepackage{amsmath,amssymb,mathtools,needspace}')
    builder.cover = cover
    builder.build(running, 'Dyadic_Euler_Tails_Running_v6')
    builder.build(continuation, 'Dyadic_Euler_Tails_Appendix_v6', True)
    assert previous in (DOC/'Dyadic_Euler_Tails_Running_v6.md').read_text(encoding='utf-8')
    metadata = {
        'method': 'Pandoc and XeLaTeX; v5 source preserved as a complete substring',
        'historical_source': str(old.relative_to(ROOT)),
        'historical_source_sha256': hashlib.sha256(old.read_bytes()).hexdigest(),
        'continuation_source': 'manuscript/CONTINUATION_06.md',
        'no_font_files_distributed': True,
        'source_history_preserved': True,
    }
    (ROOT/'sources/DOCUMENT_BUILD_V6.json').write_text(json.dumps(metadata,indent=2)+'\n')

if __name__ == '__main__':
    main()
