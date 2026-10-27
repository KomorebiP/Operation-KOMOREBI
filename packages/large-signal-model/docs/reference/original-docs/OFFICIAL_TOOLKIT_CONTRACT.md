# Official ARC-AGI-3 toolkit contract

The adapter is pinned to:

```text
arc-agi 0.9.9
arcengine 0.9.3
Python >= 3.12
```

It uses only the documented local interface:

```python
Arcade(
    arc_api_key="",
    operation_mode=OperationMode.OFFLINE,
    environments_dir="...",
    recordings_dir="...",
)

env = arcade.make(
    game_id,
    seed=seed,
    save_recording=True,
    include_frame_data=True,
    render_mode=None,
)

observation = env.reset()
observation = env.step(GameAction.from_id(action_id), data=data, reasoning=reasoning)
```

The runner reads only public wrapper fields: `action_space`, frame data, state, levels completed, win-level count, and available actions. It does not access the internal `_game` object or read source files.

A contract test with stubbed official classes verifies constructor mode, action conversion, coordinate data, and reasoning fields. `Run_Official_Adapter_Smoke.ps1` performs a real local-toolkit load against the bundled non-benchmark test environments after the official dependencies are installed.
