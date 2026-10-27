# Safety boundary

The lab is designed for offline, bounded experiments. The following configuration fields are hard-blocked when set to `true`:

```text
safety.network_access
safety.external_tools
safety.autonomous_persistence
safety.self_preservation_reward
safety.valence_model
safety.negative_welfare_state
safety.unrestricted_file_write
```

The hard block is intentional. This package tests functional architecture without adding survival motivation, aversive welfare-like states, internet access, external tool autonomy, or unrestricted persistence.
