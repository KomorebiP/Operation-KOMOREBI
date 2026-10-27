PAPER V — MONOGRAPH PUBLICATION
Synchronized copies of the three current PDFs are under pdfs/. Authored
portable source trees are under ../editable/.

  python3 build_publication.py --check-only --report /tmp/paper-v-build.json
The wrapper delegates to ../scripts/build_pdfs.py. It compiles the complete
three trees in isolated directories with externally installed fonts and compares pages
and text. No mathematical or Lean execution is invoked by PDF compilation.

Current identities: CURRENT_PUBLICATION_MANIFEST.json.
Complete current hashes: ../MANIFEST_SHA256.json.
Prior series-wide notes: ../provenance/pre_monograph_metadata/.
Historical 17-file gap: ../provenance/HISTORICAL_RECOVERY_GAPS.json.
