# Workspace and program format

Author: **Komorebi P.**

## State and meaning

A workspace has a named revision head. Each revision stores typed inputs and a graph. Operations live in a shared registry, with explicit signatures and implementation identities. Outputs are reproducible consequences of that state.

This is a concrete, editable J-like workspace interface. Its organization is engineered. It is not a claim that an intrinsic latent geometry has emerged.

## Values

Every input is represented by a kind and data:

```json
{
  "x": {"kind": "scalar", "data": 3.5},
  "turns": {"kind": "index", "data": 1},
  "selected_color": {"kind": "color", "data": 2},
  "enabled": {"kind": "flag", "data": true},
  "destination": {"kind": "point", "data": [3, 6]},
  "region": {"kind": "box", "data": [1, 1, 3, 3]}
}
```

Point coordinates are row, column. Box coordinates are row start, column start, row end, column end, with exclusive end coordinates. Scalars do not silently become indices or colors. Masks are Boolean matrices, not numeric matrices containing 0 and 1. Values copy their array inputs and expose read-only arrays through the standard API.

## Nodes and bindings

A node names the operation and binds arguments by role:

```json
{
  "id": "difference",
  "op": "learned.channel_17",
  "args": {"a": "left", "b": "right"}
}
```

Strings in bindings refer to inputs or other nodes. Node identifiers cannot overwrite input names. Forward references are allowed within a graph, while cycles and missing references are rejected. JSON key order has no effect on argument roles.

A graph declares one or more outputs:

```json
{
  "nodes": [
    {"id": "total", "op": "number.add", "args": {"a": "x", "b": "y"}}
  ],
  "outputs": {"answer": "total", "original_x": "x"}
}
```

Only values required by requested outputs are executed. All declared nodes are still checked for valid types, bindings, and cycles.

## Choice and repetition

A conditional requires a flag and two branches of the same declared type:

```json
{
  "id": "result",
  "select": {"condition": "enabled", "then": "transformed", "else": "original"}
}
```

The unselected branch is not evaluated unless another requested output needs it. This permits a guard to skip operations whose runtime requirements do not hold, such as extracting from an empty mask. It does not make invalid branch types legal.

A repeat carries one named state through a registered operation:

```json
{
  "id": "rollout",
  "repeat": {
    "op": "advance",
    "state": "start",
    "count": "count",
    "bindings": {"delta": "delta"}
  }
}
```

The operation must have a `state` parameter and return the same type. Other bindings are fixed for the loop. A zero count returns the initial state without evaluating unused loop bindings. Negative or excessive counts fail. This release supports fixed bounded iteration, not learned stopping conditions or unbounded loops.

## Reusable functions

```json
{
  "name": "double",
  "parameters": {"state": "scalar"},
  "body": {
    "nodes": [
      {"id": "twice", "op": "number.add", "args": {"a": "state", "b": "state"}}
    ],
    "outputs": {"result": "twice"}
  }
}
```

Function-local values receive qualified names such as `root/copy/patch` in execution traces. Iteration adds paths such as `root/rollout/step_0/next`. Local names do not capture similarly named values from a caller. All required information passes through named arguments.

The function identity incorporates its body, signature, and the identities of called operations. New functions can be registered under fresh names. Replacing the meaning of an existing name is rejected.

## Edits, transactions, and traces

`preview` evaluates a candidate snapshot and returns its trace and observed differences. `edit` commits a new revision only after the candidate produces all outputs successfully. A failed candidate may populate the in-memory pure-result cache, but it does not change saved inputs, programs, revisions, or branch heads.

Forked workspaces initially share a revision. Later edits create a new child revision for only the edited branch. Undo moves the branch head to its parent. Checkout selects an existing revision. There is no automatic branch merge or history deletion.

The optional expected-revision argument detects stale edits. Disk saves also take an exclusive writer lock and compare the file against the version originally loaded. These are local concurrency controls, not an external collaboration service.

Trace records describe observed execution. Dependency records describe possible data flow. A value difference after an edit is evidence of that specific intervention's consequence, not a general causal law. Cache hits reuse only registered pure native operations under matching operation identities and typed argument values.

## Future learning interface

The machinery exposes actions a learner could eventually select:

- Propose a graph or replace a node's operation and bindings.
- Choose a representation using grid, mask, region, or scalar values.
- Preview a change and inspect the resulting residual or failed requirement.
- Fork an alternative and compare its outputs and intermediate values.
- Store a parameterized function with an executable definition.
- Export complete traces for later training.

These actions and the demonstration programs are supplied in v0.6. No proposal policy, reward model, learned representation controller, autonomous function discovery, or training update is performed here.
