# Collection and action protocol

Author: **Komorebi P.**

## Typed objects and collections

An object stores its source identifier, origin identifier, frame dimensions, and explicit `[row, column, color]` pixels. Pixels are sorted and duplicate coordinates are rejected. The source is the typed input grid's hash. Component extraction creates the origin identifier from that source and the original pixels. Translation and recoloring retain the origin identifier while changing the current object value.

The object representation can carry multiple colors. The supplied component extractor creates same-color objects. Requesting one color from a multicolor object returns an ambiguity error.

Collection kinds include `list[object]`, `list[index]`, `list[scalar]`, `list[grid]`, and the other supported base kinds. Elements are typed values. An empty collection retains its declared element type:

```json
{"kind": "list[index]", "data": []}
```

There is no inferred conversion between a scalar, color, index, or Boolean flag.

## Collection nodes

A map binds each element to the operation's `item` parameter:

```json
{
  "id": "shifted",
  "map": {
    "op": "object.translate",
    "items": "selected",
    "bindings": {"offset": "offset"}
  }
}
```

The result has the operation's output type wrapped in a collection. Operations returning another collection are not accepted by map in this version.

A filter's operation must return a flag:

```json
{
  "id": "selected",
  "filter": {
    "op": "keep_large",
    "items": "objects",
    "bindings": {"minimum": "minimum"}
  }
}
```

A fold binds both `item` and `state`. The operation must preserve the state type:

```json
{
  "id": "placed",
  "fold": {
    "op": "object.paint",
    "items": "shifted",
    "state": "cleared",
    "bindings": {"background": "background", "overwrite": "overwrite"}
  }
}
```

An empty map or filter returns an empty typed collection. An empty fold returns its initial state. Unused per-item bindings are not evaluated, although all graph bindings and types are still validated. Per-item calls share the normal execution budget and have trace paths such as `root/shifted/item_0`.

`object.paint` with `overwrite: false` requires destination pixels to equal the supplied background color. With `overwrite: true`, later items can overwrite earlier ones. `object.erase` checks the object's current pixel colors against the accumulator before replacing them with background. All operations produce new values. A failure partway through a fold can appear in the inspection trace but cannot partially commit a workspace revision.

## Observe

```json
{"action": "observe", "workspace": "objects"}
```

Observation returns the current revision, registry identity, typed inputs, graph, outputs, potential dependencies, and the executed trace. Potential dependencies include branches that may not have executed.

## Propose

```json
{
  "action": "propose",
  "workspace": "objects",
  "expected_revision": "r000002",
  "updates": {"offset": {"kind": "point", "data": [0, 2]}},
  "locked_outputs": ["original"],
  "require_target_match": false
}
```

Optional fields are `graph_edits`, `targets`, and `atol`. Targets map output names to typed expected values. Setting `require_target_match` to true requires at least one supplied target. The default scalar tolerance is 10⁻⁹. Protected outputs must exist both before and after the proposal.

A proposal is evaluated without changing the bank. Successful execution can still be rejected if a target requirement or protected output fails. Its feedback contains:

- Before and after target comparisons, when targets were supplied.
- Observed output and intermediate-value differences.
- The actual execution trace, including filter decisions and fold steps.
- Protected-output checks.
- A receipt containing the exact candidate, predicted outputs, constraints, and source identities.

Residuals report missing outputs and shape mismatches explicitly. Cell coordinates are capped at 256 entries with a truncation flag. No matching score is reported for an absent target. Scalar errors and categorical cell mismatches are kept separate.

## Edit graph structure

The `graph_edits` list applies up to 64 edits in order to a copy of the graph. Supported forms are:

```json
{"kind": "rebind", "node": "product", "argument": "b", "ref": "a"}
```

```json
{"kind": "replace_node", "node": "product", "value": {"id": "product", "op": "number.add", "args": {"a": "a", "b": "b"}}}
```

```json
{"kind": "add_node", "value": {"id": "total", "op": "number.add", "args": {"a": "a", "b": "b"}}}
```

```json
{"kind": "remove_node", "node": "unused"}
```

```json
{"kind": "set_output", "output": "answer", "ref": "total"}
```

The resulting graph must still have valid names, references, types, and no cycles. Rebinding operates on explicit named arguments. To change a map, filter, fold, or choice configuration, replace that node. Input updates must refer to existing declared inputs.

## Commit

```json
{"action": "commit", "receipt": {"proposal_id": "...", "payload": {"...": "..."}}}
```

Commit checks that the receipt payload has not changed, that the original revision and registry still match, and that the candidate executes with its predicted outputs and constraints. Only then does the ordinary edit mechanism create a new revision. A rejected or stale receipt cannot commit.

The command-line `--commit proposal.json` option accepts either a receipt or a complete proposal response. A proposal response is portable across process restarts because its data and source identities are serialized. Proposal receipts are not automatically stored inside the bank.

The registry identity is conservative. Adding a function under a new name preserves existing operation definitions but changes the registry identity, so previously prepared receipts must be proposed again.

## Other actions

```json
{"action": "fork", "workspace": "objects", "name": "trial", "expected_revision": "r000003"}
```

```json
{"action": "undo", "workspace": "trial", "expected_revision": "r000003"}
```

```json
{"action": "compare", "a": "objects", "b": "trial"}
```

These wrap the existing bank operations. Creating workspaces, checking out arbitrary saved revisions, and registering functions remain available through the original CLI and Python API.

## What a future controller must supply

The interface does not decide which operation, object representation, input edit, or graph structure to try. It also does not infer goals or supply hidden answers. A future controller must construct the proposal from observations and available evidence. The machinery executes it, exposes its consequences, and preserves the selected computation if committed.
