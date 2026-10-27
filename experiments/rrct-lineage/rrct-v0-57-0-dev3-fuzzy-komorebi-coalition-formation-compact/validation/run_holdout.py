from __future__ import annotations
import json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
seeds=json.loads((ROOT/'validation/HOLDOUT_SEED_SELECTION.json').read_text())['holdout_seeds']
for seed in seeds:
    for variant in ('fuzzy','hard','direct','crystal'):
        output=ROOT/f'results/holdout/{variant}_{seed}.json'
        if output.exists():
            continue
        subprocess.run([sys.executable,str(ROOT/'validation/train_holdout_one.py'),variant,str(seed)],check=True,cwd=ROOT)
