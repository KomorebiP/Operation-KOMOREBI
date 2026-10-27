Paper IX — Visual Guide — Komorebi P.

Separate companion: 34 worked pages, 32 deterministic editable TikZ plates.
All 30 original worked pages and all 28 original vector plates are retained.
Four additional pages teach transported selectors, companion jumps, equation
presentations, and a compatible completed-root construction.

Build:
  python build.py --output-dir /absolute/path/to/new/output

Dependencies: Python 3 standard library, an installed pdflatex with the TeX
packages listed in appendix.tex, and PyMuPDF for PDF geometry checks. No
installation, network request, SymPy import, or Lean invocation is performed.
The build uses SOURCE_DATE_EPOCH=1791244800 and FORCE_SOURCE_DATE=1 and works
in an isolated temporary directory. It regenerates all plates, requires byte
identity with delivered graphics, executes the current exact checker, typesets
twice, and checks the PDF's 34 page bookmarks, safe geometry and absence of
raster image objects.

Fresh checks:
  python checks/verify_examples_exact.py

The fresh standard-library replacement checker records 241 named assertions,
31,353 declared case evaluations and 22 false controls rejected. Complete
input windows are used for direct Hurwitz prime-shift identities. Integer and
Fraction arithmetic also verify two Euler coefficient constructions, Newton
stencils, independent Bernoulli coefficients and polynomial multiplication,
modular root digits, explicit rational matrix products, finite permutations,
CRT compatibility and all displayed added examples. The computation manifest
pins exact input and result bytes and reports bounds. Finite successes do not
supply universal theorems, convergence, analytic regularity, external statement
correspondence, or a new Lean kernel acceptance.

Inherited evidence is stored under inherited/. The original SymPy checker
and its 214-assertion report (30,987 declared case evaluations, 19 controls)
were preserved but not executed. The fresh replacement is a different run
and has its own code and provenance; it is not reported as the historical run.

Navigation:
  source/crosswalk_targets.json declares each worked page's manuscript labels.
  source/traditional_targets.tex holds final numbered traditional PDF locators.
  QA/FINAL_PAGE_CROSSWALK.json records the final traditional PDF hash, each label,
  its physical page and the exact relative PDF page action.

If a new traditional build changes pagination, regenerate the crosswalk only
from its actual .aux and PDF using:
  python update_crosswalk.py --aux /path/to/final.aux --pdf /path/to/final.pdf
Then rebuild this guide. This is an editorial operation, not a Lean proof.

Geometry of the diagrams is schematic. Rational labels are exact; ordinary
page distances are not p-adic distances. The original 28-page manuscript's
full TeX, its figure generator and its full historical experiment package are
not reconstructed by this guide. The consolidated and Annals branches remain
separate preserved sources in the full edition package.
