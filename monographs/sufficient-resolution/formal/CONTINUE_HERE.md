# Continue here — Sufficient Resolution v0.16.0

Author: Komorebi P.

Open `PROGRESS.md` and `BLOCK_16_THEOREMS.md`, preserve all proof boundaries, then
continue with **sample-wise calibration certification**. The current exact positive
contract uses a split calibration frame `U,R` with `U R = I`; the approximate-frame
contract permits `||I-U R|| <= rho < 1`. Measured calibration operator error and model
fit generate a whole-operator allowance used by the inherited generalized discrepancy
recovery theorems.

Do not assume that perfect fit on a proper calibration subspace controls the whole
operator: `CalibrationExamples.arbitrarily_large_unseen_error` formally disproves that.
Do not infer the calibration truth-error allowance from fitting data alone. The next
block should derive it from finite sample-level assumptions and explicit frame geometry.
