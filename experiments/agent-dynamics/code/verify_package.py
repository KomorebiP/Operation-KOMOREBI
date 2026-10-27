"""Check the frozen delivered snapshot. Regeneration may overwrite these files."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    inventory=json.loads((ROOT/'SHA256SUMS.json').read_text(encoding='utf-8'))
    errors=[]
    for name,expected in inventory.items():
        path=(ROOT/name).resolve()
        if not path.is_relative_to(ROOT):
            errors.append(f'Unsafe relative path: {name}')
        elif not path.is_file():
            errors.append(f'Missing: {name}')
        elif hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            errors.append(f'Changed: {name}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(inventory)} files match the frozen snapshot.')
