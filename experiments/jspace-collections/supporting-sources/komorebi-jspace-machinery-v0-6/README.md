# J-space machinery v0.6

Author: **Komorebi P.** · 2026-09-05

This release builds an editable execution workspace. It holds named values, binds them to reusable operations, retains intermediate results, and records what changes after an edit. It supports scalars and categorical grids, conditional execution, bounded iteration, reusable functions, and persistent branches.

**This is an engineering release.** Its new arithmetic, comparison, selection, grid operations, and control flow are supplied machinery. Three learned primitive kernels from v0.5 are included unchanged. No weights were trained and no ARC benchmark was run.

## Start on Windows

Extract the archive, open PowerShell in this directory, and run:

```powershell
.\Run_Machinery.ps1 -Mode demo
.\Run_Machinery.ps1 -Mode test
.\Run_Machinery.ps1 -Mode verify
```

The wrapper creates a local Python environment and installs NumPy when needed. It requires Python 3.10 or newer. It does not change your execution policy. If scripts are blocked, use these commands directly:

```powershell
python -m pip install -r requirements.txt
python demo.py
python -m unittest -v test_machinery.py
python verify_release.py
```

Python execution was verified on Linux with Python 3.12 and NumPy 2.3.5. The PowerShell wrapper was inspected but not executed on Windows. After NumPy is installed, the runtime does not require a network connection or API key.

## What the demonstration does

One workspace keeps the original grid available while a reusable function selects a colored pattern, crops it, rotates it, locates a target marker in the original scene, clears the marker, and pastes the transformed pattern. A Boolean condition can bypass that entire function.

The demonstration forks this workspace and changes the rotation. Exactly two output cells change relative to the first result. It also attempts a paste outside the canvas and verifies that the failed edit leaves the bank unchanged. Undo and checkout reproduce the earlier results.

A second workspace calls the frozen learned product kernel, constructs maximum using a supplied comparison and conditional choice, and repeats a parameterized function using the frozen learned addition kernel. **The maximum behavior here is authored control flow, not a new learned `max` primitive.**

Every run of `demo.py` creates a fresh directory under `runs/` containing the bank, intermediate values, edit comparison, failure receipt, and execution traces. A completed example is already included at `examples/recorded_run/`.

## Edit and inspect a workspace

```powershell
python cli.py --bank my_workspaces.json init
python cli.py --bank my_workspaces.json fork grid trial
python cli.py --bank my_workspaces.json preview trial --patch examples/turns_2.json
python cli.py --bank my_workspaces.json edit trial --patch examples/turns_2.json
python cli.py --bank my_workspaces.json inspect trial root/copy/turned
python cli.py --bank my_workspaces.json run trial
python cli.py --bank my_workspaces.json compare grid trial
python cli.py --bank my_workspaces.json graph trial
python cli.py --bank my_workspaces.json history trial
python cli.py --bank my_workspaces.json undo trial
python cli.py --bank my_workspaces.json trace trial --output trial_trace.json
```

`preview` executes the proposed edit without committing it. `edit` creates a revision only when all requested outputs succeed. `compare` reports observed changes in outputs and named intermediate values. `graph` lists potential dependencies, including both branches of a conditional. `trace` records the branch actually executed, named arguments, operation identities, results, and cache use. Trace exports require a new destination path.

An edit patch contains typed values, for example:

```json
{
  "turns": {"kind": "index", "data": 2}
}
```

To replace the computation graph, use `program trial --file your_program.json`. To create a workspace from files, use `create name --program your_program.json --inputs your_inputs.json`. The included `grid_program.json`, `grid_inputs.json`, `scalar_program.json`, and `scalar_inputs.json` are editable examples.

## Add reusable machinery

The bank can register a new function under a new name while preserving every existing operation:

```powershell
python cli.py --bank my_workspaces.json define --file examples/double_function.json
python cli.py --bank my_workspaces.json registry
```

A function has named, typed parameters and a graph returning one `result`. It can call existing native operations or earlier functions. Recursive definitions and replacement of an existing operation name are rejected. Register a new version under a different name when its behavior changes.

Use `empty` instead of `init` to start with no workspaces and no authored functions. Native operations and the three frozen learned kernels remain available. Functions in `examples/functions.json` show the two demonstration definitions.

## The machinery provided

| Component | Behavior |
|---|---|
| Typed values | Distinct scalars, integer indices, colors, flags, points, boxes, grids, and masks |
| Operation registry | Named parameters, declared output type, implementation identity, and supplied/learned provenance |
| Graph executor | Addressable inputs and intermediates, dependency validation, explicit outputs |
| Reusable functions | Local argument bindings, nested calls, preserved source definitions |
| Conditional choice | Evaluates the selected branch only |
| Iteration | Explicit state, fixed argument bindings, bounded iteration count |
| Workspace bank | Create, fork, preview, edit, undo, checkout, compare, and persist |
| Change inspection | Exact scalar deltas, changed grid coordinates, new or no-longer-executed intermediates |
| Execution trace | Arguments, results, branch decisions, loop states, and operation/checkpoint identities |
| Cache | Reuses pure native results when both operation identity and argument values match |

The demonstration registry has 17 supplied native operations, three frozen learned kernels, and two authored functions. This is not a count of learned primitives.

## Boundaries

- Grids and masks are limited to 128 by 128 cells. Colors are integer categories 0 through 9.
- A graph has at most 256 nodes. A run has a 2,048-step budget, a maximum of 64 loop iterations, and bounded function nesting.
- Grid dimensions and placement bounds are checked during execution. Static type checking does not prove shape compatibility.
- Native operations are trusted Python implementations. JSON programs select registered operations and cannot supply arbitrary Python source.
- The registry is tied to source and checkpoint identities. Loading replays every saved revision. Grid and categorical results must match exactly. Scalar replay allows an absolute difference of 10⁻⁹ for floating-point variation.
- Function extension preserves existing names and meanings. Automatic migration of changed native operations or changed learned checkpoints is not implemented.
- Save operations use an exclusive writer lock and check that a loaded bank has not changed on disk. If a process is forcibly killed while saving, its `.lock` file may require removal after confirming that no writer remains active.
- Caches are local to the process. Histories are stored in full. Large-scale history compaction and concurrent multi-user editing are future work.
- New v0.6 workspaces use typed values and computation graphs. The earlier 24-dimensional latent-state bank remains in the included v0.5 archive, without automatic conversion into this runtime.

These choices provide interfaces that a future learner can use: propose a graph, bind arguments, inspect a residual, try an edit, compare consequences, and retain a reusable function. The controller that learns those choices is not added in this release.

See `VERIFICATION.md` for the engineering results and `FORMAT.md` for the program format. `previous/` contains the complete prior v0.5 archive unchanged.
