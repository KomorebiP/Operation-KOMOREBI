# Development failures and corrections

## Mathematical overclaims corrected

1. A residual kernel is an invariant Boolean subalgebra, not generally an ideal.
   The residual quotient is additive, not a Boolean-algebra quotient.
2. Invariant observables map to definable coherent sections, not necessarily
   all sections. A further ideal quotients away evaluation-identical observables.
3. A canonical Boolean projector is not available in general. The two-world
   symmetry obstruction is proved. A finite-cofinite example also rules out
   existence of a Boolean retraction in general.
4. Ordinary scalar truth defects have zero graph cohomology class by construction.
   Proposed edge data can be nonintegrable. Rich transport can have holonomy.
   These are distinct claims.
5. Eventual constancy on one path is not robust modal stabilization.
6. A common Boolean presentation alone does not establish a shared forcing ground
   or an explanatory generative structure.
7. A diagram limit is not by itself a sheaf. Universal forcing amalgamation is not
   an admissible default hypothesis.

## Lean environment failure

No Lean or Lake executable was found in the inspected runtime locations.
A download of the pinned Lean 4.19.0 Linux archive using curl failed twice with:

    curl: (6) Could not resolve host: github.com

The external download tool required a successfully viewed asset URL. The web
asset fetch was restricted, so that alternate route did not supply the archive.
No Lean compilation was run. The included source is labeled UNCOMPILED.

## PDF build failures, subsequently repaired

The first LaTeX build failed because `newtxmath` defined `openbox` before `amsthm`
was loaded. Moving the AMS packages before the math font package fixed it.

The next build exposed a malformed macro inserted by a shell edit. A backslash-n
was interpreted as a newline, leaving `ewcommand` in the preamble. The macro
was repaired directly. The subsequent LaTeX build succeeded.

Final pagination, references, and visual inspection are recorded in the PDF
quality-assurance output. These build corrections do not change mathematical claims.
