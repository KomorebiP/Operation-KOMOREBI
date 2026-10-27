# Execution notes

The combined first audit invocation exceeded the tool execution window after Operator Workspace and Stable Quotient completed. Ambient Packets had printed 59 passing unit tests but its subsequent full verifier did not complete.

The Packet Closure full verifier exceeded the bounded 28-second child budget. Its pytest grandchild survived the parent timeout; it was identified by its exact package path. Before a termination attempt, it completed and printed `505 passed in 145.11s`. No live descendant remained. This is a completed unit-test transcript, but its parent verifier had already timed out, so there is no completed full package-verifier result. The log retains both events in order.

All other recorded completed checks have separate exit codes in fresh_checks.json. Verification of saved evidence is not retraining or an independent replication. No one-use Semantic Retraction learned bank was consumed. Entry--Cone--Holonomy was verified without repeating its one-shot learned endpoint evaluation.

An initial request for an interactive execution session was rejected by the container before a command was run. Subsequent checks used ordinary bounded executions.
