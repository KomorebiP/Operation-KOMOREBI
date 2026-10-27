Python computation evidence and reproduction

The two recorded manifests preserve the original commands, bounded claims,
inputs, observed software versions, outputs and run limits. Their source paths
refer to the execution workspace used for this release. The original small
wrappers are preserved unchanged in provenance/. They assume that original
layout and are not entrypoints to run in place here.

provenance/INPUT_PATH_MAP.json maps every original execution input to an exact
byte-identical file in this release. Original python-examples/ inputs are now
under editable/traditional/. Original python-companion/code/ inputs are now
under code/. The original verification script is preserved in
recorded_companion/artifact/scripts/verify_python.py.

Direct reproduction

Use a disposable copy of the unpacked release, because these commands create
new results and change checksums. From that copy's root, with Python 3.12
(the accepted run used 3.12.14):

  python3.12 -m venv .venv
  .venv/bin/python -m pip install -r code/python/requirements.lock.txt
  .venv/bin/python editable/traditional/visual_checks/verify_examples.py
  PYTHONPATH=code/python .venv/bin/python -m pytest -q -W error -p no:cacheprovider --import-mode=importlib code/python/tests
  .venv/bin/python code/python/run_all.py

The exact visual checker writes its new receipt beside its source. The test
command runs the 33 companion tests with warnings fatal. run_all.py regenerates
results/ and ten PDF/PNG figure pairs under paper/figures/. These commands are
documented reproduction commands, not additional execution evidence.

Accepted results: 96 exact finite/symbolic assertions, 33 tests, and ten
regenerated PDF/PNG pairs. See the manifests for finite ranges, tolerances,
random seeds and limits. These checks do not prove universal mathematical
claims or formally verify the Python implementation.
