# Reader storage and delivery

The reader workflow verifies the complete generated site, source identities,
local links, accessibility safeguards and contents of every reading ZIP before
packaging the Pages output. `tools/reader_delivery.py` then:

- retains the PDFs, manuscript sources, Lean sources, figures and runtime assets;
- stores generated notation and selection indexes as deterministic gzip files;
- checks that each compressed index restores the exact original bytes;
- retains raw JSON exports and complete reading ZIPs as byte-identical release
  assets bound to the full collection commit;
- updates native download links and records their checksums in `delivery.json`;
- installs a small index loader with native gzip decompression and the existing,
  pinned fflate fallback for browsers without `DecompressionStream`;
- supplies a browser handoff for old bookmarked export routes and native release
  links on the custom 404 page, including when JavaScript is disabled.

Native HTML reading remains available without JavaScript. The release downloads
also work without JavaScript. Existing bookmarked binary URLs now hand off in a
browser; command-line consumers should use the export URL in `delivery.json` or
the current `downloads/index.json`. Release ZIP filenames and contents remain
unchanged. Raw JSON export filenames include their directory names to prevent
collisions; the JSON contents remain unchanged.

`tools/publish_reader_downloads.py` runs only on trusted main-branch builds. It
publishes and verifies all exports before Pages can deploy. A retry checks
existing assets by size and SHA-256 and refuses to overwrite different bytes.
Reader download releases do not replace the project's latest release.

The final Pages output still has a hard 1 GiB gate. `delivery-report.json` records
the storage change. `delivery-manifest.json` and `SHA256SUMS.txt` accompany the
release for reproduction. Release assets must be retained while a deployed site
or historical download link uses them.
