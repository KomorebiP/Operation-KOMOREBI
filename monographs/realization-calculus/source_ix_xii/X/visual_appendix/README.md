# Paper X visual guide: current edition

The 33-page guide contains a cover, two current-scope pages, and thirty worked
atlas pages labeled V1–V30. The same thirty pages occur at PDF pages 61–90 of
the monograph. This deliberate duplication is one atlas, not two independent
mathematical additions.

`source/models.py` supplies the exact finite models. The inherited
`checks/verify_examples.py` checks 263 positive assertions and rejects 14 false
controls. `source/generate_graphics.py` supplies deterministic TikZ plates.
`source/pages.tex` is the editable exposition. No image generator or font binary
is distributed. The examples do not constitute new universal arithmetic proofs.

Run the current coordinated builder from the package root:

```bash
python publication/build_publication.py
python publication/validate_publication.py
python verification/run_checks.py --output ../paper_x_replay
```

The coordinated builder resolves current TeX labels and appends the atlas after
building the traditional text. Use it rather than the older `build.py`, which is
retained as a historical entry point and expects its original workspace layout.

The active record is inherited conditional 20/20. Historical Block 27 and
scalar/Mellin descriptions of 17/20 remain dated evidence of their revisions.
The later stronger 19/20 attempt is not a retraction of the checked source.
The final page distinguishes all three contracts and their assumptions.
