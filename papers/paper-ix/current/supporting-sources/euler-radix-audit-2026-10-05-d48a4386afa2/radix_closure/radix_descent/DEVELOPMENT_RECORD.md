# Development record

The first runner invocation was rejected before running the checker: execution_artifacts listed only the script while --input also listed the inherited coefficient JSON. The contract was corrected to declare both immutable execution inputs. No mathematical output was produced by the rejected invocation.

The checker was then extended with the stronger one-coefficient construction. Its final manifest supersedes the earlier completed run, which remains as development history because the current checker includes the additional test.

The one-coefficient checker received one additional independent consistency check: its source Taylor coefficients0 and1 must equal the separately computed rational/logarithmic source value and derivative. certified_run_reviewed is the current manifest; the earlier final-named run is superseded by this source revision.
