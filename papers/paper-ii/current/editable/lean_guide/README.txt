Paper II Lean and evidence guide, 19 October 2026

CURRENT GUIDE
Compile the included current TeX, generated current overview, preserved
walkthrough, and exact source excerpts from this directory:
  python3 build.py

For a coordinated three-edition build with current page references, run from
the package root:
  python3 publication/build_current.py

CURRENT FORMAL DEVELOPMENT
The active Lean sources are formal/current/ at the package root. The current
source/evidence correspondence is:
  formal/coverage/Paper_II_Current_Correspondence_2026-10-19.json
Its exact recorded statuses and release gates appear at the start of the guide.
The publication generator does not grant compiler or semantic acceptance.
Use the current formal replay instructions and exact source-bound receipts.

HISTORICAL WALKTHROUGH
The historical walkthrough chapters and original generated/theorem_map.json explain the
preserved canonical v1.2.1 / Lean v1.1.1 component. Its 25 rows, 160 unique
targets, 171 target occurrences, 15 Lean files, and September 3 report belong to
that snapshot. They are not counts of the current enlarged project.

The historical generator remains available:
  python3 build_guide_data.py
It reads the preserved source/canonical_v1.2.1 component and regenerates its
historical excerpts and maps. It does not replace the current scope generator:
  python3 publication/sync_current_scope.py
Run the latter from the package root after refreshing the correspondence.
Current navigation is refreshed by publication/sync_navigation.py against the
actual built traditional PDF and AUX. Historical navigation metadata remains
preserved; generated/current_traditional_crosswalk.tex is the live table.

All document builders require XeLaTeX and the packaged fonts. PDF compilation
alone invokes no Lean compiler. Static lexical name lookup, kernel replay,
semantic scope review, and page QA are separate evidence records.
