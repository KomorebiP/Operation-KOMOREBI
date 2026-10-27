PAPER I — TWO-FILE RELEASE DELIVERY

The release is delivered as two ordinary ZIP files:

1. Komorebi_Paper_I_Release_Core_2026-10-15.zip
   Contains all current PDFs, editable sources, Lean modules, computations,
   current verification evidence, and the complete release manifest.
2. Komorebi_Paper_I_Completion_Block08_v0.8.0_2026-10-12.zip
   The unchanged, previously accepted historical checkpoint. Its filename
   and October 12 date identify the predecessor, not the current release.

Extract the core ZIP. From its Komorebi_Paper_I_Release_2026-10-15 directory,
run the following with the actual path to the second downloaded ZIP:

  python3 scripts/assemble_release.py /path/to/Komorebi_Paper_I_Completion_Block08_v0.8.0_2026-10-12.zip

The helper verifies the historical archive's size and SHA-256, copies that
ZIP intact to:

  source/predecessor/Komorebi_Paper_I_Completion_Block08_v0.8.0_2026-10-12.zip

and runs the full release integrity check. Do not extract the historical
ZIP into that destination. Manual assembly is also possible: copy it intact
to the exact destination, then run:

  python3 scripts/verify_integrity.py

The core is one part of the complete release until this assembly is done.
Both parts together reproduce the complete recorded release tree. The full
manifest deliberately includes the historical ZIP; before assembly, an
integrity check will report that single missing file. The current PDFs and
fresh formal-verification workflow do not require opening the historical ZIP.

Historical ZIP: 58,279,775 bytes
SHA-256: 16d3c743b06fa8ceadc3d2499a52c96247a55bc03ea5ec2844d6f0d363d318cc
