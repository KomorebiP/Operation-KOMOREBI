// Fixed-source qualification transfer. Imports in B can rerun initializers.
let checkpointPhase = false;
let checkpointCommitted = false;
let checkpointInvalid = false;
const checkpointManifests = new Map();
const checkpointCorePacks = new Map();
const checkpointMeasured = {};
let checkpointCodecPromise;
const checkpointCodec = () => checkpointCodecPromise ??= import(workerConfig.checkpointCodecUrl);
async function checkpointReadManifest(url) {
  const response = await fetch(url);
  if (!response.ok) throw Error('Checkpoint manifest HTTP failure: ' + url);
  const bytes = new Uint8Array(await response.arrayBuffer());
  const codec = await checkpointCodec();
  const engine = new URL('../', assetBase + '/').href;
  const absolute = new URL(url, location.href).href;
  if (!absolute.startsWith(engine)) throw Error('Checkpoint manifest outside engine.');
  const key = absolute.slice(engine.length);
  const expected = codec.CHECKPOINT.manifests[key];
  const hash = await codec.sha256(bytes);
  if (!expected || expected !== hash) throw Error('Checkpoint pinned manifest mismatch: ' + key);
  checkpointManifests.set(key, hash);
  return JSON.parse(new TextDecoder().decode(bytes));
}
async function checkpointIdentity() {
  const codec = await checkpointCodec(), pin = codec.CHECKPOINT;
  const sourceResponse = await fetch(new URL('../SOURCE.json', assetBase + '/'), {cache: 'no-cache'});
  if (!sourceResponse.ok) throw Error('Checkpoint engine identity unavailable.');
  const sourceBytes = new Uint8Array(await sourceResponse.arrayBuffer());
  if (await codec.sha256(sourceBytes) !== pin.engineSourceSha) throw Error('Checkpoint engine source identity mismatch.');
  const source = JSON.parse(new TextDecoder().decode(sourceBytes));
  if (source.lean !== pin.lean || source.mathlib !== pin.mathlib || source.mathlib_source_sha256 !== pin.mathlibArchiveSha) throw Error('Checkpoint compiler/library pin mismatch.');
  const entries = Object.entries(pin.manifests).sort(([a], [b]) => a.localeCompare(b));
  if (checkpointManifests.size !== entries.length || entries.some(([name, hash]) => checkpointManifests.get(name) !== hash)) throw Error('Checkpoint requires the same complete frontend library manifests.');
  if (checkpointMeasured.wasmTransfer !== pin.wasmTransferSha || checkpointMeasured.glueOriginal !== pin.glueSha || checkpointMeasured.applied !== true || !checkpointMeasured.wasmTransformed || !checkpointMeasured.glueTransformed) throw Error('Checkpoint exact native runtime pair unavailable.');
  const corePacks = Object.entries(pin.corePacks).sort(([a], [b]) => a.localeCompare(b));
  if (checkpointCorePacks.size !== corePacks.length || corePacks.some(([name, hash]) => checkpointCorePacks.get(name) !== hash)) throw Error('Checkpoint exact core pack set unavailable.');
  const measured = {wasmTransfer: checkpointMeasured.wasmTransfer, glueOriginal: checkpointMeasured.glueOriginal, applied: checkpointMeasured.applied, wasmTransformed: checkpointMeasured.wasmTransformed, glueTransformed: checkpointMeasured.glueTransformed};
  return codec.textHash(JSON.stringify({contract: pin.contract, source: pin.engineSourceSha, measured, corePacks, manifests: entries, frontend: pin.frontendSha, wrapper: pin.wrapperSha}));
}
async function exportCheckpoint(request) {
  const codec = await checkpointCodec();
  if (!moduleReady || compileBusy || checkpointCommitted) throw Error('Checkpoint export requires an idle current worker.');
  codec.assertSession(request.session); codec.assertReceipts(request.receipts);
  const parts = codec.expectedParts().map(part => {
    const path = codec.artifactPath(part.module, part.suffix);
    const stat = Module.FS.lstat(path);
    if (!Module.FS.isFile(stat.mode)) throw Error('Checkpoint emitted part is not a regular file: ' + path);
    return {...part, size: stat.size};
  });
  // Stat and cumulative checks precede reading or allocating any artifact bytes.
  codec.assertLengths(parts);
  const identity = await checkpointIdentity();
  for (const part of parts) {
    if (!moduleReady) throw Error('Checkpoint transaction was invalidated.');
    part.bytes = new Uint8Array(Module.FS.readFile(codec.artifactPath(part.module, part.suffix)));
    if (part.bytes.length !== part.size) throw Error('Checkpoint stat/read length changed.');
    part.sha256 = await codec.sha256(part.bytes);
    post({type: 'status', data: 'Checkpoint part ' + part.module + part.suffix + ': ' + part.size + ' bytes'});
  }
  const capsule = {schema: 1, scope: codec.CHECKPOINT.scope, session: request.session, identity, receipts: request.receipts, parts};
  await codec.validateCapsule(capsule, request.session, identity);
  return capsule;
}
async function installCheckpoint(request) {
  const codec = await checkpointCodec();
  if (!moduleReady || compileBusy || checkpointCommitted) throw Error('Checkpoint install requires a fresh idle worker.');
  const identity = await checkpointIdentity();
  const total = await codec.validateCapsule(request.capsule, request.session, identity);
  if (!moduleReady) throw Error('Checkpoint transaction was invalidated.');
  const FS = Module.FS, stage = '/workspace/.checkpoint-' + request.session.run;
  // All destinations are checked before the first stage write. No arbitrary paths.
  for (const part of request.capsule.parts) if (FS.analyzePath(codec.artifactPath(part.module, part.suffix)).exists) throw Error('Checkpoint destination already exists.');
  if (FS.analyzePath(stage).exists) throw Error('Checkpoint staging transaction already exists.');
  mkdirp(FS, stage);
  for (const [i, part] of request.capsule.parts.entries()) {
    const path = stage + '/' + i;
    FS.writeFile(path, part.bytes);
    const written = new Uint8Array(FS.readFile(path));
    if (written.length !== part.size || await codec.sha256(written) !== part.sha256) throw Error('Checkpoint staged artifact mismatch.');
    if (!moduleReady) throw Error('Checkpoint transaction was invalidated.');
  }
  // Rename is multi-file, not atomic. The exclusive phase lock makes it
  // compiler-visible all-or-terminal-failure; any exception invalidates worker.
  for (const [i, part] of request.capsule.parts.entries()) {
    const path = codec.artifactPath(part.module, part.suffix);
    mkdirp(FS, path.slice(0, path.lastIndexOf('/')));
    FS.rename(stage + '/' + i, path);
  }
  checkpointCommitted = true;
  return {parts: request.capsule.parts.length, bytes: total, identity};
}
