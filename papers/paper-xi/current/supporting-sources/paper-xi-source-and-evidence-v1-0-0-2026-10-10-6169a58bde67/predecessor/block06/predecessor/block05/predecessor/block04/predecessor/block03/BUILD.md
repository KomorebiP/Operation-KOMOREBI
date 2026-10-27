# Building and replaying the Block03 checkpoint

Python 3.11 or later is suitable for the delivered scripts. The nine arithmetic/model gates use the standard library only. Building the mathematical continuation requires XeLaTeX, its ordinary math/graphics packages, and installed URW Base35/OpenType, Nimbus Sans and DejaVu Sans Mono fonts. The Linux paths in the inherited style are explicit. No font files are redistributed. For another operating system, adapt the style to installed equivalents before building.

The PDF assembly/review tools require PyMuPDF and Pillow. The versions used here are recorded in verification/block03/ENVIRONMENT.json. Install them with your normal package manager where needed.

From the checkpoint root:

```sh
python tools/verify_package.py
python tools/replay_block03.py --output ../replay03
python tools/build_block03.py --output ../build03
python tools/assemble_reader.py --continuation ../build03/Paper_XI_Conjecture66_Block03.pdf --output ../reader03
```

Always keep output outside the package: strict integrity checking rejects added files. To fit short execution windows, split the replay with --only. Gate names are listed in verification/block03/REPLAY_SUMMARY.json. The recorded tests are finite illustrations and selected exact arithmetic, not proof of Conjecture66 or a Lean build.

The supplied cumulative reader is an assembly of a preserved 33-page B02 PDF, a new editable continuation, and a map. The unavailable B02 source is not reconstructed by the build. The original three core readers are unchanged baselines.
