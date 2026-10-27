# Release Process

1. Build the monograph from a clean source tree.
2. Confirm zero undefined references, warnings, and overfull or underfull boxes.
3. Run PDF preflight and render every page.
4. Check for blank pages, malformed glyphs, clipping, and border contact.
5. Compare the clean rebuild with the candidate release at the rendered-pixel level.
6. Copy the final PDF and complete source tree into the release-assets directory.
7. Calculate SHA-256 hashes after all files are final.
8. Verify `VERSION`, `CITATION.cff`, `RELEASE_MANIFEST.json`, release notes, and tag agree.
9. Create the tag `projector-refinement-physics-volume-ii-v1.0.0`.
10. Upload the PDF, source archive, and `SHA256SUMS.txt` without replacing different bytes under the same version.

Any change to the PDF or source archive after hashing requires a new checksum manifest. A scientific correction that changes a formula, theorem, benchmark, or claim boundary requires a new release version rather than silent asset replacement.
