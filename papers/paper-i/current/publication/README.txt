Paper I current publication — release edition, 15 October 2026

The traditional manuscript, Lean guide and machine-native companion are the
three current release documents. Their identical PDF copies are maintained in
papers/ and publication/pdfs/.
The same-named PDF outputs in editable/ are synchronized to these copies.

Build all three:
  python3 scripts/build_pdfs.py

For an isolated reproduction that leaves the distributed PDFs untouched:
  python3 scripts/build_pdfs.py --check-only

Select one with --component traditional, --component lean_guide, or
--component machine. The publication/build_publication.py command delegates
to the same build so both public PDF directories stay synchronized.

The current manuscript includes its own monograph style and bundled fonts.
The current companions retain the series house style. Historical sources,
figures and evidence remain versioned separately under source/.

Current record destinations are in CURRENT_PUBLICATION_LOCATORS.json and
COMPANION_CROSSWALK.json. They are generated after final PDF validation.
CURRENT_PUBLICATION_MANIFEST.json records the current PDF identities and
verification scope. The dated migration.json remains the historical 8 October
presentation-migration record; it does not report the current formal checks.
