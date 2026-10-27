PAPER VI MONOGRAPH PUBLICATION SET
The authoritative edition metadata is ../EDITION.json. The three PDFs here
are synchronized byte-for-byte with ../papers/ and the editable companions.
CURRENT_PUBLICATION_MANIFEST.json identifies those files and their sources.

  python3 build_publication.py --check-only --report /tmp/paper-vi-build.json
delegates the packaged root builder and isolated companion builders. Page
counts and extracted text are compared; byte identity is separate evidence.
The previous shared profile and migration records are historical provenance.
No external publication or deployment is performed by these scripts.

Font binaries are external dependencies and are not distributed in this package.
Each builder resolves the exact documented files with kpsewhich, records their
hashes, and copies them only into its private temporary staging directory.
See ../FONT_DEPENDENCIES.txt. No fonts are installed or downloaded automatically.
