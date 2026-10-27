# Real Run Checklist

## Before staging

- [ ] NVIDIA driver and CUDA-visible PyTorch work in the isolated environment.
- [ ] The external repository is at the pinned commit.
- [ ] `checkpoint_37` exists as a regular file.
- [ ] The checkpoint's full SHA-256 has been recorded.
- [ ] The GPT-2 base model is available locally or by a frozen model ID/revision.
- [ ] `data/prontoqa_test.json` exists in the pinned repository.
- [ ] The real config was calibrated on a disjoint support.
- [ ] The final task count is fixed.
- [ ] Group IDs reflect proof-template dependence where possible.
- [ ] No final result has been inspected.

## Stage

```powershell
.\Run_Real_LRM_Pilot.ps1 -StageOnly
```

- [ ] `frozen/real_preaudit_seal.json` exists.
- [ ] `frozen/donor_plan.json` exists.
- [ ] `python -m sric_real_lrm verify-seal frozen/real_preaudit_seal.json` passes.
- [ ] The seal is copied to an immutable archive location.

## Execute

```powershell
.\Run_Real_LRM_Pilot.ps1 -RunOnly
```

- [ ] Every ordinary trace is finite.
- [ ] Every replay stays under the sealed tolerance.
- [ ] The result status is recorded without manual relabeling.
- [ ] Runtime errors and OOMs are preserved.
- [ ] No threshold or donor assignment is changed.

## Verify and archive

```powershell
python -m sric_real_lrm verify-result .\results\real_checkpoint_audit.json
python .\build_manifest.py
python .\verify_package.py
```

- [ ] Result receipt verifies.
- [ ] Complete environment package list is archived.
- [ ] CUDA, GPU, driver, Python, PyTorch, and Transformers versions are recorded.
- [ ] Raw logs and failures are retained.
