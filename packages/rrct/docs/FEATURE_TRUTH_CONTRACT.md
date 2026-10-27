# Feature-truth contract

The common schema is intentionally broader than any one experiment. v0.60 prevents that breadth from becoming silent configuration fiction and binds runtime/checkpoint ownership through the experiment registry.

## Contract statuses

| Status | Meaning |
|---|---|
| `implemented` | The selected experiment or common runtime reads the setting and it changes an execution path. |
| `partial` | The setting is meaningful only for some families or only one direction of the switch is universal. |
| `unsupported` | The selected family has no detected execution path for this nondefault setting. |

With strict mode enabled, unsupported nondefault settings stop the run before output is created.

```toml
[run]
strict_feature_contract = true
fail_on_unused_setting = true
```

## Commands

```text
python -m rrct_lab contract CONFIG.toml
python -m rrct_lab validate CONFIG.toml
python -m rrct_lab features
```

`contract` reports only nondefault settings. `features` reports the status of every schema key across every experiment family.

## Scientific use

A frozen run stores its feature contract beside the resolved configuration. This makes it possible to distinguish:

- a mechanism that was enabled and executed
- a retained but partial compatibility setting
- a setting that would otherwise have been ignored

The AST audit is a practical contract checker, not a formal proof that every numerical value has a large behavioral effect. Focused knob-perturbation tests remain appropriate for high-stakes comparisons.
