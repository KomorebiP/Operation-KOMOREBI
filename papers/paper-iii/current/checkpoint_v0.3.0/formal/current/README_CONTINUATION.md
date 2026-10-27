# Active Paper III formal source

`PaperIIIContinuation.lean` is the active import root. It includes the preserved
finite development and the three new coordinate modules. The old
`KomorebiPaperIII.lean` root and its 41-row theorem map still describe the finite
predecessor only. Passing that old root alone is not this continuation's acceptance.

Use the root `tools/rebuild_production.py` script. It enumerates every active
production module from `coverage/PRODUCTION_MODULES.json` and requires an empty
own-project object destination. The active Section 16 statement map is
`coverage/SECTION16_CORRESPONDENCE.json` at the package root.

The original Lake configuration and finite audit are retained for provenance.
The tested route for this continuation is the explicit offline compiler runner,
not a claim that the old default Lake target now covers every new module.
