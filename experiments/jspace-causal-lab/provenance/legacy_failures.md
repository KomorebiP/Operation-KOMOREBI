# Interface-build failures and resolutions

## 1. Legacy skip-exchange contract mismatch

The first JavaScript-versus-PyTorch check failed in 11 output comparisons, all in the parent's `skip_exchange` control. The new access path implements this control, but the original parent exchange method treats that unrecognized string as an ordinary intact exchange. The initial port applied skip behavior to both. The JavaScript parent path was changed to preserve the original source behavior. The repaired suite matches all 4,608 decisions. No weights, expected outputs, thresholds, or examples were changed. The initial failed record remains in `checks/port_validation_before_legacy_fix.json`. This mode is not offered in the live UI.

## 2. Missing bundled Playwright browser

Playwright's default cached Chromium executable was absent. The installed system `/usr/bin/chromium` was available and used explicitly. No browser download or installation was performed.

## 3. Managed Chromium file-URL restriction

Direct `file://` navigation returned `ERR_BLOCKED_BY_ADMINISTRATOR`. The test runner used the exact self-contained HTML through Playwright `set_content` instead. This exercised its scripts, controls, rendering, and downloads without external resource requests, but is not direct file-URL compatibility verification. Ordinary browser and mobile file-opening behavior can differ.

## 4. Mobile answer wrapping

Visual inspection found pair answers wrapping inside the two narrow model cards. Nonwrapping values and smaller mobile answer typography corrected the layout. A fixed mobile controls/results navigation strip was added and the UI suite was rerun.

## Remaining numerical and scientific limits

Inference has small floating-point differences from the original PyTorch implementation. Tested decisions agree; untested histories are not guaranteed to match near decision boundaries. No neural training or new scientific validation of J-space occurred during this interface build. All substantive research failures documented in the source v0.6 report remain in force.
