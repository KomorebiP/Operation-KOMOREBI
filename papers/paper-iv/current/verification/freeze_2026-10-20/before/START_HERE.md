# Paper IV complete verification delivery — v1.1.0

The directory `Paper_IV_Verification_Closeout_v1.1.0/` is the frozen core package.
Its README, five-page closeout report, full Lean source, compiler evidence,
three retained readers, editable baseline and progress ledger are all included.
`Delivery_Receipts/` adds the actual fresh-extraction tests and the retained failed
30-second consumer attempt followed by the successful same-source retry.

After extracting the ZIP, run:

```bash
python3 -B verify_bundle.py
```

This validates every delivered file and the frozen core's recorded gates. It is
not a fresh Lean invocation. For complete source replay, follow the core README.
No compiler, dependency cache, standalone fonts or automatic installation is
included. The exact final archive digest is in the separate
`Paper_IV_Delivery_Verification_v1.1.0.json` download.
