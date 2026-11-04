"""Build a private, fixed-source Conventions handoff diagnostic.

Each explicit run checks either the original or a deliberately false final target.
The receiver is closed immediately after that target; no public loader is changed.
"""
import argparse
import json
from pathlib import Path
import subprocess

from lean_browser import verify_runtime
from lean_checkpoint_probe import build as build_base, once, sha, serve, VERSION as BASE_VERSION

VERSION = '20261104-conventions-probe1'
ORIGINAL_ROOT = 'monographs/quantum-and-circuits/verification/quantum_fresh_20261026/fresh'
ORIGINALS = [
    ('QuantumArithmeticBridge', '087f1f22c465f910e343ae917d252b87717c1811f74492d219bc70894d8cc825'),
    ('FiniteFourier', 'f11757042bdda213f442659fd7649bb25cf3a79d49728db124c2a71741510f8f'),
    ('SemanticBridge', '2841b63adaa735e9ca50044407786a78710d36440267c9973e7bbc77c6b43af5'),
    ('Conventions', 'd6057793389c3ee66789caf78021fbcfc31f752db98601604373abfa564083a8'),
]
LIBRARIES = [
    ('Mathlib.Tactic.Positivity.Finset', '6aab775f8ff057ee93263e7ea22a5f2ec0f6b871bef39bd8e8821005820ba386'),
    ('Mathlib.Tactic.Positivity', '74549078792cb4bef7b904577b94f0e206912935507b6f2f39eb73b7a15927d6'),
]
FALSE_SUFFIX = '\nexample : (1 : Nat) = 2 := by rfl\n'


def pinned_inputs(repo, runtime, source):
    """Validate every producer/consumer before creating any output directory."""
    originals, libraries = [], []
    for module, expected in ORIGINALS:
        path = ORIGINAL_ROOT + '/' + module + '.lean'
        raw = (repo / path).read_bytes()
        if sha(raw) != expected:
            raise ValueError('Fixed original Conventions source changed: ' + path)
        originals.append(dict(module=module, path=path, source=raw.decode('utf8'), size=len(raw), sha256=expected))
    for module, expected in LIBRARIES:
        path = 'lean-mathlib/sources/' + module.replace('.', '/') + '.lean'
        row = source['mathlib_source_modules'][module]
        raw = (runtime / path).read_bytes()
        if row['module'] != module or row['asset'] != path or row['sha256'] != expected or sha(raw) != expected or row['source'] != raw.decode('utf8') or row['size'] != len(raw):
            raise ValueError('Pinned Conventions source library changed: ' + module)
        libraries.append(dict(module=module, path=path, source=raw.decode('utf8'), size=len(raw), sha256=expected))
    return originals, libraries


def build(runtime, output, node='node'):
    runtime, output = runtime.resolve(), output.resolve()
    if output.exists() or runtime == output or runtime in output.parents:
        raise ValueError('Use a new output directory outside the runtime')
    repo = Path(__file__).resolve().parents[1]
    source = verify_runtime(runtime)
    originals, libraries = pinned_inputs(repo, runtime, source)
    graph = build_base(runtime, output, node)
    wasm = output / 'assets/lean-wasm'
    support = repo / 'tools/fixtures/lean_checkpoint'
    good, bad = originals[-1]['source'], originals[-1]['source'] + FALSE_SUFFIX
    fixture = (wasm / 'fixture.js').read_text(encoding='utf8').split('export const MODULE=')[0]
    for name, value in [('A_SOURCES', originals[:3]), ('B_SOURCES', libraries), ('CONSUMER_GOOD', good), ('CONSUMER_FALSE', bad)]:
        fixture += '\nexport const ' + name + '=' + json.dumps(value) + ';\n'
    fixture += 'export const MODULE=A_SOURCES[0].module,SOURCE=A_SOURCES[0].source;\n'
    (wasm / 'fixture.js').write_bytes(fixture.encode())
    program = 'const f=await import(' + json.dumps((wasm / 'fixture.js').as_uri()) + ');process.stdout.write(JSON.stringify([...f.A_SOURCES,...f.B_SOURCES].map(x=>f.moduleSource(x.source,x.module))));'
    wrapped = json.loads(subprocess.check_output([node, '--input-type=module', '-e', program]).decode())
    config = graph['config']
    config.update(scope='conventions-fixed-terminal-target-probe1', workspace='diagnostic-conventions-terminal-target-probe1', boundary=3, contract=VERSION,
                  modules=[dict(module=r['module'], sourceSha=r['sha256'], wrappedSha=sha(code.encode())) for r, code in zip(originals[:3], wrapped[:3])],
                  allowedSources=[sha(code.encode()) for code in wrapped + [good, bad]])
    del config['manifests']['lean-mathlib/workspaces/proof-path-compression.json']
    config['manifests']['lean-mathlib/real-analysis-layer.json'] = source['files']['lean-mathlib/real-analysis-layer.json']['sha256']
    (wasm / 'checkpoint-policy.js').write_bytes(('export const CHECKPOINT=' + json.dumps(config, sort_keys=True) + ';\n').encode())
    compiler = (wasm / 'compiler.js').read_text(encoding='utf8')
    for before, after in [
        ("optionalLayers(assets, 'workspaces/proof-path-compression.json')", 'optionalLayers(assets)'),
        ('let producerAttempted=false;', 'const producerAttempts=new Set();'),
        ('if (producerAttempted)', 'if (producerAttempts.has(checkpointEntry.module))'),
        ('producerAttempted=true;', 'producerAttempts.add(checkpointEntry.module);'),
        ('checkpointReceipts.size !== 1', 'checkpointReceipts.size !== 3'),
    ]:
        compiler = once(compiler, before, after)
    (wasm / 'compiler.js').write_bytes(compiler.encode())
    worker = (wasm / 'worker.js').read_text(encoding='utf8')
    worker = once(worker, "checkpointCompileCount !== 1 || checkpointExported) throw Error('Checkpoint export needs exactly one original producer compile.')",
                  "checkpointCompileCount !== 3 || checkpointExported) throw Error('Checkpoint export needs exactly three original producer compiles.')")
    worker = once(worker, 'for (const mb of [2048, 1536, 1024, 768])', 'for (const mb of [1024, 768])')
    (wasm / 'worker.js').write_bytes(worker.encode())
    codec = (wasm / 'checkpoint-codec.js').read_text(encoding='utf8')
    (wasm / 'checkpoint-codec.js').write_bytes(once(codec, 'exactly five probe parts', 'exactly fifteen probe parts').encode())
    for path in wasm.glob('*.js'):
        path.write_bytes(path.read_text(encoding='utf8').replace(BASE_VERSION, VERSION).encode())
        subprocess.run([node, '--check', str(path)], check=True, capture_output=True)
    (output / 'assets/checkpoint-control.js').write_bytes((support / 'heavy-control.js').read_text(encoding='utf8').replace('HEAVY_VERSION_HERE', VERSION).encode())
    html = output / 'lean/browser/checkpoint.html'
    html.write_bytes((support / 'heavy-probe.html').read_text(encoding='utf8').replace('HEAVY_VERSION_HERE', VERSION).encode())
    graph.pop('consumer_with_compatibility_sha256')
    graph.update(version=VERSION, config=config, bounds=dict(parts=15, per_part=16777216, total=67108864),
                 source_sha256=[r['sha256'] for r in originals[:3]], consumer_sha256=originals[-1]['sha256'], false_sha256=sha(bad.encode()),
                 source_inputs=[{k: r[k] for k in ('module', 'path', 'size', 'sha256')} for r in originals + libraries],
                 memory_trial=dict(requested_initial_mib=[1024, 768], artifact_limits_unchanged=True, measured='Initial allocation only, not growth, peak memory or physical reclamation.'),
                 scope='One explicit original OR false-edited final target run. Single-use issuance unchanged. Close receiver after final target. New imports may initialize again. No persistent cache, arbitrary initializer/state continuity, general compiler call limit, public support or parallel compiler claim.')
    graph['files'] = [dict(path=p.relative_to(output).as_posix(), size=p.stat().st_size, sha256=sha(p.read_bytes()))
                      for p in sorted((output / 'assets').rglob('*')) if p.is_file()]
    graph['files'].append(dict(path='lean/browser/checkpoint.html', size=html.stat().st_size, sha256=sha(html.read_bytes())))
    (output / 'lean/browser/checkpoint-graph.json').write_bytes((json.dumps(graph, indent=2) + '\n').encode())
    subprocess.run([node, '--check', str(output / 'assets/checkpoint-control.js')], check=True, capture_output=True)
    return graph


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--node', default='node')
    parser.add_argument('--serve', action='store_true')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    graph = build(args.runtime, args.output, args.node)
    print(json.dumps(dict(status='Prepared only; browser execution required', version=VERSION, assets=len(graph['files']))))
    if args.serve:
        serve(args.output, args.port)
