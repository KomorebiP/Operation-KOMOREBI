# Frozen records

- `fake_fixture_preaudit_seal.json` is the valid seal for the engineered adapter fixture.
- `fake_fixture_donor_plan.json` is the corresponding procedure-donor assignment.
- `real_preaudit_seal.json` is intentionally absent from the distributed package. It can be created only after the external repository, base model, checkpoint, data file, calibrated config, and final task subset exist on the executing machine.

A generated real seal must be preserved before `run-real` is invoked.
