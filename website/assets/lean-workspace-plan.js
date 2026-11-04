// Route a selected file through its edited project imports without changing source.
// This is deliberately narrower than Lean's parser; Lean still checks every proof.
import {OPTIONAL_LIBRARIES, optionalLayers, sourceHeader, stripComments} from './lean-wasm/roots.js';

const moduleName = /^[\p{ID_Start}_][\p{ID_Continue}']*(?:\.[\p{ID_Start}_][\p{ID_Continue}']*)*$/u;
const externalRoots = new Set(['Init', ...OPTIONAL_LIBRARIES,
  ...optionalLayers({layerBase: ''}).flatMap(layer => layer.roots)]);
const reservedNames = new Set(['all', 'import', 'module', 'prelude', 'public', 'private', 'meta',
  'as', 'hiding', 'renaming', 'only', 'except']);
const bodyCommands = new Set(['section', 'end', 'namespace', 'open', 'export', 'variable', 'variables',
  'universe', 'universes', 'def', 'theorem', 'example', 'instance', 'inductive', 'structure', 'class',
  'abbrev', 'opaque', 'constant', 'constants', 'axiom', 'axioms', 'initialize', 'builtin_initialize',
  'syntax', 'macro', 'macro_rules', 'elab', 'elab_rules', 'notation', 'infix', 'infixl', 'infixr',
  'prefix', 'postfix', 'attribute', 'set_option', 'noncomputable', 'unsafe', 'mutual']);

function unsupported(module, detail) {
  throw new Error(`Cannot plan ${module}: unsupported or ambiguous import header${detail ? ': ' + detail : '.'} Use Run workspace to check the complete source.`);
}

// stripComments also masks strings. Reject strings hidden inside a recognized
// header rather than interpreting `import A "B"` as just `import A`.
function validateHeaderText(source, end, module) {
  let depth = 0;
  for (let i = 0; i < source.length && (i < end || depth);) {
    const pair = source.slice(i, i + 2);
    if (depth) {
      if (pair === '/-') { depth++; i += 2; }
      else if (pair === '-/') { depth--; i += 2; }
      else i++;
    } else if (pair === '/-') { depth = 1; i += 2; }
    else if (pair === '--') {
      const next = source.indexOf('\n', i);
      i = next < 0 ? source.length : next + 1;
    } else if (source[i] === '"') unsupported(module, 'string in header');
    else i++;
  }
  if (depth) unsupported(module, 'unterminated header comment');
}

function projectImports(source, module) {
  if (typeof source !== 'string') throw new Error(`Missing edited source for ${module}.`);
  const {prefix} = sourceHeader(source);
  const masked = stripComments(source);
  validateHeaderText(source, prefix.length, module);
  const result = [];
  let sawModule = false, sawPrelude = false, sawImport = false;
  for (const line of masked.slice(0, prefix.length).split('\n')) {
    const text = line.trim();
    if (!text) continue;
    if (text === 'module') {
      if (sawModule || sawPrelude || sawImport) unsupported(module, text);
      sawModule = true; continue;
    }
    if (text === 'prelude') {
      if (sawPrelude || sawImport) unsupported(module, text);
      sawPrelude = true; continue;
    }
    const match = /^((?:(?:public|private|meta)\s+)*)import\s+(.+)$/.exec(text);
    if (!match) unsupported(module, text);
    const flags = match[1].trim().split(/\s+/).filter(Boolean);
    if (new Set(flags).size !== flags.length || flags.includes('public') && flags.includes('private')) {
      unsupported(module, text);
    }
    const names = match[2].trim().split(/\s+/);
    if (names[0] === 'all') names.shift();
    if (!names.length || names.some(name => !moduleName.test(name) || reservedNames.has(name))) {
      unsupported(module, text);
    }
    for (const name of names) if (!result.includes(name)) result.push(name);
    sawImport = true;
  }
  const body = masked.slice(prefix.length);
  // Header continuations, late imports and modifiers unsupported by the shared
  // header reader must fail before any source command is executed.
  for (const line of body.split('\n')) {
    const text = line.trim();
    if (/^(?:(?:public|private|meta|all)\s+)*(?:import|prelude|module)\b/.test(text) ||
        /^(?:public|private|meta|all)$/.test(text) ||
        /^(?:protected|noncomputable|unsafe|scoped|local)\b.*\bimport\b/.test(text)) {
      unsupported(module, text);
    }
  }
  const firstBodyLine = body.split('\n').map(line => line.trim()).find(Boolean);
  if (sawImport && firstBodyLine && moduleName.test(firstBodyLine) && !bodyCommands.has(firstBodyLine)) {
    unsupported(module, 'possible multiline import: ' + firstBodyLine);
  }
  return result;
}

/** Return original file indices for exactly the selected target and its ancestors.
 * A stable topological sort preserves registry order among ready modules.
 * No source is rewritten or executed, and unrelated source headers are not read.
 */
export function planSelectedFile(workspace, sources, targetIndex) {
  const files = workspace?.files;
  if (!Array.isArray(files) || !files.length || !Array.isArray(sources) || sources.length !== files.length ||
      !Number.isInteger(targetIndex) || targetIndex < 0 || targetIndex >= files.length) {
    throw new Error('Invalid selected workspace file.');
  }
  const byModule = new Map();
  for (const [index, file] of files.entries()) {
    if (!file || typeof file.module !== 'string' || !moduleName.test(file.module)) {
      throw new Error('Invalid workspace module name.');
    }
    if (byModule.has(file.module)) throw new Error('Duplicate workspace module: ' + file.module);
    byModule.set(file.module, index);
  }
  const dependencies = new Map(), pending = [targetIndex];
  while (pending.length) {
    const index = pending.pop();
    if (dependencies.has(index)) continue;
    const file = files[index], names = projectImports(sources[index], file.module), edges = new Set();
    if (workspace.legacy && !file.library && !file.generated) {
      const legacy = byModule.get(workspace.legacy);
      if (legacy === undefined || !files[legacy].generated) {
        throw new Error('Missing generated compatibility module: ' + workspace.legacy);
      }
      names.push(workspace.legacy);
    }
    for (const name of names) {
      if (byModule.has(name)) edges.add(byModule.get(name));
      else if (!externalRoots.has(name.split('.')[0])) {
        throw new Error(`Missing project import ${name} requested by ${file.module}.`);
      }
    }
    dependencies.set(index, edges);
    pending.push(...edges);
  }
  const remaining = new Map(), consumers = new Map();
  for (const [index, edges] of dependencies) {
    remaining.set(index, edges.size);
    for (const dependency of edges) {
      if (!consumers.has(dependency)) consumers.set(dependency, []);
      consumers.get(dependency).push(index);
    }
  }
  const ready = [...remaining.keys()].filter(index => remaining.get(index) === 0).sort((a, b) => a - b);
  const order = [];
  while (ready.length) {
    const index = ready.shift();
    order.push(index);
    for (const consumer of consumers.get(index) || []) {
      const count = remaining.get(consumer) - 1;
      remaining.set(consumer, count);
      if (!count) { ready.push(consumer); ready.sort((a, b) => a - b); }
    }
  }
  if (order.length !== dependencies.size) {
    const cycle = [...remaining].filter(([, count]) => count > 0).map(([index]) => files[index].module);
    throw new Error('Project import cycle prevents checking: ' + cycle.join(', '));
  }
  return order;
}
