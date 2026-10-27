# External storage contract

The implementation uses SQLite rollback-journal transactions with explicit
BEGIN IMMEDIATE, COMMIT and ROLLBACK, and synchronous=FULL. Its intended atomic
publication behavior relies on the SQLite/OS/filesystem contract, not a Lean proof
of physical writes. Official primary references consulted September 13, 2026:

- https://www.sqlite.org/atomiccommit.html (including hardware and flushing assumptions)
- https://www.sqlite.org/lang_transaction.html

The process-exit suite is bounded implementation evidence. It is not power-loss
certification, hostile rollback protection, distributed consensus or universal
refinement of Python/SQLite behavior to the functional journal.
