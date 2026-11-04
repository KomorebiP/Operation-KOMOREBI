import test from 'node:test';
import assert from 'node:assert/strict';
import {checkedFrontendSource, frontendMarkers} from '../website/assets/lean-wasm/frontend-check.js';

const nonce = '0123456789abcdef0123456789abcdef';

// Decode the bounded Lean string expression so tests compare the exact source,
// including large/Unicode inputs, rather than merely matching generated text.
function embeddedSource(transport) {
  const match = transport.match(/^  let src := (.+)\n  let ictx/m);
  assert.ok(match, 'transport contains the embedded source expression');
  const expression = match[1];
  let offset = 0;
  function part() {
    if (expression.startsWith('String.join [', offset)) {
      offset += 13;
      let value = '';
      while (expression[offset] !== ']') {
        value += part();
        if (expression.startsWith(', ', offset)) offset += 2;
        else break;
      }
      assert.equal(expression[offset++], ']');
      return value;
    }
    assert.equal(expression[offset], '"');
    const start = offset++;
    while (offset < expression.length) {
      if (expression[offset] === '\\') { offset += 2; continue; }
      if (expression[offset++] === '"') return JSON.parse(expression.slice(start, offset));
    }
    assert.fail('unterminated source literal');
  }
  const source = part();
  assert.equal(offset, expression.length);
  return {source, outside: transport.replace(match[0], '  let src := <source>\n  let ictx')};
}

test('original headers and large source text survive the fixed transport exactly', () => {
  const header = 'module\npublic meta import Mathlib.Pilot\nimport all Lean.Pilot\n';
  const body = ('-- α🌿 \\ " Unicode\t\r\nexample : True := by trivial\n').repeat(1100);
  const code = header + body;
  const transport = checkedFrontendSource(code, {nonce});
  const decoded = embeddedSource(transport);
  assert.equal(decoded.source, code);
  assert.ok(transport.startsWith('module\nimport Lean\nmeta import Lean.Elab.Frontend\nopen Lean\n'));
  assert.ok(!decoded.outside.includes('Mathlib.Pilot'));
  assert.ok(!decoded.outside.includes('import all Lean.Pilot'));
});

test('template-looking source and replacement tokens are never interpreted', () => {
  const code = '#eval "$& $` $\' FRONTEND_NAMESPACE_HERE SOURCE_EXPRESSION_HERE MAIN_MODULE_HERE INPUT_FILE_NAME_HERE __STARTED_NONCE__ __COMPLETED_NONCE__"\n';
  const decoded = embeddedSource(checkedFrontendSource(code, {nonce, mainModule: "Pilot.α'"}));
  assert.equal(decoded.source, code);
  assert.ok(!/FRONTEND_NAMESPACE_HERE|SOURCE_EXPRESSION_HERE|MAIN_MODULE_HERE|INPUT_FILE_NAME_HERE|__STARTED_NONCE__|__COMPLETED_NONCE__/.test(decoded.outside));
  assert.ok(decoded.outside.includes("importedEnv.setMainModule `Pilot.α'"));
  const markers = frontendMarkers(nonce);
  assert.ok(decoded.outside.includes('Parser.mkInputContext src "' + markers.fileName + '"'));
  assert.equal(decoded.outside.split('logInfo "' + markers.started + '"').length, 2);
  assert.equal(decoded.outside.split('logInfo "' + markers.completed + '"').length, 2);
});

test('helper declarations and calls use one fresh namespace without rewriting source text', () => {
  const secondNonce = 'f'.repeat(32);
  const code = '-- FRONTEND_NAMESPACE_HERE KomorebiFrontend_' + nonce + '\nexample : True := by trivial\n';
  const first = embeddedSource(checkedFrontendSource(code, {nonce}));
  const second = embeddedSource(checkedFrontendSource(code, {nonce: secondNonce}));
  assert.equal(first.source, code);
  assert.equal(second.source, code);
  const firstNamespace = 'KomorebiFrontend_' + nonce;
  const secondNamespace = 'KomorebiFrontend_' + secondNonce;
  for (const [decoded, expected, other] of [[first, firstNamespace, secondNamespace], [second, secondNamespace, firstNamespace]]) {
    const declared = [...decoded.outside.matchAll(/^meta def ([\w]+)\./gm)].map(match => match[1]);
    const referenced = [...decoded.outside.matchAll(/\b(KomorebiFrontend_[0-9a-f]{32})\./g)].map(match => match[1]);
    assert.ok(declared.length > 0, 'transport declares executable helpers');
    assert.deepEqual(new Set(declared), new Set([expected]));
    assert.deepEqual(new Set(referenced), new Set([expected]));
    assert.ok(!decoded.outside.includes(other));
    assert.ok(!decoded.outside.includes('FRONTEND_NAMESPACE_HERE'));
    assert.equal(decoded.outside.match(/^run_cmd do$/gm)?.length, 1);
  }
});

test('unsupported original characters and non-string inputs are rejected before encoding', () => {
  const forbidden = [...Array(9).keys(), 11, 12, ...Array.from({length: 18}, (_, i) => i + 14), 0x2028, 0x2029];
  for (const codePoint of forbidden) {
    assert.throws(() => checkedFrontendSource('-- ' + String.fromCodePoint(codePoint), {nonce}), /unsupported control/);
  }
  for (const code of [null, undefined, 1, {}, ['import Std']]) {
    assert.throws(() => checkedFrontendSource(code, {nonce}), /must be a string/);
  }
  const allowed = 'import Std\r\n-- π🌿\t\n';
  assert.equal(embeddedSource(checkedFrontendSource(allowed, {nonce})).source, allowed);
});

test('nonces identify distinct exact lifecycle markers and embedded filenames', () => {
  const first = frontendMarkers(nonce);
  const second = frontendMarkers('f'.repeat(32));
  assert.equal(new Set(Object.values(first)).size, 3);
  assert.equal(new Set([...Object.values(first), ...Object.values(second)]).size, 6);
  assert.equal(first.fileName, '<komorebi-frontend-' + nonce + '>');
  for (const invalid of [undefined, null, '', 'a'.repeat(31), 'a'.repeat(33), 'A'.repeat(32), 'g'.repeat(32), {toString: () => nonce}]) {
    assert.throws(() => frontendMarkers(invalid), /nonce/);
    assert.throws(() => checkedFrontendSource('', {nonce: invalid}), /nonce/);
  }
});

test('module names are optional but cannot inject transport commands', () => {
  assert.ok(checkedFrontendSource('', {nonce}).includes('importedEnv.setMainModule Name.anonymous'));
  for (const mainModule of ['Pilot.Main', "Pilot.α'", '_Pilot']) {
    assert.ok(checkedFrontendSource('', {nonce, mainModule}).includes('importedEnv.setMainModule `' + mainModule));
  }
  for (const mainModule of ['', '../Pilot', 'Pilot/Main', 'Pilot..Main', 'Pilot`\n#exit', 'Pilot Main', 0, {toString: () => 'Pilot'}]) {
    assert.throws(() => checkedFrontendSource('', {nonce, mainModule}), /main module/);
  }
});
