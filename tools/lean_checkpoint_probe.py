"""Build a separate fixed-source browser checkpoint qualification probe.

No public loader or source is modified. This is not a persistent cache API.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from lean_browser import verify_runtime
from lean_workspaces import COMPRESSION, RECOVERY, COMPAT_SOURCE

VERSION = '20261104-checkpoint-probe1'
SOURCE_SHA = 'b12eac584bfddf459c54e882191623de2007d73824db84e51fb38d82756d07b9'
CONSUMER_SHA = 'ab689304f37b09092620f9a82a523f51612f8b5ba652d15a333cc4c2221ba3d2'


def sha(raw): return hashlib.sha256(raw).hexdigest()


def once(text, before, after):
    if text.count(before) != 1:
        raise ValueError('Probe adapter no longer matches the production loader: ' + before[:90])
    return text.replace(before, after)


def build(runtime, output, node='node'):
    repo = Path(__file__).resolve().parents[1]
    support = repo / 'tools/fixtures/lean_checkpoint'
    runtime, output = runtime.resolve(), output.resolve()
    if output.exists() or runtime == output or runtime in output.parents:
        raise ValueError('Use a new output directory outside the runtime')
    source = verify_runtime(runtime)
    raw = (repo / COMPRESSION).read_bytes()
    consumer = (repo / RECOVERY).read_bytes()
    if sha(raw) != SOURCE_SHA or sha(consumer) != CONSUMER_SHA:
        raise ValueError('The fixed original Proof Path sources changed')
    output.mkdir(parents=True)
    assets, out = output / 'assets', output
    wasm = assets / 'lean-wasm'
    shutil.copytree(repo / 'website/assets/lean-wasm', wasm)
    shutil.copytree(runtime, out / 'lean/browser/engine')
    shutil.copyfile(repo / 'website/assets/lean-browser-sw.js', out / 'lean/browser/sw.js')
    suffix, version = '', VERSION
    browser_source = (repo / 'website/assets/lean-browser.js').read_text(encoding='utf8')
    wrapper = browser_source[browser_source.index('export function moduleSource('):browser_source.index('export function outcome(')]
    fixture = "import {sourceHeader} from './roots.js';\n" + wrapper
    fixture += browser_source[browser_source.index('export function withCompatibility('):browser_source.index('export function withCompatibilityImport(')]
    fixture += '\n'.join('export const ' + key + '=' + json.dumps(value) + ';' for key,value in
        [('MODULE','ProofPath.Compression'),('SOURCE',raw.decode()),('CONSUMER_SOURCE',consumer.decode()),('COMPATIBILITY',COMPAT_SOURCE)])
    fixture += '\nexport const CONSUMER_GOOD=withCompatibility(CONSUMER_SOURCE,COMPATIBILITY);\n'
    fixture += 'export const CONSUMER_FALSE=CONSUMER_GOOD+"\\nexample : (1 : Nat) = 2 := by rfl\\n";\n'
    (wasm / 'fixture.js').write_bytes(fixture.encode())
    program = 'const f=await import(' + json.dumps((wasm / 'fixture.js').as_uri()) + ');process.stdout.write(JSON.stringify([f.moduleSource(f.SOURCE,f.MODULE),f.CONSUMER_GOOD,f.CONSUMER_FALSE]));'
    wrapped,good,bad = json.loads(subprocess.check_output([node,'--input-type=module','-e',program]).decode())
    modules=[dict(module='ProofPath.Compression',sourceSha=SOURCE_SHA,wrappedSha=sha(wrapped.encode()))]
    manifest_keys=['lean-wasm/core-layer.json','lean-mathlib/workspaces/proof-path-compression.json',
                   'lean-lib/Lean-layer.json','lean-lib/Std-layer.json','lean-lib/Batteries-layer.json']
    frontend_path = repo / 'website/assets/lean-wasm/frontend-check.js'
    config=dict(scope='proof-path-fixed-source-five-part-probe1',workspace='diagnostic-proof-path-probe1',boundary=1,
        contract=VERSION,requiredRoots=['Mathlib','Lean','Std','Batteries'],
        allowedSources=[sha(code.encode()) for code in [wrapped,good,bad]],
        engineSourceSha=sha((runtime/'SOURCE.json').read_bytes()),lean=source['lean'],mathlib=source['mathlib'],mathlibArchiveSha=source['mathlib_source_sha256'],
        wasmTransferSha=source['remote_files']['lean-wasm/lean.wasm.gz']['sha256'],glueSha=source['remote_files']['lean-wasm/lean.js']['sha256'],
        frontendSha=sha(frontend_path.read_bytes()),wrapperSha=sha(wrapper.encode()),
        manifests={key:source['files'][key]['sha256'] for key in manifest_keys},modules=modules,
        corePacks={key:row['sha256'] for key,row in source['remote_files'].items() if key.startswith('lean-wasm/core-lib/')})
    (wasm/'checkpoint-policy.js').write_bytes(('export const CHECKPOINT='+json.dumps(config,sort_keys=True)+';\n').encode())
    (wasm/'checkpoint-codec.js').write_bytes((support/'codec.js').read_bytes())
    (wasm/'frontend-check.js').write_bytes(frontend_path.read_bytes())

    worker = (repo / 'website/assets/lean-wasm/worker.js').read_text(encoding='utf8')
    snippet = (support / 'worker.js.inc').read_text(encoding='utf8')
    worker = once(worker, 'function mkdirp(FS, path) {', snippet + '\nfunction mkdirp(FS, path) {')
    worker = once(worker, 'let compileBusy = false;', 'let compileBusy = false;\nlet checkpointCompileCount = 0;\nlet checkpointExported = false;')
    worker = once(worker, '  compileBusy = true;\n  const t0', '  compileBusy = true;\n  checkpointCompileCount++;\n  const t0')
    worker = once(worker, '  const response = await fetch(`${assetBase}/core-layer.json`);\n  if (!response.ok) throw new Error(`core-layer.json: HTTP ${response.status}`);\n  const manifest = await response.json();', '  const manifest = await checkpointReadManifest(`${assetBase}/core-layer.json`);')
    worker = once(worker, '  const response = await fetch(manifestUrl);\n  if (!response.ok) throw new Error(`${label}: manifest HTTP ${response.status}`);\n  const manifest = await response.json();', '  const manifest = await checkpointReadManifest(manifestUrl);')
    core_start = worker.index('async function loadLibrary() {')
    core_end = worker.index('\n}\n', core_start) + 2
    core_loader = worker[core_start:core_end]
    core_loader = once(core_loader, '    await verifyPackHash(pack, bytes, signal);', '''    await verifyPackHash(pack, bytes, signal);
        const codec = await checkpointCodec(), key = 'lean-wasm/core-lib/' + pack.file;
        const digest = await codec.sha256(bytes);
        if (codec.CHECKPOINT.corePacks[key] !== digest) throw Error('Checkpoint pinned core pack mismatch: ' + key);
        checkpointCorePacks.set(key, digest);''')
    worker = worker[:core_start] + core_loader + worker[core_end:]
    wasm_start = worker.index('async function loadWasmUrl(script) {')
    wasm_end = worker.index('\n}\n', wasm_start) + 2
    wasm_loader = worker[wasm_start:wasm_end]
    wasm_loader = once(wasm_loader, '    let bytes = new Uint8Array(await response.arrayBuffer());\n    if (bytes[0]', '    let bytes = new Uint8Array(await response.arrayBuffer());\n    checkpointMeasured.wasmTransfer = await (await checkpointCodec()).sha256(bytes);\n    if (bytes[0]')
    worker = worker[:wasm_start] + wasm_loader + worker[wasm_end:]
    worker = once(worker, '          script.source = prepared.source;\n          bytes = prepared.bytes;', '''          script.source = prepared.source;
              bytes = prepared.bytes;
              checkpointMeasured.applied = true;
              const codec = await checkpointCodec();
              checkpointMeasured.wasmTransformed = await codec.sha256(bytes);
              checkpointMeasured.glueTransformed = await codec.textHash(script.source);''')
    worker = once(worker, "    return { source: new TextDecoder().decode(bytes), layout, transferBytes, decodedBytes: bytes.length };", "    checkpointMeasured.glueOriginal = await (await checkpointCodec()).sha256(bytes);\n    return { source: new TextDecoder().decode(bytes), layout, transferBytes, decodedBytes: bytes.length };")
    rpc = '''  if (checkpointInvalid && msg.type !== 'dispose' && msg.type !== 'blob_url') {
        const error='Checkpoint worker was invalidated.';
        if (msg.type === 'compile') post({type:'result',id:msg.id,success:false,error});
        else if (msg.type === 'checkpoint_export' || msg.type === 'checkpoint_install') post({type:'checkpoint_error',id:msg.id,error});
        else post({type:'error',data:error});
        return;
      }
      if (checkpointPhase) {
        checkpointInvalid = true;
        moduleReady = false;
        post({type: 'error', data: 'Checkpoint transaction overlapped another runtime operation.'});
        return;
      }
      if (msg.type === 'checkpoint_export' || msg.type === 'checkpoint_install') {
        checkpointPhase = true;
        try {
          if (msg.type === 'checkpoint_export') {
            if (checkpointCompileCount !== 1 || checkpointExported) throw Error('Checkpoint export needs exactly one original producer compile.');
            const capsule = await exportCheckpoint(msg);
            if (!moduleReady) throw Error('Checkpoint transaction was invalidated.');
            checkpointExported = true;
            self.postMessage({type: 'checkpoint_exported', id: msg.id, capsule}, capsule.parts.map(part => part.bytes.buffer));
          } else {
            if (checkpointCompileCount !== 0) throw Error('Checkpoint install requires a new worker before any source compile.');
            const installed = await installCheckpoint(msg);
            if (!moduleReady) throw Error('Checkpoint transaction was invalidated.');
            post({type: 'checkpoint_installed', id: msg.id, ...installed});
          }
        } catch (error) {
          checkpointInvalid = true;
          moduleReady = false;
          post({type: 'checkpoint_error', id: msg.id, error: String(error.message || error)});
        } finally { checkpointPhase = false; }
        return;
      }
    '''
    worker = once(worker, '  const msg = event.data || {};\n', '  const msg = event.data || {};\n' + rpc)
    (wasm / f'worker{suffix}.js').write_bytes(worker.encode())

    runtime = (repo / 'website/assets/lean-wasm/runtime.js').read_text(encoding='utf8')
    runtime = "import {validateCapsule} from './checkpoint-codec.js';\n" + runtime
    runtime, n = re.subn(r"\./worker\.js\?v=[^']+", f'./worker{suffix}.js?v={version}', runtime)
    assert n == 1
    runtime = once(runtime, 'function post(message) {', 'function post(message, transfers = []) {')
    runtime = once(runtime, 'worker.postMessage(message);', 'worker.postMessage(message, transfers);')
    runtime = once(runtime, 'hostOwnsBlobUrls: true })', "hostOwnsBlobUrls: true, checkpointCodecUrl: new URL('./checkpoint-codec.js', import.meta.url).href })")
    runtime = once(runtime, 'async function request(message, match, label, timeoutMs) {', 'async function request(message, match, label, timeoutMs, transfers = []) {')
    runtime = once(runtime, '\t\t\tpost(message);', '\t\t\tpost(message, transfers);')
    runtime_rpc = '''  async function exportCheckpoint(session, receipts) {
        try {
          const id = nextId++;
          const reply = await request({type: 'checkpoint_export', id, session, receipts}, msg => (msg.type === 'checkpoint_exported' || msg.type === 'checkpoint_error') && msg.id === id, 'Exporting checked module artifacts', 120000);
          if (reply.error) throw Error(reply.error);
          await validateCapsule(reply.capsule, session);
          return reply.capsule;
        } catch (error) { await dispose(); throw error; }
      }
      async function installCheckpoint(capsule, session) {
        try {
          await validateCapsule(capsule, session);
          const id = nextId++;
          const reply = await request({type: 'checkpoint_install', id, session, capsule}, msg => (msg.type === 'checkpoint_installed' || msg.type === 'checkpoint_error') && msg.id === id, 'Installing checked module artifacts', 120000, capsule.parts.map(part => part.bytes.buffer));
          if (reply.error) throw Error(reply.error);
          return reply;
        } catch (error) { await dispose(); throw error; }
      }
    '''
    runtime = once(runtime, '\tasync function reset() {', runtime_rpc + '\n\tasync function reset() {')
    runtime = once(runtime, '\t\tcompile,\n\t\treset,', '\t\tcompile,\n        exportCheckpoint, installCheckpoint,\n\t\treset,')
    (wasm / f'runtime{suffix}.js').write_bytes(runtime.encode())

    compiler = (repo / 'website/assets/lean-wasm/compiler.js').read_text(encoding='utf8')
    compiler = "import {CHECKPOINT, textHash, assertReceipts, assertSession} from './checkpoint-codec.js';\n" + compiler
    compiler, n = re.subn(r"\./runtime\.js\?v=[^']+", f'./runtime{suffix}.js?v={version}', compiler)
    assert n == 1
    compiler, n = re.subn(r"\./frontend-check\.js\?v=[^']+", f'./frontend-check{suffix}.js?v={version}', compiler)
    assert n == 1
    compiler = once(compiler, 'const loadedRoots = new Set();', 'const loadedRoots = new Set();\n    const checkpointReceipts = new Map();\n    let checkpointUsed = false;')
    compiler = once(compiler, 'return {result, parsed};', 'return {result, parsed, checkpointNonce: nonce};')
    compiler = once(compiler, "if (!SYNTAX_MODES.includes(mode)) throw new Error(`syntaxCheck must be one of ${SYNTAX_MODES.join(', ')}, not ${mode}`);", """if (!SYNTAX_MODES.includes(mode)) throw new Error(`syntaxCheck must be one of ${SYNTAX_MODES.join(', ')}, not ${mode}`);
                let checkpointEntry = null;
                if (runOptions.checkpointModule) {
                  checkpointEntry = CHECKPOINT.modules.find(entry => entry.module === runOptions.checkpointModule);
                  if (mode !== 'frontend' || !checkpointEntry || runOptions.mainModule !== checkpointEntry.module || await textHash(syntaxSource) !== checkpointEntry.sourceSha || await textHash(code) !== checkpointEntry.wrappedSha) throw Error('Checkpoint accepts only the exact wrapped probe source.');
                }""")
    compiler = once(compiler, "const hasErrors = problems.some((p) => p.severity === 'error') || result.success === false;", """const hasErrors = problems.some((p) => p.severity === 'error') || result.success === false;
                if (checkpointEntry && !hasErrors) checkpointReceipts.set(checkpointEntry.module, {module: checkpointEntry.module, sourceSha: checkpointEntry.sourceSha, wrappedSha: checkpointEntry.wrappedSha, nonce: frontend.checkpointNonce});""")
    compiler_rpc = '''        async exportCheckpoint(session) {
              assertSession(session);
              if (checkpointUsed || checkpointReceipts.size !== 1) throw Error('Checkpoint does not have the exact completed probe source.');
              checkpointUsed = true;
              const receipts = CHECKPOINT.modules.map(entry => checkpointReceipts.get(entry.module));
              assertReceipts(receipts);
              return runtime.exportCheckpoint(session, receipts);
            },
            async installCheckpoint(capsule, session) {
              assertSession(session);
              if (checkpointUsed || checkpointReceipts.size) throw Error('Checkpoint requires a fresh compiler.');
              checkpointUsed = true;
              const state = {attempted: new Set(), layers: new Set(), loaded: [], notMirrored: []};
              try {
                await ensureRoots(CHECKPOINT.requiredRoots, state, frontendLayers);
                return await runtime.installCheckpoint(capsule, session);
              } catch (error) { runtime.dispose(); throw error; }
            },
    '''
    compiler = once(compiler, "\t\tlanguage: 'lean',", "\t\tlanguage: 'lean',\n" + compiler_rpc)
    (wasm / f'compiler{suffix}.js').write_bytes(compiler.encode())

    index = (repo / 'website/assets/lean-wasm/index.js').read_text(encoding='utf8')
    index, n = re.subn(r"\./compiler\.js\?v=[^']+", f'./compiler{suffix}.js?v={version}', index)
    assert n == 1
    (wasm / f'index{suffix}.js').write_bytes(index.encode())

    compiler_path = wasm / 'compiler.js'
    compiler = compiler_path.read_text(encoding='utf8')
    compiler = once(compiler, 'const frontendLayers = optionalLayers(assets).map', "const frontendLayers = optionalLayers(assets, 'workspaces/proof-path-compression.json').map")
    compiler = once(compiler, 'textHash, assertReceipts, assertSession}', 'textHash, assertReceipts, assertSession, validateCapsule}')
    compiler = """// One in-memory issued lineage, shared only by this fixed-source probe graph.
    const issued = new Map();
    const sessionKey = session => JSON.stringify(session);
    const capsuleSeal = capsule => textHash(JSON.stringify({schema:capsule.schema,scope:capsule.scope,
      session:capsule.session,identity:capsule.identity,receipts:capsule.receipts,
      parts:capsule.parts.map(({module,suffix,size,sha256})=>({module,suffix,size,sha256}))}));
    """ + compiler
    compiler = once(compiler, 'const checkpointReceipts = new Map();', 'const checkpointReceipts = new Map(); let producerAttempted=false;')
    compiler = once(compiler, "            let checkpointEntry = null;", """            if (!CHECKPOINT.allowedSources.includes(await textHash(code))) throw Error('Probe source is not allowlisted.');
                if (mode !== 'frontend') throw Error('Probe requires completed frontend checking.');
                if (options.signal?.aborted) throw Error('Probe session was stopped.');
                let checkpointEntry = null;""")
    compiler = once(compiler, "\t\t\tconst state = { attempted: new Set(), layers: new Set(), loaded: [], notMirrored: [] };", """            if (checkpointEntry) {
                  if (producerAttempted) throw Error('Probe producer executes once per explicit run.');
                  producerAttempted=true;
                }
                const state = { attempted: new Set(), layers: new Set(), loaded: [], notMirrored: [] };""")
    compiler = once(compiler, 'checkpointEntry && !hasErrors', 'checkpointEntry && !hasErrors && problems.length === 0')
    compiler = once(compiler, 'return runtime.exportCheckpoint(session, receipts);', """const capsule=await runtime.exportCheckpoint(session,receipts);
              await validateCapsule(capsule,session);
              const seal=await capsuleSeal(capsule);
              if (options.signal?.aborted) throw Error('Probe session was stopped.');
              issued.clear();issued.set(sessionKey(session),{seal,signal:options.signal});
              return capsule;""")
    compiler = once(compiler, 'async installCheckpoint(capsule, session) {', """async installCheckpoint(capsuleInput, sessionInput) {
              const capsule=structuredClone(capsuleInput),session=structuredClone(sessionInput);""")
    compiler = once(compiler, '            await ensureRoots(CHECKPOINT.requiredRoots, state, frontendLayers);', """            await validateCapsule(capsule,session);
                const key=sessionKey(session),seal=await capsuleSeal(capsule),entry=issued.get(key);
                if (!entry || entry.seal!==seal || entry.signal!==options.signal || entry.signal?.aborted || options.signal?.aborted) throw Error('Probe lacks live privately issued artifact provenance.');
                issued.delete(key);
                await ensureRoots(CHECKPOINT.requiredRoots, state, frontendLayers);
                if (entry.signal?.aborted || options.signal?.aborted) throw Error('Probe session was stopped.');""")
    compiler_path.write_bytes(compiler.encode())

    shutil.copyfile(support/'control.js',assets/'checkpoint-control.js')
    shutil.copyfile(support/'probe.html',out/'lean/browser/checkpoint.html')
    records=[dict(path=path.relative_to(out).as_posix(),size=len(path.read_bytes()),sha256=sha(path.read_bytes()))
             for path in sorted(assets.rglob('*'),key=lambda path:path.parts) if path.is_file()]
    records += [dict(path='lean/browser/checkpoint.html',size=len((out/'lean/browser/checkpoint.html').read_bytes()),sha256=sha((out/'lean/browser/checkpoint.html').read_bytes()))]
    graph=dict(version=VERSION,config=config,files=records,source_sha256=SOURCE_SHA,consumer_sha256=CONSUMER_SHA,
        consumer_with_compatibility_sha256=sha(good.encode()),bounds=dict(parts=5,per_part=16777216,total=67108864),
        scope='One explicit run. Fixed original sources; new imports can initialize again. No persistent cache, general checkpoint API, state continuity or parallel compiler claim.')
    (out/'lean/browser/checkpoint-graph.json').write_bytes((json.dumps(graph,indent=2)+'\n').encode())
    for path in wasm.glob('*.js'):subprocess.run([node,'--check',str(path)],check=True,capture_output=True)
    return graph


def serve(output, port):
    """Local diagnostic server; the pinned pthread build requires isolation."""
    class Handler(SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
            self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
            self.send_header('Cache-Control', 'no-store')
            super().end_headers()

        def log_message(self, *_args): pass

    with ThreadingHTTPServer(('127.0.0.1', port), partial(Handler, directory=str(output.resolve()))) as server:
        print(f'Probe: http://127.0.0.1:{server.server_port}/lean/browser/checkpoint.html', flush=True)
        try: server.serve_forever()
        except KeyboardInterrupt: pass


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--node',default='node')
    parser.add_argument('--serve',action='store_true',help='Serve the generated probe on localhost with isolation headers')
    parser.add_argument('--port',type=int,default=8000)
    args=parser.parse_args()
    graph=build(args.runtime,args.output,args.node)
    print(json.dumps(dict(status='Prepared only; browser execution required',output=str(args.output.resolve()),assets=len(graph['files']),version=VERSION)))
    if args.serve: serve(args.output, args.port)
