#!/usr/bin/env python3
"""Build the reader guide from the accepted continuation summary and proof supplement."""
import json
import re
import subprocess
from pathlib import Path

PUB = Path(__file__).resolve().parent
CONT = PUB.parent

def main():
    stats = json.loads((CONT / 'VERIFICATION_SUMMARY.json').read_text())
    if stats['status'] != 'PASS':
        raise SystemExit('Refusing to publish a completed guide without accepted verification')
    # Publication-only markup copy; the audited source proof stays immutable.
    proof = (PUB / 'Projection_Excerpt.md').read_text()
    intro = f'''# What this continuation closes

**WR01 and WR02 now have compiled formal counterparts under their published real Hilbert-space hypotheses.** The new development also connects bounded approximation to the actual protected correction kernel. An independent review compared the public Lean theorem types with every clause of the two printed groups.

This package continues the proof-expanded v1.7.0 monograph. The inherited 161-page monograph, 43-page visual guide, and 36-page evidence guide are retained as historical reader documents. This guide supplies the updated formal status. It is a formal continuation, not a claim that those three older PDFs were re-typeset.

| Result | Formal scope now established |
|:---|:---|
| WR01 | A bounded approximating sequence gives an exact preimage within the same norm budget. The range equivalence and divergence to infinity for unattained data are included. |
| WR02 | Minimum-norm points of arbitrary nested nonempty closed affine sets converge strongly exactly when their norms stay bounded. Finite and limiting energy identities, uniqueness, and divergence are included. |
| Protected realization | An exact repaired candidate preserves the declared observable and stays within the original correction budget. |
| Convex auxiliary result | Nested closed convex minimum points satisfy the energy inequality and the bounded-intersection criterion. The affine case retains the stronger equality. |

# Evidence and its scope

The predecessor ZIP and all 2,270 payload hashes were checked before editing. All 169 inherited files across its two formal source trees remain unchanged. The accepted old evidence is preserved rather than overwritten.

| Check | Accepted result |
|:---|:---|
| Clean combined baseline | {stats['base_compile_targets']} source targets, joining the canonical core and regularization extension. |
| New production sources | {stats['new_production_modules']} new modules compiled from source. |
| Final imported declaration audit | {stats['audited_declarations']:,} declarations, including generated declarations. |
| Axiom dependencies | Only `propext`, `Classical.choice`, and `Quot.sound`. |
| Controls | {stats['positive_files']} positive files, {stats['compiler_negative_files']} compiler rejection files, and {stats['policy_negative_files']} axiom-policy rejection files. |

The final integration reuses only source-bound, hash-checked project objects from the newly accepted clean combined baseline. It compiles the additions and final entrypoint, exports a fresh audit of the entire final imported scope, and reruns the controls. This is an incremental extension of a fresh clean baseline. It is not described as a second empty-directory rebuild of every final source.

The official Lean compiler and kernel, standard axioms, and pinned compiled dependency caches remain trusted. Mathlib was not rebuilt from source. Compilation and axiom checks do not automatically verify prose translations or the Python implementations. No numerical suite was rerun merely to increase a test count.

# How the arguments fit together

The WR01 Lean proof uses compactness of a dual norm ball, Riesz representation, and continuous evaluation against the adjoint. It retains the exact budget and makes no separability or closed-range assumption. It does not separately formalize the monograph's printed weak-subsequence construction.

The WR02 proof constructs minimum points on the actual closed convex sets. A projection inequality bounds distance by the change in squared norms. Bounded energy then makes the sequence Cauchy. Completeness supplies a strong limit, and closedness places that limit in every constraint set. Affineness upgrades the inequality to the exact Pythagorean identity.

The next sections give an alternative written route that uses this same projection mechanism for WR01–WR03. That route passed independent mathematical review. **WR03 remains written-only:** a reviewed alternate proof is not a new compiled counterpart for its complete budget-profile statement.

# What remains

The WR catalogue now has **six complete groups, two partial groups, and eight written-only groups**. The complete groups are WR01, WR02, WR06, WR07, WR13, and WR14. WR09 and WR16 retain their pointwise formal inequalities and still require the limiting conclusions. The written-only groups are WR03–WR05, WR08, WR10–WR12, and WR15.

The next formal block is WR03–WR05: fixed-budget attainment and profile geometry, sharp dual certificates, and robustness under model and data uncertainty. WR08 then supports the remaining regularization limits. Full proof-to-source review of the rest of the book and synchronized publication remain separate obligations.

Development failures were retained. They included missing typeclass information, elaboration and simplification mismatches, strict-linter failures in proof fixtures, and an incomplete local import list during bridge testing. They were corrected before the accepted runs. The first direct compiler launch also needed the offline runtime's documented executable-path adapter. Exact failed and accepted logs are included in the package.

The first guide build failed because the LuaLaTeX font loader was unavailable. XeLaTeX provided the working font backend. A second build found an equation tag inside an alignment block. Moving the tag to the outer display corrected that typesetting error without changing the equation. Font substitutions were resolved before the final page review.

# A common projection proof for bounded realization

The following derivation preserves the existing WR01–WR03 claims and uses the projection theorem proved in the monograph's analytic appendix. Elementary norm identities, real suprema and infima, and completeness are the remaining background. The general convex inequality is kept distinct from the affine equality.

'''
    # AMS tags belong to the outer display, not inside an aligned subenvironment.
    def display_layout(match):
        block = match.group(1)
        if r'\begin{aligned}' in block:
            tags = re.findall(r'\\tag\{[^}]+\}', block)
            block = re.sub(r'\\tag\{[^}]+\}', '', block)
            block += ''.join(tags)
        return '\\[' + block + '\\]'
    proof = re.sub(r'\\\[(.*?)\\\]', display_layout, proof, flags=re.S)
    proof = proof.replace(r'\exists (u_j)_{j\in\mathbb N}\subseteq H,\quad',
                          r'\exists (u_j)_{j\in\mathbb N}\subseteq H,\\'+'\n'+r'&\qquad')
    proof = re.sub(r'(?m)^(Consequently|so|and)$', r'\1\n\n\\nopagebreak[4]', proof)
    proof = proof.replace('## Boundary cases and scope checks',
                          '\\newpage\n\n## Boundary cases and scope checks')
    md = intro + proof
    (PUB / 'Continuation_Guide.md').write_text(md)
    template = r'''\documentclass[11pt]{article}
\usepackage{geometry,fontspec}
\usepackage{amsmath,amssymb,amsthm,booktabs,longtable,array,calc}
\usepackage{xcolor,hyperref,bookmark,fancyhdr,microtype}
\usepackage{komorebi-publication}
\renewcommand{\KomorebiTitle}{Komorebi Space}
\renewcommand{\KomorebiSubtitle}{Bounded realization and minimum corrections}
\renewcommand{\KomorebiSeries}{Foundations of the Realization Calculus}
\renewcommand{\KomorebiKind}{Formal continuation}
\renewcommand{\KomorebiEdition}{Formal continuation 1.8.0}
\renewcommand{\KomorebiShortTitle}{Komorebi Space}
\KomorebiSetup
\setmainfont{DejaVuSerif.ttf}[Path=/usr/share/fonts/truetype/dejavu/,BoldFont=DejaVuSerif-Bold.ttf,ItalicFont=DejaVuSerif.ttf,ItalicFeatures={FakeSlant=0.18},BoldItalicFont=DejaVuSerif-Bold.ttf,BoldItalicFeatures={FakeSlant=0.18}]
\setsansfont{NimbusSans-Regular.otf}[Path=/usr/share/fonts/opentype/urw-base35/,BoldFont=NimbusSans-Bold.otf,ItalicFont=NimbusSans-Italic.otf,BoldItalicFont=NimbusSans-BoldItalic.otf,Scale=.94]
\definecolor{pine}{HTML}{204F43}
\hypersetup{colorlinks=true,linkcolor=pine,urlcolor=pine,pdftitle={Komorebi Space: Formal Continuation v1.8.0}}
\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}
\setlength{\emergencystretch}{2em}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\begin{document}
\KomorebiCover
$body$
\end{document}
'''
    (PUB / 'guide_template.tex').write_text(template)
    subprocess.run(['pandoc',str(PUB/'Continuation_Guide.md'),'--from=markdown+tex_math_single_backslash','--to=latex','--standalone','--template',str(PUB/'guide_template.tex'),'-o',str(PUB/'Continuation_Guide.tex')],check=True)
    for _ in range(2):
        subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','Continuation_Guide.tex'],cwd=PUB,check=True,stdout=subprocess.DEVNULL)
    print(PUB/'Continuation_Guide.pdf')

if __name__ == '__main__':
    main()
