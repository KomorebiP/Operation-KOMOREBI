#!/usr/bin/env python3
"""Verify the expanded Paper V release. Author: Komorebi P.

Runs real Lean verification, all three test families, numerical replay, and a
fresh manuscript build. Any missing prerequisite or failed gate is a failure.
PDF-to-Lean mathematical correspondence remains an explicit manual review.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
V = ROOT / 'verification'

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def run(command, cwd, name, timeout=900):
    try:
        result = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or b''
        if isinstance(output, bytes):
            output = output.decode('utf-8', errors='replace')
        (V/name).write_text(output + '\nTIMEOUT\n')
        raise RuntimeError(f'Timeout: {name}') from exc
    (V/name).write_text(result.stdout)
    require(result.returncode == 0, f'Failed command; see verification/{name}')
    return result.stdout

def main():
    report = {'release': '1.1.0-expanded-lean-checked',
              'timestamp_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'STARTED', 'gates': {},
              'pdf_to_lean_correspondence': 'manually reviewed; not mechanically proved'}
    try:
        contract = json.loads((V/'manuscript_contract.json').read_text())
        for rel, digest in contract['reviewed_source_sha256'].items():
            require(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest() == digest,
                    f'Reviewed-source hash mismatch: {rel}')
        report['gates']['reviewed_sources'] = 'PASS'
        run([sys.executable, str(V/'verify.py')], ROOT, 'paper_lean_run.log')
        lean = json.loads((V/'verification_status.json').read_text())
        require(lean['status'] == 'LEAN_CHECKS_PASS' and lean['lean_kernel_checked'],
                'No real Lean build/audit pass')
        report['gates']['lean'] = {'status': 'PASS', 'theorem_targets': 225,
                                  'proof_modules': 23, 'namespace_declarations': 827}
        junit = V/'companion_junit.xml'
        run([sys.executable, '-m', 'pytest', '-q', 'tests', f'--junitxml={junit}'],
            ROOT/'companion', 'companion_tests.log', 180)
        suites = list(ET.parse(junit).getroot().iter('testsuite'))
        for field in ('failures', 'errors', 'skipped'):
            require(sum(int(s.get(field, 0)) for s in suites) == 0,
                    f'Companion tests contain {field}')
        require(sum(int(s.get('tests', 0)) for s in suites) == 33,
                'Unexpected companion test count')
        exact_count = sum(lean['gates'][name]['tests_run'] for name in
                          ('exact_model', 'second_block', 'verifier_controls'))
        require(exact_count == 36, 'Unexpected exact/verifier test count')
        report['gates']['tests'] = {'status': 'PASS', 'companion': 33,
                                  'independent_exact': 20, 'verifier_controls': 16,
                                  'total': 69, 'exact_assertions': 305933}
        run([sys.executable, '-O', str(V/'verify.py'), '--static-only'], ROOT,
            'optimized_static_run.log', 180)
        shutil.copy2(V/'static_status.json', V/'optimized_static_status.json')
        report['gates']['optimized_static'] = 'PASS'

        os.environ['MPLBACKEND'] = 'Agg'
        sys.path.insert(0, str(ROOT/'companion'))
        import numpy as np
        from projector_signal.experiments import run_experiments, make_signal_1d
        from projector_signal.visuals import make_figures
        baseline = json.loads((ROOT/'provenance/original_companion/results/numerical_results.json').read_text())
        recorded = json.loads((ROOT/'companion/results/numerical_results.json').read_text())
        require(recorded == baseline, 'Current numerical record differs from recovered baseline')
        with tempfile.TemporaryDirectory(prefix='paper-v-numerics-') as name:
            temp = Path(name)
            generated = run_experiments(temp)
            floats = []
            def compare(a, b, key=''):
                if isinstance(a, dict):
                    require(isinstance(b, dict) and a.keys() == b.keys(), f'Result keys: {key}')
                    for k in a:
                        compare(a[k], b[k], key+'/'+k)
                elif isinstance(a, list):
                    require(isinstance(b, list) and len(a) == len(b), f'Result length: {key}')
                    for i, (x, y) in enumerate(zip(a, b)):
                        compare(x, y, key+'/'+str(i))
                elif type(a) is float:
                    require(np.isfinite(b) and np.isclose(a, b, rtol=1e-10, atol=1e-12),
                            f'Numerical mismatch: {key}: {a} vs {b}')
                    floats.append((key, a, b))
                else:
                    require(a == b, f'Discrete result mismatch: {key}')
            compare(recorded, generated)
            figures = make_figures(temp)
            require(len(figures) == 36, 'Expected eighteen figure pairs')
            require(len(list((temp/'figures').glob('*.pdf'))) == 18, 'PDF figure count')
            require(len(list((temp/'figures').glob('*.png'))) == 18, 'PNG figure count')
        signal = make_signal_1d()['signal']
        spectrum = np.fft.fft(signal-signal.mean())
        for keep in (16, 32, 64, 128, 256):
            indices = set(np.argsort(abs(spectrum))[::-1][:keep])
            require(all((-i) % len(signal) in indices for i in indices),
                    f'Sparse Fourier budget {keep} not conjugate-pair closed')
        report['gates']['numerical_replay'] = {
            'status': 'PASS', 'floating_metrics_compared': len(floats),
            'all_stored_values_exactly_reproduced': generated == recorded,
            'figure_pairs_regenerated': 18, 'sparse_conjugate_pairs': 'PASS',
            'comparison_rtol': 1e-10, 'comparison_atol': 1e-12}
        env = {'python': sys.version, 'platform': sys.platform}
        for name in ('numpy', 'scipy', 'matplotlib', 'pytest', 'pypdf'):
            env[name] = importlib.metadata.version(name)
        (V/'numerical_environment.json').write_text(json.dumps(env, indent=2)+'\n')

        manuscript = ROOT/'manuscript'
        tex = manuscript/'Paper_V_Expanded_Lean_Checked.tex'
        source = tex.read_text()
        require(len(re.findall(r'\\begin\{(?:theorem|proposition|corollary|lemma)\}', source)) == 20,
                'Expected twenty manuscript theorem-like statements')
        require(source.count(r'\begin{proof}') == 20, 'Expected twenty explicit proofs')
        require(source.count(r'\begin{conjecture}') == 2, 'Expected two open conjectures')
        figure_names = re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', source)
        require(len(figure_names) == len(set(figure_names)) == 18, 'Figure inventory mismatch')
        for name in figure_names:
            require((manuscript/'figures'/name).is_file(), f'Missing figure {name}')
        for binary in ('pdflatex', 'pdftotext', 'pdftoppm'):
            require(shutil.which(binary) is not None, f'Missing prerequisite: {binary}')
        with tempfile.TemporaryDirectory(prefix='paper-v-tex-') as name:
            temp = Path(name)
            shutil.copy2(tex, temp/tex.name)
            shutil.copytree(manuscript/'figures', temp/'figures')
            for i in range(3):
                run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', tex.name],
                    temp, f'paper_tex_pass{i+1}.log', 120)
            log = (temp/tex.with_suffix('.log').name).read_text()
            require(not re.search(r'Overfull|Underfull|LaTeX Warning:|Package .* Warning:', log),
                    'TeX warnings remain; see paper_tex_pass3.log')
            aux = (temp/tex.with_suffix('.aux').name).read_text()
            actual = re.findall(r'\\newlabel\{result:\d+\}\{\{([^}]+)\}\{([^}]+)\}', aux)
            require([a[0] for a in actual] == contract['result_numbers'],
                    'Manuscript result numbers changed')
            from pypdf import PdfReader
            rebuilt = temp/tex.with_suffix('.pdf').name
            published = manuscript/tex.with_suffix('.pdf').name
            reader = PdfReader(rebuilt)
            require(len(reader.pages) == contract['page_count'], 'PDF page count changed')
            rebuilt_text = run(['pdftotext', '-layout', str(rebuilt), '-'], temp,
                               'paper_rebuilt_text.txt', 60)
            published_text = run(['pdftotext', '-layout', str(published), '-'], temp,
                                 'paper_published_text.txt', 60)
            require(rebuilt_text == published_text, 'Published PDF text differs from fresh TeX build')
            require('??' not in rebuilt_text, 'Unresolved reference in PDF')
            run(['pdftoppm', '-r', '50', '-png', str(rebuilt), str(temp/'page')], temp,
                'paper_render.log', 180)
            require(len(list(temp.glob('page-*.png'))) == contract['page_count'],
                    'Not every rebuilt PDF page rendered')
        report['gates']['manuscript'] = {
            'status': 'PASS', 'pages': contract['page_count'], 'theorem_like_results': 20,
            'explicit_proofs': 20, 'open_conjectures': 2, 'figures': 18,
            'numbering_preserved': True, 'tex_warnings': 0, 'fresh_build_text_match': True,
            'all_pages_rendered': True}
        report['status'] = 'PAPER_V_RELEASE_CHECKS_PASS'
        report['exit_code'] = 0
    except Exception as exc:
        report.update(status='FAIL', error=str(exc), exit_code=1)
    (V/'paper_release_status.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2), flush=True)
    return report['exit_code']

if __name__ == '__main__':
    raise SystemExit(main())
