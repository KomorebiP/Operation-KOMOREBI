# Producing compiler runtime

Author: Komorebi P.

Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, and mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06 were used for all five checked blocks. The compiler, kernel, and dependency sources were not modified. The verifier checks every locked dependency revision and rejects tracked source changes.

The producing environment denies readlink on the runtime's numeric current-process executable path, while allowing /proc/self/exe. The attached app_path.c redirects only that self-location request to /proc/self/exe. It is loaded with LD_PRELOAD; other requests and all proof checking remain unchanged. A normal installation does not need this adapter. No compiler or mathlib binaries are included in this release.

The fresh block build and namespace axiom audit are recorded one directory above. The retained first-block positive and negative runtime controls use the same real compiler: a valid arithmetic identity must pass and an invalid proof of a false identity must be rejected. These controls do not replace the namespace audit.
