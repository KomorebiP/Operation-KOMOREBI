# Restoration transport continuation

Read `RESEARCH_NOTE.md` for the mathematical statements and `AUDIT.md` for corrections and limitations.

Run all finite controls, including the output-redirection-only historical replay:

```bash
python checks/run_all.py
```

Python's standard library is sufficient. This run produces `results/COMPUTATION_MANIFEST.json`, scientific JSON files and logs. All default output paths are relative to this extracted project.

The original objective is P versus NP. It is not resolved. The actual results include a constant-factor protected-output normal form, a two-sided degree/restoration theorem, a full-degree NP-complete graph family, and an exact midpoint decoding identity. The obtained circuit lower bounds are linear.

Historical scripts are retained as evidence, not as the default verification route. No font files or third-party code are included.
