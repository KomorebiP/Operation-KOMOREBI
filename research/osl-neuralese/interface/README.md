# Finite semantic checkpoint interface

This newly authored module is an exact finite reference demonstration. It is **not a learned Neuralese decoder**.

`FiniteMachine` specifies the entire deterministic transition table and observation function (1–256 states, 1–32 actions). `make_certificate` performs partition refinement. `verify_certificate` independently checks the local observation and transition equations, accepting a sound quotient even when it is not minimal. The table and observation function are trust roots.

`checkpoint` serializes a quotient class with exact source, certificate, and scope binding. `restore` validates those bindings. The hashes do not authenticate a principal or detect a consistently rehashed lie about which valid class was historically visited. `quotient_step` only executes declared operations.

The demonstration uses D4's eight semantic states plus a private bit. The private bit is removable because no declared operation makes it visible. Adding a new operation or observation invalidates the old scope. The mathematical induction is in the OSL manuscript.

```text
python -m unittest discover -s tests -v
python run_demo.py --output ../../local_demo
```

Run these from `interface/`. For the second command, the neighboring `OSL/core05` source is needed. It produces two actual OSL executions. The valid finite evidence path is admitted; the absent-certificate path remains provisional and quarantined. Both paths are checked. All effects are symbolic; no external action is authorized or executed.
