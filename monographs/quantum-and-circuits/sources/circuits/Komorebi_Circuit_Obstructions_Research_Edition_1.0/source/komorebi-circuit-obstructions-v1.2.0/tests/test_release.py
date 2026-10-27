"""Small exact controls for the closed release. No third-party packages."""
from __future__ import annotations
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'checks'))
from reversible import (one, variables, degree, validate, trace, monomial_oracle,
                        compile_source, check_circuit)
from truth_tables import profile, affine_masks
from verify_completeness import optimal_small
from verify_projection import full_oracle, q_oracle, gf2rank
from verify_fingerprint import M, anf, weights, evaluate, extract


class BooleanControls(unittest.TestCase):
    def test_truth_table_convention(self):
        self.assertEqual(variables(2), [0b1010, 0b1100])
        self.assertEqual(one(2), 15)
        self.assertEqual(degree(0, 2), -1)
        self.assertEqual(degree(0b1000, 2), 2)
        self.assertEqual(degree(0b0110, 2), 1)

    def test_profiles_against_supported_enumeration(self):
        count = 0
        for n in range(1, 4):
            for f in range(1 << (1 << n)):
                local = [n + 1] * (1 << n)
                sub = f
                while sub:
                    d = degree(sub, n)
                    for v in range(1 << n):
                        if sub >> v & 1:
                            local[v] = min(local[v], d)
                    sub = (sub - 1) & f
                ds = [local[v] for v in range(1 << n) if f >> v & 1]
                self.assertEqual(profile(f, n), (min(ds), max(ds)) if ds else (0, 0))
                count += 1
        self.assertEqual(count, 276)

    def test_affine_masks(self):
        for n in range(1, 5):
            masks = affine_masks(n)
            self.assertEqual(len(set(masks)), 1 << (n + 1))
            self.assertTrue(all(degree(f, n) <= 1 for f in masks))

    def test_small_optimal_oracles(self):
        counts = {0: 0, 1: 0, 3: 0}
        for n in range(1, 4):
            vs, mask = variables(n), one(n)
            for f in range(1 << (1 << n)):
                ops, width, y, t = optimal_small(f, n)
                validate(ops, width)
                self.assertEqual(sum(g[0] == 'T' for g in ops), t)
                bstar = max(profile(f ^ ell, n)[1] for ell in affine_masks(n))
                self.assertEqual(t, max(0, degree(f, n) - 1, 2 * bstar - 3))
                for bit in (0, 1):
                    start = vs + [0] * (width - n)
                    start[y] = bit * mask
                    want = start.copy()
                    want[y] ^= f
                    self.assertEqual(trace(ops, start, mask)[-1], want)
                counts[t] += 1
        self.assertEqual(counts, {0: 28, 1: 120, 3: 128})

    def test_illegal_gates_rejected(self):
        for ops, width in [([('T', 0, 0, 1)], 2), ([('C', 0, 0)], 1),
                           ([('T', 0, 1, 3)], 3), ([('X', 0)], 2),
                           ([('N', -1)], 2)]:
            with self.assertRaises(AssertionError):
                validate(ops, width)

    def test_repeated_source_operands(self):
        for operation in ('AND', 'OR'):
            ops, width, y = compile_source(1, [(operation, 0, 0)], 1)
            validate(ops, width)
            self.assertFalse(any(g[0] == 'T' for g in ops))
            for x in (0, 1):
                for bit in (0, 1):
                    state = [x] + [0] * (width - 1)
                    state[y] = bit
                    wanted = state.copy()
                    wanted[y] ^= x
                    self.assertEqual(trace(ops, state, 1)[-1], wanted)

    def test_monomials_and_active_cut(self):
        for n in range(2, 7):
            ops, width, y = monomial_oracle(n)
            f = 1 << ((1 << n) - 1)
            _, _, t = check_circuit(n, ops, width, y, f, n)
            self.assertEqual(t, 2 * n - 3)
        ops, width, y = monomial_oracle(3)
        detour = [('T', y, 0, 3), ('T', y, 0, 3)]
        dirty = ops[:1] + detour + ops[1:]
        check_circuit(3, dirty, width, y, 1 << 7, 3)

    def test_unbalanced_family_breaks_extrapolation(self):
        n = 5
        f = sum((bool(x & 1 and x & 2) or x >> 2 == 7) << x for x in range(32))
        profiles = [profile(f ^ ell, n) for ell in affine_masks(n)]
        self.assertEqual(max(a for a, _ in profiles), 3)
        self.assertEqual(max(b for _, b in profiles), 4)

    def test_projection_changes_cost_and_safety(self):
        m, a = 3, 7
        labels = list(range(1, a))
        n, vs = len(labels), variables(len(labels))
        ls = []
        for j in range(m):
            val = 0
            for i, label in enumerate(labels):
                if label >> j & 1:
                    val ^= vs[i]
            ls.append(val)
        f = one(n)
        for val in ls:
            f &= val
        q = 0
        for i, u in enumerate(labels):
            for j, v in enumerate(labels):
                if i < j and u ^ v == a:
                    q ^= vs[i] & vs[j]
        self.assertNotEqual(q & (~f & one(n)), 0)
        self.assertEqual((degree(f, n), degree(q, n)), (3, 2))
        for ops, width, y, fn in [(*full_oracle(m, labels), f), (*q_oracle(labels, a), q)]:
            for bit in (0, 1):
                state = vs + [0] * (width - n)
                state[y] = bit * one(n)
                want = state.copy()
                want[y] ^= fn
                self.assertEqual(trace(ops, state, one(n))[-1], want)
        self.assertEqual(gf2rank([2, 1]), 2)

    def test_weighted_overlap_counterexample(self):
        z = [2]
        self.assertEqual(evaluate(0b10, weights(z)), 2)
        self.assertEqual(evaluate(0b01, weights(z)), 1)
        self.assertEqual(M[2][1], 2)
        self.assertEqual(extract(anf(0, 1), z), 0)

    def test_small_weighted_extraction(self):
        for f in range(16):
            for a in range(4):
                for b in range(4):
                    self.assertEqual(extract(anf(f, 2), [a, b]), evaluate(f, weights([a, b])))


class RepositoryControls(unittest.TestCase):
    def test_claim_contract(self):
        data = json.loads((ROOT / 'docs/claims.json').read_text(encoding='utf-8'))
        self.assertEqual([c['id'] for c in data['active_claims']], [f'C{i:02}' for i in range(1, 9)])
        for claim in data['active_claims']:
            self.assertTrue((ROOT / claim['proof_file']).is_file())
            for field in ('statement', 'status', 'finite_scope', 'boundary'):
                self.assertTrue(claim[field])
        release = json.loads((ROOT / 'RELEASE.json').read_text(encoding='utf-8'))
        self.assertEqual(release['scope'], 'closed')
        self.assertEqual(release['research_completion_blockers'], [])

    def test_flat_imports(self):
        for path in (ROOT / 'checks').glob('*.py'):
            self.assertNotIn("sys.path.insert(0,str(R/'predecessor", path.read_text(encoding='utf-8'))

    def test_markdown_local_links(self):
        files = [*ROOT.glob('*.md'), *(ROOT / 'docs').glob('*.md'), ROOT / 'archive/README.md']
        checked = 0
        for path in files:
            text = re.sub(r'```.*?```', '', path.read_text(encoding='utf-8'), flags=re.S)
            for target in re.findall(r'\]\(([^)]+)\)', text):
                target = target.split('#', 1)[0]
                if not target or '://' in target or target.startswith('mailto:'):
                    continue
                self.assertTrue((path.parent / target).exists(), f'{path.name}: {target}')
                checked += 1
        self.assertGreaterEqual(checked, 15)


class LauncherControls(unittest.TestCase):
    def test_optimized_python_rejected(self):
        import subprocess
        result = subprocess.run([sys.executable, '-O', str(ROOT / 'scripts/verify.py'), '--quick'],
                                cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 2)
        self.assertIn('optimized Python', result.stderr)

    def test_archive_traversal_rejected(self):
        import tempfile
        import zipfile
        sys.path.insert(0, str(ROOT / 'scripts'))
        from verify import extract_safe
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            bad = folder / 'bad.zip'
            with zipfile.ZipFile(bad, 'w') as z:
                z.writestr('../escaped.txt', 'not allowed')
            with self.assertRaises(ValueError):
                extract_safe(bad, folder / 'destination')
            self.assertFalse((folder / 'escaped.txt').exists())

    def test_integrity_detects_mutation(self):
        import tempfile
        sys.path.insert(0, str(ROOT / 'scripts'))
        from check_integrity import verify
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            (folder / 'integrity').mkdir()
            (folder / 'code.py').write_text('changed', encoding='utf-8')
            (folder / 'integrity/SOURCE_SEAL.json').write_text(
                json.dumps({'files': {'code.py': '0' * 64}}), encoding='utf-8')
            with self.assertRaises(ValueError):
                verify(folder)


if __name__ == '__main__':
    unittest.main(verbosity=2)
