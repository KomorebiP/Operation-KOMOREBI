# Reporting correction

On 9 October 2026, the first reporting-collector invocation failed before writing a summary because it looked for `input_provenance` in a version 2 manifest. The actual runner schema names that field `input_artifacts`. The collector was corrected to read the supplied schema, then rerun with all manifest validations enabled.

No scientific replay failed, and no historical source or scientific result was changed by this reporting error. The correction concerns the evidence inventory only.
