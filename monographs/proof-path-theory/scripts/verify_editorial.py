"""Compatibility entry point for the current publication audit.

The prior editorial verifier is preserved under historical/publication_1.5.0/.
Run pytest and the separate finite checkers for execution evidence.
"""
from verify_publication_edition import main
if __name__ == "__main__":
    raise SystemExit(main())
