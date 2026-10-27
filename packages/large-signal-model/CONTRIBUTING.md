# Contributing

Contributions should be narrow, reproducible, and explicit about which
mathematical or software contract they change.

## Before opening a pull request

1. Create a focused branch.
2. Install `.[dev]` under Python 3.12 or 3.13.
3. Add or update tests before changing a declared exactness or benchmark claim.
4. Run the core tests, both examples, and a wheel build.
5. Update documentation and the claim boundary where applicable.

Do not commit credentials, downloaded ARC environments, runtime recordings,
generated result directories, proprietary third-party material, or large
binaries unrelated to the paper.

By submitting a contribution, you represent that you have the right to
submit it and permit the project owner to incorporate it under the
repository's existing license terms. No open-source license grant is implied
by repository visibility.
