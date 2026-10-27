# Block 46 failure ledger

- The source archive contained no project proof objects. The v0.45 dependency closure therefore had to be rebuilt before Block 46 could be tested.
- Two predecessor build commands reached 3,055/3,057 and 3,056/3,057 jobs before their external windows closed. They were classified as inconclusive. The unchanged tree was resumed until all 3,057 jobs completed.
- An early verification wrapper invoked direct Lean files from the wrong working directory. Those path failures were discarded and the gates were rerun from the project root.
- A combined negative-control loop stalled after the first expected rejection. Each remaining control was rerun independently and rejected for the intended contradiction.
- No timeout, partial build, cache population, or failed wrapper is counted as proof evidence.
