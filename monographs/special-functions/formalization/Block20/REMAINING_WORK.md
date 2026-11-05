# Remaining work after SF-LEAN-B20

The selected arithmetic lowering is checked against a typed interpreter for all
values in its source-variable profiles. The statement/control template and the
faithfulness of Python AST selection/data emission remain trusted. The next
structural task is an explicit interpreter or verified lowering for the same
six-function statement fragment, preserving mutation, conversion ordering and
exceptions. The existing Block19 operational theorem remains its target.

Do not label the result a verified general Python compiler. CPython/Fraction/
stdlib internals, exact validation-exception object identity and unexpected
machine failures remain outside scope. Retain other J/F/H, I and A-E obligations,
conditional ordinary type convergence and G.2's nonzero-defect guard.
