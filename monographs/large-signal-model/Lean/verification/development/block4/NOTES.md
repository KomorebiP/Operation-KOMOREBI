# Additional development observations

The numbered JSON records preserve compiler stdout/stderr and their corresponding source snapshots. The source-candidate scanner attempt is stored separately. The final release run is not one of these development records.

A release-ledger generation command (outside the Lean compiler) initially stopped with `KeyError: 'Komorebi.LSM.invariantSequence_stays_fixed'`. Inspection found the actual inherited declaration `Komorebi.LSM.invariantSequence_stays`. The ledger was regenerated with that target. This note records the captured command error, not a fabricated subprocess receipt.

The new negative-control word example was initially drafted using tentative theorem names. Those names were resolved against the actual declaration list before the verifier executed it. The accepted rejection comes from the false equality 5/32 = 3/16, not from an unresolved declaration.
