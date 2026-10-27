PAPER IV — MONOGRAPH PUBLICATION
This folder contains synchronized copies of the three current Paper IV PDFs.
The authoritative authored source trees are under editable/.

From this directory:
  python3 build_publication.py --check-only --report /tmp/paper-iv-build.json
The wrapper delegates to ../scripts/build_pdfs.py and uses the three portable
isolated XeLaTeX builders. No Lean or mathematical checks are invoked.
Current document identities are in CURRENT_PUBLICATION_MANIFEST.json. Complete
file hashes live in ../MANIFEST_SHA256.json. Earlier series-wide publication
notes and migration records are retained as dated historical metadata under
../provenance/pre_monograph_metadata/. They are not current Paper IV claims.
