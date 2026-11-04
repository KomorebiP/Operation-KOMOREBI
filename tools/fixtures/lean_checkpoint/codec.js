// Scratch-only, fixed-source checkpoint qualification codec. This is not a proof certificate.
import {CHECKPOINT} from './checkpoint-policy.js';
export {CHECKPOINT};
export const SUFFIXES = ['.olean', '.olean.server', '.olean.private', '.ir.sig', '.ir'];
export const MAX_PART = 16 * 1024 * 1024;
export const MAX_TOTAL = 64 * 1024 * 1024;
const HEX = /^[0-9a-f]{64}$/;
const NONCE = /^[0-9a-f]{32}$/;
const plain = value => value !== null && typeof value === 'object' && !Array.isArray(value);
function exactKeys(value, keys, name) {
  if (!plain(value) || Object.keys(value).sort().join('|') !== [...keys].sort().join('|')) throw Error('Checkpoint invalid ' + name + ' fields.');
}
export async function sha256(bytes) {
  return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), byte => byte.toString(16).padStart(2, '0')).join('');
}
export async function textHash(text) { return sha256(new TextEncoder().encode(text)); }
export function expectedParts() {
  return CHECKPOINT.modules.flatMap(entry => SUFFIXES.map(suffix => ({module: entry.module, suffix})));
}
export function artifactPath(module, suffix) {
  if (!CHECKPOINT.modules.some(entry => entry.module === module) || !SUFFIXES.includes(suffix)) throw Error('Checkpoint module/part is not allowlisted.');
  return '/lib/lean/' + module.replaceAll('.', '/') + suffix;
}
export function assertSession(session) {
  exactKeys(session, ['workspace', 'generation', 'run', 'boundary'], 'session');
  if (session.workspace !== CHECKPOINT.workspace || session.boundary !== CHECKPOINT.boundary || !Number.isSafeInteger(session.generation) || session.generation < 1 || !NONCE.test(session.run)) throw Error('Checkpoint session is not the fixed original boundary.');
}
export function assertReceipts(receipts) {
  if (!Array.isArray(receipts) || receipts.length !== CHECKPOINT.modules.length) throw Error('Checkpoint needs the exact completed source receipt.');
  const nonces = new Set();
  for (const [i, entry] of CHECKPOINT.modules.entries()) {
    const receipt = receipts[i];
    exactKeys(receipt, ['module', 'sourceSha', 'wrappedSha', 'nonce'], 'receipt');
    if (receipt.module !== entry.module || receipt.sourceSha !== entry.sourceSha || receipt.wrappedSha !== entry.wrappedSha || !NONCE.test(receipt.nonce) || nonces.has(receipt.nonce)) throw Error('Checkpoint completion/source receipt mismatch.');
    nonces.add(receipt.nonce);
  }
}
export function assertLengths(parts) {
  const expected = expectedParts();
  if (!Array.isArray(parts) || parts.length !== expected.length) throw Error('Checkpoint requires exactly five probe parts.');
  let total = 0;
  for (const [i, part] of parts.entries()) {
    if (part.module !== expected[i].module || part.suffix !== expected[i].suffix || !Number.isSafeInteger(part.size) || part.size < 0 || part.size > MAX_PART) throw Error('Checkpoint part identity or byte budget mismatch.');
    total += part.size;
    if (total > MAX_TOTAL) throw Error('Checkpoint total byte budget exceeded.');
  }
  return total;
}
export async function validateCapsule(capsule, session, identity = null) {
  exactKeys(capsule, ['schema', 'scope', 'session', 'identity', 'receipts', 'parts'], 'capsule');
  assertSession(session); assertSession(capsule.session);
  if (JSON.stringify(session) !== JSON.stringify(capsule.session) || capsule.schema !== 1 || capsule.scope !== CHECKPOINT.scope || !HEX.test(capsule.identity) || identity !== null && capsule.identity !== identity) throw Error('Checkpoint stale session or compiler identity.');
  assertReceipts(capsule.receipts);
  const total = assertLengths(capsule.parts), buffers = new Set();
  for (const part of capsule.parts) {
    exactKeys(part, ['module', 'suffix', 'size', 'sha256', 'bytes'], 'part');
    if (!HEX.test(part.sha256) || !(part.bytes instanceof Uint8Array) || !(part.bytes.buffer instanceof ArrayBuffer) || part.bytes.byteOffset !== 0 || part.bytes.byteLength !== part.size || part.bytes.buffer.byteLength !== part.size || buffers.has(part.bytes.buffer)) throw Error('Checkpoint part must own its exact byte buffer.');
    buffers.add(part.bytes.buffer);
  }
  // Shape/budgets are checked for every part before any digest allocation.
  for (const part of capsule.parts) if (await sha256(part.bytes) !== part.sha256) throw Error('Checkpoint artifact checksum mismatch: ' + part.module + part.suffix);
  return total;
}
