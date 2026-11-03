// Which libraries a program needs, and what to say when one cannot be supplied.
//
// The runtime ships Mathlib only as a packed layer, and Std/Lean/Batteries as individual files, so
// there are two transports. Neither list is hardcoded to a specific host: both take the resolved
// asset directories.

/** Roots fetched one file at a time from `<libBase>`. */
export const OPTIONAL_LIBRARIES = ['Std', 'Lean', 'Batteries'];

/** Packed layers, each answering for a set of roots. */
export function optionalLayers(assets,manifest) {
	if(manifest!==undefined && !/^workspaces\/[a-z0-9-]+\.json$/.test(manifest)) throw new Error('Invalid workspace library manifest.');
	return [
		{
			label: 'Mathlib',
			manifestUrl: `${assets.layerBase}/${manifest||'real-analysis-layer.json'}`,
			packBase: assets.layerBase,
			roots: [
				'Mathlib',
				'Aesop',
				'Qq',
				'Plausible',
				'ProofWidgets',
				'ImportGraph',
				'LeanSearchClient',
				'Game'
			]
		}
	];
}

/** Roots that can never be supplied here, with the reason. */
export const UNAVAILABLE_LIBRARIES = {
	Lake: 'Lake is a build tool, and there is no build step here.'
};

/** Strip comments so a commented-out import does not count as one. */
export function stripComments(code) {
	const out=code.split('');let depth=0,string=false;
	for(let i=0;i<out.length;){
		const pair=out.slice(i,i+2).join('');let width=1;
		if(depth){if(pair==='/-'){depth++;width=2;}else if(pair==='-/'){depth--;width=2;}}
		else if(string){if(out[i]==='\\')width=2;else if(out[i]==='"')string=false;}
		else if(pair==='/-'){depth=1;width=2;}
		else if(pair==='--'){const end=out.indexOf('\n',i);width=(end<0?out.length:end)-i;}
		else if(out[i]==='"')string=true;
		else{i++;continue;}
		for(let j=i;j<Math.min(i+width,out.length);j++)if(out[j]!=='\n')out[j]=' ';
		i+=width;
	}
	return out.join('');
}

/** The original header prefix, including modern module markers and comments. */
export function sourceHeader(code) {
	const masked=stripComments(code);let offset=0,end=0,moduleEnd=0;
	for(const line of masked.split('\n')) {
		const next=Math.min(masked.length,offset+line.length+1),trimmed=line.trim();
		if(!trimmed){offset=next;continue;}
		if(!end&&trimmed==='module'){end=next;moduleEnd=next;}
		else if(trimmed==='prelude'){end=next;moduleEnd=next;}
		else if(/^(?:(?:public|private|meta)\s+)*import\s+\S/.test(trimmed))end=next;
		else break;
		offset=next;
	}
	// Masking retains UTF-16 offsets, including astral characters in comments.
	return {prefix:code.slice(0,end),body:code.slice(end),moduleEnd};
}

/** The distinct top-level roots a program imports, in order. */
export function importedRoots(code) {
	const roots = [];
	for (const line of importLines(code).split('\n')) {
		for (const name of line.replace(/^import\s+(?:all\s+)?/, '').split(/\s+/)) {
			const root = name.replace(/^'/, '').split('.')[0];
			if (root && !roots.includes(root)) roots.push(root);
		}
	}
	return roots;
}

/** Imports for the separate syntax probe, retaining the program's imported notation. */
export function importLines(code) {
	return stripComments(code)
		.split('\n')
		.map((line) => /^\s*(?:(?:public|private|meta)\s+)*import\s+(\S.*)$/.exec(line))
		.filter(Boolean)
		// The separate parser check needs the same imported notation; it does
		// not export a module, so visibility modifiers do not belong in its header.
		.map((match) => 'import '+match[1].trim())
		.join('\n');
}

/** Roots named by the compiler's "unknown module prefix 'X'" diagnostics. */
export function missingRoots(problems) {
	const roots = [];
	for (const problem of problems) {
		const match = /unknown module prefix '([^']+)'/.exec(problem.text);
		if (match && !roots.includes(match[1])) roots.push(match[1]);
	}
	return roots;
}

/** Which roots the package can fetch, for a caller that wants to check before running. */
export function fetchableRoots(assets) {
	return [...OPTIONAL_LIBRARIES, ...optionalLayers(assets).flatMap((layer) => layer.roots)];
}

function assetCommandFor(root, assets) {
	if (OPTIONAL_LIBRARIES.includes(root)) return 'lean-wasm-fetch-assets';
	if (optionalLayers(assets).some((layer) => layer.roots.includes(root))) {
		return 'lean-wasm-fetch-assets';
	}
	return null;
}

/**
 * Explain an unavailable import rather than leaving the compiler's bare "unknown module prefix",
 * which reads like a typo instead of a limit of this playground.
 *
 * `build` is what the worker has learned about the artifact and the layers. When their commits differ, the
 * usual advice — fetch the layer — is not enough: an `.olean` from another Lean build may be unreadable, so
 * the note says to fetch assets built by *this artifact's* Lean, not just any mirror (P2-2 in HANDOVER.md).
 */
export function unavailableImportNotes(code, notMirrored, assets, build = null) {
	const notes = [];
	const add = (note) => {
		if (!notes.includes(note)) notes.push(note);
	};
	const artifact = build?.artifact ?? null;
	const core = build?.core ?? null;
	const mixed =
		artifact && core && artifact !== core
			? ` This host's Lean artifact is ${artifact.slice(0, 12)} but its libraries are ${core.slice(0, 12)}, ` +
				`so fetch assets built by the artifact's Lean — \`lean-wasm-fetch-assets\` from any other build will not do.`
			: '';
	for (const root of importedRoots(code)) {
		if (notMirrored.includes(root)) {
			const command = assetCommandFor(root, assets);
			add(
				command
					? `${root} is not on the asset host. Mirror it with \`${command}\`.${mixed}`
					: `${root} is not available here.`
			);
		} else if (UNAVAILABLE_LIBRARIES[root]) {
			add(UNAVAILABLE_LIBRARIES[root]);
		}
	}
	return notes;
}

/**
 * A Mathlib module outside the published closure fails by path rather than by prefix, because
 * "Mathlib" itself resolves. Only the compiler-matched modules on the host are available.
 */
export function outsideClosureNotes(problems) {
	const notes = [];
	for (const problem of problems) {
		const match = /object file '[^']*' of module (\S+)/.exec(problem.text);
		if (!match || !match[1].startsWith('Mathlib.')) continue;
		const note =
			`${match[1]} is outside the available compiler-matched libraries. ` +
			'The browser has selected Mathlib modules; this import needs an additional matching artifact.';
		if (!notes.includes(note)) notes.push(note);
	}
	return notes;
}
