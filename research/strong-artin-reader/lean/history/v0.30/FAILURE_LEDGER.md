# Failure ledger — v0.30

Failures are retained separately from proof evidence.

## Operational interruptions

- A streaming container launch was unsupported. Runtime assembly and all proof checks subsequently used synchronous bounded commands.
- Runtime assembly verified all seven parts and the combined archive; extraction completed with exit code zero.
- A development dependency batch was interrupted after completed modules; incomplete module verdicts were not promoted.
- A fresh replay batch was interrupted by the outer 100-second wrapper after ten completed modules in that batch. Its persistent manifest retained the observed zero return codes. No verifier process remained running. The next module and remaining closure were compiled in smaller unchanged-source batches. Final first-replay status: PASS.

## Rejected compilation drafts

There are 13 rejected attempts in `development/ATTEMPTS.jsonl`. Raw diagnostics and source hashes are retained; rejected draft source contents are not certified as final.

- `ProfiniteCyclicGenerator` returned 1; source `bbb1c81b2f03b97a9ddf304b159ca9efe820b58dda376983c2b06b4f85976083`; log `development/logs/ProfiniteCyclicGenerator.1789183535930683988.log`.
- `ProfiniteCyclicGenerator` returned 1; source `45a28a9c1abfc7aefc35fc377e8b483e01a15648118cae8f01768c6f38a69543`; log `development/logs/ProfiniteCyclicGenerator.1789183554887777748.log`.
- `ProfiniteCyclicGenerator` returned 1; source `adaa08a3ad66b42b655863a870f79a398f585f621394185f0ac53268f827de47`; log `development/logs/ProfiniteCyclicGenerator.1789183588309120181.log`.
- `ProcyclicFrobeniusLifting` returned 1; source `8790a1979eb132e608ee1f75029d307a18122cf21b7229e5548ba184871af565`; log `development/logs/ProcyclicFrobeniusLifting.1789183655355549132.log`.
- `UnramifiedSquareZeroLifting` returned 1; source `db6414612a8e7ca7f740638686e00ba04ef3ea6b9a46df8534743869152ed090`; log `development/logs/UnramifiedSquareZeroLifting.1789183773451625739.log`.
- `KernelGaugeCorrection` returned 1; source `f79647f49fa03f674f3ceae2b62065244cc6e91fe76b979d9f607a3f51d79678`; log `development/logs/KernelGaugeCorrection.1789183932287656996.log`.
- `UnramifiedGaugeObstruction` returned 1; source `3f111d78654be4fa2fa40cfe8a034e6618df3fd671794115b699bee6a81bd058`; log `development/logs/UnramifiedGaugeObstruction.1789184008457648863.log`.
- `UnramifiedGaugeObstruction` returned 1; source `ec20583d50b5feeb07249c2d2e6f57f777278e1f310501dc1967714e5683642c`; log `development/logs/UnramifiedGaugeObstruction.1789184034555492102.log`.
- `UnramifiedGaugeObstruction` returned 1; source `e861819bc262d1dc8297b2132ab2acdcf224c1917b23ee08a58c4b5b6df5f6f2`; log `development/logs/UnramifiedGaugeObstruction.1789184068597468920.log`.
- `FrobeniusRestrictionNorm` returned 1; source `80221d4f2cf25e0e4daf6499a023389172b5f3914d3f0dc6f1114dde7240d290`; log `development/logs/FrobeniusRestrictionNorm.1789184144810440430.log`.
- `FrobeniusRestrictionNorm` returned 1; source `feb0c8a63a066bb021f810d8972ddb47353634c4965b7d324d311df7664a2a57`; log `development/logs/FrobeniusRestrictionNorm.1789184170010361828.log`.
- `FrobeniusLocalizationCokernel` returned 1; source `bebcae46356ca8a2b9850bf42a52d77b0e1a05fd4bdf4cd3d1fccb7426200d9c`; log `development/logs/FrobeniusLocalizationCokernel.1789184240694260709.log`.
- `FrobeniusLocalizationCokernel` returned 1; source `6ab26642029656e58d217770ec442fccb38f46cbe9438d07968d8d188e4f4290`; log `development/logs/FrobeniusLocalizationCokernel.1789184264985119327.log`.

Causes: extensionality tactics overconsuming binders, guessed API names, category universe/coercion mismatches, missing direct dependency build, quotient simplification, recursive field notation, and unused-variable warnings. These are development failures, not counterexamples to the accepted theorems.

## Mathematical negative results, not implementation failures

The no-C3-lift and nonzero prescribed degree-three obstruction are accepted, kernel-checked theorems. The unramified source permits Frobenius order to grow; fixing its degree-three restriction restores a real obstruction. These are limitations of stronger possible claims, not of the proved unrestricted lifting theorem.

## Review boundary

Self-review plus Lean checking and an exact-arithmetic corroboration script. No second kernel, external specialist referee or all-historical replay is claimed.
