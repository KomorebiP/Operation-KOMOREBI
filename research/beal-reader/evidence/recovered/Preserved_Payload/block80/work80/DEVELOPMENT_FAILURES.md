# Development failures and corrected claims

1. Initial primary input validation required the old ordinary logarithm generator
   to generate the ENTIRE finite multiplicative field group. It only needs to
   generate its seventh-power quotient; the retained Block79 generator has exactly
   that property. The run raised "bad ordinary primitive" before producing its
   certificate. The check was corrected to g^((Q-1)/7)!=1, without changing the
   inherited generator or any residue normalization. Rejected source is retained
   in development/rejected_full_primitive_check.py.txt. Both final arithmetic
   implementations subsequently passed and agreed.
2. A later exploratory inspection expected the old base fixture to contain the
   three degree-two columns and raised StopIteration. Those columns have their
   separate inherited normalization. The Block68 degree-two proof is now copied
   and hash-pinned directly; build_inputs verifies its literal generator entries.
   This inspection failure produced no scientific output.
3. The first new wrapper syntax check found a missing space in "else3". No
   scientific job was launched by that wrapper. The rejected source is retained
   in development/rejected_verifier_syntax.py.txt. The corrected wrapper compiles.
4. A guessed mathematical PDF endpoint was unavailable and broad source searches
   returned unrelated items. The author-maintained book index supplied the exact
   ADT second-edition PDF; the needed pages were then inspected directly. No
   conclusion or source credit comes from failed probes. No local PDF cache is
   claimed.

Mathematical nonclosure: the new restricted primitive theorem does not establish
geometric local compatibility. No actual affine target was available for evaluation.
Synthetic image and nonimage targets check the operator and prevent declaring the
zero homogeneous vector an actual affine origin. These are linear-algebra controls,
not arithmetic counterexamples. All upstream failures remain in the original ZIP.
