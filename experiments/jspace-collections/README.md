# J-space collections and actions v0.7

Author: **Komorebi P.** · 2026-09-06

This machinery release adds **typed object collections** and a **common workspace action interface**. Programs can extract objects, filter them, apply a function to each object, and accumulate their results into a grid. Controllers can observe a workspace, propose input or graph edits, inspect their consequences, and commit a matching saved proposal.

No training was performed. Object grouping, the example programs, and the example proposals are supplied. The frozen learned kernels from v0.5 remain unchanged. This is a foundation for a future controller, not an autonomous solver or an ARC performance result.

## Run

Extract the ZIP and open PowerShell in this directory:

```powershell
.\Run_Machinery.ps1 -Mode demo
.\Run_Machinery.ps1 -Mode test
.\Run_Machinery.ps1 -Mode verify
```

The wrapper creates a local Python environment and installs NumPy when needed. It requires Python 3.10 or newer and does not modify your execution policy. Direct Python commands are also available:

```powershell
python -m pip install -r requirements.txt
python demo.py
python -m unittest -v test_machinery.py test_collections.py
python verify_release.py
```

After dependency installation, all runtime operations are local and need no API key or network connection. Python was tested on Linux. The PowerShell wrapper was inspected but not executed on Windows.

## What is new

| Machinery | Purpose |
|---|---|
| Object values | Keep pixels, coordinate frame, source identity, and transformation lineage together |
| Typed collections | Carry up to 64 objects, scalars, grids, masks, or other supported base values |
| `map` | Apply a registered operation or function to each item |
| `filter` | Keep items selected by a Boolean predicate |
| `fold` | Carry an accumulator through a collection, such as painting objects into a scene |
| Object operations | Extract components, inspect area/color/bounds, translate, recolor, erase, and paint |
| JSON action interface | Observe, propose, commit, fork, undo, and compare |
| Proposal receipts | Bind a candidate to its source revision, operation library, predicted outputs, and constraints |
| Residual feedback | Report target mismatches by output type, including changed cells and shape failures |
| Protected outputs | Reject a proposal that changes an output the caller required to preserve |

Existing named bindings, functions, conditional execution, bounded repetition, branch history, previews, pure-operation caching, and atomic saves remain available.

## Concrete demonstration

The example scene contains three same-color components. An authored function keeps the two objects with area at least two. A map translates them, and two folds erase their original pixels and paint their new pixels. The smaller distractor remains in place.

The action interface previews a supplied two-column translation against a supplied target. It reports ten mismatching cells before the edit and zero afterward. The bank is unchanged during preview. A saved receipt then commits after the bank is reloaded. Collision attempts, unmet target requirements, and attempts to reuse a stale receipt are rejected.

**The correct offset and target are provided by the example. The runtime does not discover them.** These are behavioral checks of the machinery.

`demo.py` writes a new directory under `runs/`. The shipped `examples/recorded_run/` already contains a complete run, including initial and final values, the proposal, commit, rejected attempts, branch comparison, and persistent bank.

## Use the action interface

Start a fresh demonstration bank:

```powershell
python cli.py --bank my_workspaces.json init
python control.py --bank my_workspaces.json --request examples/observe_objects.json --response observation.json
python control.py --bank my_workspaces.json --request examples/move_proposal.json --response proposal.json
python control.py --bank my_workspaces.json --commit proposal.json --response commit.json
python cli.py --bank my_workspaces.json run objects
python cli.py --bank my_workspaces.json inspect objects root/shifted
```

Response files are written only to new paths. The example request is based on revision `r000002`, which is the object workspace in a freshly initialized bank. After changing the workspace, observe it again and update `expected_revision` in your request. Stale proposals are deliberately rejected.

The response contains the full proposal receipt and inspection data. The console prints a short status when `--response` is used. Without it, the complete response is printed as JSON. A successful bank write and a response-file write are separate filesystem operations. If response export fails after a bank write, the error includes `bank_updated: true`.

Direct workspace editing is still supported:

```powershell
python cli.py --bank my_workspaces.json fork objects alternative
python cli.py --bank my_workspaces.json preview alternative --patch examples/offset_2.json
python cli.py --bank my_workspaces.json edit alternative --patch examples/offset_2.json
python cli.py --bank my_workspaces.json compare objects alternative
python cli.py --bank my_workspaces.json graph objects
python cli.py --bank my_workspaces.json trace objects --output object_trace.json
python cli.py --bank my_workspaces.json undo alternative
```

The direct editor applies the requested change without the optional target/lock constraints of a proposal. Use the action interface when those constraints should govern the edit.

## Python integration

```python
from collection_scenarios import make_bank, proposal
from machinery.actions import Actions

bank = make_bank()
interface = Actions(bank)
observation = interface.apply({"action": "observe", "workspace": "objects"})
preview = interface.apply(proposal(bank))

if preview["status"] == "ready":
    result = interface.apply({"action": "commit", "receipt": preview["receipt"]})
```

`proposal(bank)` in this example supplies a hand-authored edit. A future controller would construct that request itself. Functions can still be registered through `Store.define_function` or the existing CLI `define` command.

## Scope and limits

- Component extraction is an authored same-color connected-component algorithm. Connectivity is explicitly 4 or 8. This is not learned object discovery.
- Object source and origin identifiers record provenance. Regrouping a changed scene creates new identifiers, so they are not persistent physical-object identities across observations.
- Collections have one level and at most 64 entries. Nested collections are rejected. Map and filter preserve order; fold processes items in that order.
- Grids are at most 128 by 128, with integer colors 0 through 9. Graphs permit at most 256 nodes and share a 2,048-step execution budget. Existing iteration and function-depth bounds remain.
- Translation must keep every object pixel in its coordinate frame. Painting checks frame compatibility and can reject occupied destinations. Erasing checks that the selected source pixels still match.
- Scalar tolerances are explicit in proposal constraints. Grid and mask comparisons are exact. Feedback is reported by output type without pretending that scalar error and cell mismatch counts share one unit.
- Proposal hashes detect accidental changes. They are not signatures or authorization credentials. Commit rechecks the revision, library, execution result, targets, and protected outputs.
- A receipt becomes stale after its workspace changes. Restoring exactly the original revision can make that same proposal applicable again. Receipts are not single-use tokens.
- Native operations remain trusted local Python. JSON requests can select registered operations and edit graphs, but cannot introduce arbitrary Python code.
- The action interface currently edits existing inputs and graph structure. Autonomous search, action selection, representation learning, learned stopping conditions, and training updates are not included.
- v0.6 bank files are not silently converted to this version. Its complete original ZIP is preserved under `previous/`. The v0.6 programs and example outputs were checked in the new runtime, but automatic bank migration remains unfinished.

The demonstration registry contains **29 supplied native operations, three frozen learned kernels, and three authored functions**. It does not contain 35 newly learned operations.

Read `PROTOCOL.md` for request and node formats and `VERIFICATION.md` for the checks and their limits.
