# ProsQA Follow-up Protocol

## Purpose

PrOntoQA is the source-faithful causal admission tier. ProsQA is the intended structure-sensitive tier. It should be activated only after the PrOntoQA adapter passes replay.

## Stronger claim

A ProsQA result may use `PROCEDURE_SPECIFIC` only when all of the following are implemented before final audit:

1. proof graphs or derivation structures are extracted independently of text surface;
2. donors are matched on final answer and broad difficulty;
3. a structure-near donor and structure-far donor are assigned for every recipient;
4. the primary statistic is the contrast

   `loss(far donor) - loss(near donor)`;

5. the contrast has a positive frozen interval and positive-task fraction;
6. semantic twins preserve proof topology while changing wording, entity names, and premise order;
7. final proof structures are held out by template family.

## Why the contrast matters

A harmful arbitrary donor can reflect task identity, vocabulary, or context formatting. The far-minus-near contrast asks whether disruption grows with formal solution-structure distance after answer and difficulty are controlled.

## Additional adapter work

ProsQA answers are not limited to Boolean labels. A separate answer parser and protected loss contract are required. The current PrOntoQA adapter must not be silently reused as if these formats were identical.

## Frozen source references

The external source lock records the ProsQA test-data Git blob, checkpoint repository, checkpoint revision, and checkpoint filename. Those entries are planning locks, not evidence that the ProsQA checkpoint has been executed.
