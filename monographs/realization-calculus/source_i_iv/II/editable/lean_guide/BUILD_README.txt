Paper II Lean guide build
Author: Komorebi P.

Compile the authored guide from this directory:
    python3 build.py
To put the rebuilt PDF and auxiliary files elsewhere:
    python3 build.py --output-directory /path/to/build

Requirements: Python 3.9 or newer, XeLaTeX, and the TeX packages named in the
master and house style. Current sources, fonts, and excerpts are packaged
locally. This compile-only command does not regenerate guide data, restore
historical prose, access the network, or run Lean. Four XeLaTeX passes resolve
the contents and cross-references from a clean directory. Pass transcripts and
the final TeX log are written beside the rebuilt PDF. The deterministic
timestamp comes from publication/PUBLICATION_BUILD_CONFIG.json. The
--edition-date option selects another ISO date explicitly.

The historical editorial verification below belongs to the original guide.
Current monograph changes and validation are recorded separately in the full
package release reports. Historical font choices do not describe the current
bundled monograph style.

Paper II Lean Guide build and editorial verification

Scope: guide-only authoring; preserved canonical Lean and canonical report
were read, hashed, and excerpted without changes. No other paper was edited.

Draft corrections retained for transparency:
1. Initial complete-content XeLaTeX attempt stopped at an unsupported
   \llbracket macro in the zeta chapter. Replaced that display notation by
   supported paired brackets. The failed output is qa/build_pass1.txt.
2. Source excerpt boundaries were tightened after source-line inspection.
   The data generator was then rerun, so final excerpts.json and exact/display
   files agree with the final selections in build_guide_data.py.
3. Independent narrow review of the transfer and arithmetic chapters caught
   an incorrect illustrative sign-matrix display attributed to the formal
   constants. Replaced it with the exact canonical involution [[1,1],[0,-1]]
   and projectors [[1,1/2],[0,0]], [[0,-1/2],[0,1]]. The original Lean was
   unchanged. No conjugacy or added formal claim was introduced.
4. A map heading containing a code macro caused PDF-bookmark warnings.
   Plain text was used for the heading; code formatting remains in the body.
5. Earlier compiler passes had expected unresolved forward references.
   Subsequent full passes regenerated the table of contents and references.

Final mathematical proofreading scope: the newly authored guide prose,
displays, TeX structure, exact excerpt boundaries, and map/crosswalk framing.
Routine corrections: supported display delimiters, source-line endpoints,
bookmark formatting, cross-reference reruns.
Mathematical-token correction: the guide's rational sign matrices were
corrected to the exact canonical formal constants, as item 3 records.
No preserved formal-source mathematical tokens were changed.
Unresolved mathematical claims: none asserted beyond the guide's explicitly
scoped exposition; the inherited verification lacks raw execution logs and
is described as inherited report evidence throughout.

Validation: generated static audit, complete XeLaTeX build, every-page render,
contact-sheet review, and selected code/equation detail review. Final counts,
PDF digest, and diagnostics are recorded in qa/pdf_verification.json.

6. Visual detail review identified collapsed spaces in inline code commands
   and a missing standalone capital A in Nimbus Sans bold headings. Enabled
   URL-space preservation for inline code and used DejaVu Sans for the
   heading family. Exact Lean source text was unchanged.

   Liberation Sans was first attempted but is unavailable in this runtime;
   the failed font lookup log is qa/font_attempt_failed.txt. The final font
   family is DejaVu Sans, with P052 serif body text unchanged.

7. The portable compile-only builder performs four XeLaTeX passes so a clean
   build with no auxiliary files converges after its three-page contents.
