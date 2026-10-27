"""Fork, edit and undo a learned cubic signal. Author: Komorebi P."""
import json
import numpy as np
from cli import ROOT, load_bank

bank = load_bank(ROOT / 'results/workspaces_0.json')
bank.fork('rule_0', 'my_cubic')
q1, q2 = [[2., 1.]], [[1., 0.]]
before = bank.read('my_cubic', q1, q2)
receipt = bank.edit_amplitude('my_cubic', .5)
after = bank.read('my_cubic', q1, q2)
assert np.max(abs((after-before)[:, 0] - [4., 3.5, 4.5])) < 1e-6
bank.undo('my_cubic')
assert np.array_equal(bank.read('my_cubic', q1, q2), before)
destination = ROOT / 'examples/demo_workspaces.json'
bank.save(destination)
print(json.dumps({'author': 'Komorebi P.', 'readers': ['value', 'difference', 'sum'],
                  'before': before[:, 0].tolist(), 'after': after[:, 0].tolist(),
                  'change': (after-before)[:, 0].tolist(), 'edit': receipt,
                  'undo_restored_exactly': True, 'saved': str(destination)}, indent=2))
