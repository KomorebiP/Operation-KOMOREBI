// The runtime worker: one long-lived Worker that boots the Lean runtime once and then compiles
// repeatedly, reusing the environment it has already imported.
//
// It has to be a Worker rather than the calling thread for two reasons: the Init import is a long
// synchronous stretch inside wasm, and a pthread build parks its thread pool on the thread that
// created it. LiveCodes runs language drivers inside its own sandbox worker, and a worker may create
// a nested one — but the script URL must be same-origin, so the runtime is handed over as a **blob**
// that is generated here.
//
// The worker's own source arrives as a string (see scripts/sync-worker.mjs, which generates it from
// `worker/lean-worker.js`), so there is one implementation and the demo in this repo consumes it too.

// Separate same-origin worker source keeps the vendored implementation reviewable.
const RUNTIME_WORKER_SOURCE = 'importScripts(' + JSON.stringify(new URL('./worker.js?v=20261103-staged1', import.meta.url).href) + ');';
const NATIVE_INVOKES_URL = new URL('./native-invokes.js', import.meta.url).href;

const COMPILE_PATH = '/workspace/input.lean';
const SHUTDOWN_TIMEOUT_MS = 100;

function createWorkerSource(config) {
	// A blob URL carries no query string, so the config travels as a global the worker reads first.
	// The worker still accepts `?assetBase=`/`?libBase=`, which is what the demo uses.
	return `self.__LEAN_WASM_CONFIG__ = ${JSON.stringify(config)};\n${RUNTIME_WORKER_SOURCE}`;
}

export function createRuntime({ assetBase, libBase, memory, onProgress, onStatus }) {
	let worker = null;
	let objectUrl = null;
	let stdout = '';
	let stderr = '';
	let nextId = 1;
	let ready = false;
	let operations = 0;
	let disposed = false;
	let retiringWorker = null;
	let retirementId = null;
	let retirementTimer = null;
	let closedResolved = false;
	let resolveClosed;
	const closed = new Promise(resolve => { resolveClosed = resolve; });
	// Worker-created object URLs do not have a specified worker-unload cleanup
	// hook. Create the runtime's large Blob URLs here so hard Stop owns them too.
	const ownedBlobUrls = new Set();
	const assetUrls = new Map();
	const waiters = [];
	// Build identities the worker has seen, so the compiler can make its fallback notes build-aware.
	const build = { artifact: null, core: null, layer: null };

	function noteBuild(msg) {
		if (!msg.build) return;
		for (const key of ['artifact', 'core', 'layer']) {
			if (msg.build[key]) build[key] = msg.build[key];
		}
	}

	const emit = (message) => {
		if (message) onProgress?.(message);
	};

	function dispatch(event, source) {
		const msg = event.data || {};
		if (disposed) {
			if (source === retiringWorker && msg.type === 'disposed' && msg.id === retirementId) {
				finishClose({acknowledged: true, cleanup: msg.cleanup});
			}
			return;
		}
		if (source !== worker) return;

		switch (msg.type) {
			case 'create_blob_url': {
				try {
					if (!Number.isSafeInteger(msg.id) || msg.id < 1 ||
						!['wasm', 'script'].includes(msg.kind) || !(msg.blob instanceof Blob) || assetUrls.has(msg.kind)) {
						throw new Error('Invalid runtime asset URL request.');
					}
					const url = URL.createObjectURL(msg.blob);
					ownedBlobUrls.add(url);assetUrls.set(msg.kind, url);
					source.postMessage({type: 'blob_url', id: msg.id, url});
				} catch (error) {
					try { source.postMessage({type: 'blob_url', id: msg.id, error: String(error.message || error)}); }
					catch { dispose({force: true}); }
				}
				return;
			}
			case 'ready':
				ready = true;
				break;
			case 'stdout':
				stdout += msg.data + '\n';
				return;
			case 'stderr':
				stderr += msg.data + '\n';
				return;
			case 'status':
				onStatus?.(msg.data);
				return;
			case 'memory':
				// Only a threaded artifact gets here: an unshared one leaves the memory to Emscripten, so
				// there is no choice to report.
				emit(
					msg.failed
						? `shared memory: ${msg.mb} MB refused, trying a smaller one`
						: `shared memory: ${msg.mb} MB (max ${msg.maximumPages} pages)`
				);
				return;
			case 'library':
				noteBuild(msg);
				if (msg.stage === 'manifest') {
					emit(`core layer: ${msg.modules} modules in ${msg.packs} packs`);
				} else if (msg.stage === 'pack') {
					emit(`core pack ${msg.loaded}/${msg.total}`);
				} else if (msg.stage === 'written') {
					emit(`${msg.files} library files installed`);
				}
				return;
			case 'modules':
				if (msg.stage === 'progress') emit(`loading ${msg.root}: ${msg.files}/${msg.total} files`);
				return;
			case 'layer':
				noteBuild(msg);
				if (msg.stage === 'progress') emit(`loading ${msg.label}: pack ${msg.pack}/${msg.packs}`);
				return;
			default:
				break;
		}

		for (const waiter of [...waiters]) {
			if (!waiter.match(msg)) continue;
			waiters.splice(waiters.indexOf(waiter), 1);
			clearTimeout(waiter.timer);
			waiter.resolve(msg);
		}

		if (msg.type === 'error') {
			failAll(new Error(msg.data));
			dispose({force: true});
		}
	}

	function failAll(error) {
		for (const waiter of waiters.splice(0)) {
			clearTimeout(waiter.timer);
			waiter.reject(error);
		}
	}

	function waitFor(match, label, timeoutMs) {
		return new Promise((resolve, reject) => {
			const waiter = { match, resolve, reject, timer: null };
			waiter.timer = setTimeout(() => {
				const index = waiters.indexOf(waiter);
				if (index >= 0) waiters.splice(index, 1);
				reject(new Error(`${label} timed out after ${Math.round(timeoutMs / 1000)}s`));
			}, timeoutMs);
			waiters.push(waiter);
		});
	}

	function post(message) {
		if (disposed || !worker) throw new Error('The Lean runtime is not running.');
		worker.postMessage(message);
	}

	async function request(message, match, label, timeoutMs) {
		operations++;
		try {
			post(message);
			return await waitFor(match, label, timeoutMs);
		} catch (error) {
			ready = false;
			dispose({force: true});
			throw error;
		} finally { operations--; }
	}

	async function start() {
		if (disposed || worker) throw new Error('The Lean runtime cannot be started again.');
		objectUrl = URL.createObjectURL(new Blob([createWorkerSource({ assetBase, libBase, memory, nativeInvokesUrl: NATIVE_INVOKES_URL, hostOwnsBlobUrls: true })], { type: 'text/javascript' }));
		ownedBlobUrls.add(objectUrl);
		try { worker = new Worker(objectUrl); }
		catch (error) { dispose({force: true});throw error; }
		const startedWorker = worker;
		worker.onmessage = event => dispatch(event, startedWorker);
		worker.onerror = (event) => {
			if (startedWorker !== worker && startedWorker !== retiringWorker) return;
			failAll(new Error(event.message || 'Lean runtime error'));
			dispose({force: true});
		};

		// The Init import is the long part, and it reports progress through the heartbeats the worker
		// forwards, so the timeout only has to be generous enough to notice a wedged boot.
		try { await request({type: 'start'}, msg => msg.type === 'ready', 'Starting the Lean runtime', 120_000); }
		catch (error) { dispose({force: true});throw error; }
	}

	async function loadModules(roots) {
		const id = nextId++;
		const reply = await request({type: 'load_modules', id, roots}, msg => msg.type === 'modules_loaded' && msg.id === id, `Loading ${roots.join(', ')}`, 300_000);
		return reply.results ?? [];
	}

	async function loadLayer(layer) {
		const id = nextId++;
		const reply = await request({type: 'load_layer', id, label: layer.label, manifestUrl: layer.manifestUrl, packBase: layer.packBase}, msg => msg.type === 'layer_loaded' && msg.label === layer.label, `Loading ${layer.label}`, 600_000);
		return reply;
	}

	async function compile(code) {
		const id = nextId++;
		stdout = '';
		stderr = '';
		const reply = await request({type: 'compile', id, code, path: COMPILE_PATH}, msg => msg.type === 'result' && msg.id === id, 'Compiling', 600_000);
		// A trap or escaped exception may leave the native stack unusable. Plain
		// Lean IO errors remain retryable so missing imports can still be loaded.
		if (reply.fatal) dispose({force: true});
		return { ...reply, stdout, stderr };
	}

	async function reset() {
		const id = nextId++;
		await request({type: 'reset', id}, msg => msg.type === 'reset_done' && msg.id === id, 'Resetting the workspace', 30000);
	}

	function finishClose(info = {acknowledged: false}) {
		clearTimeout(retirementTimer);retirementTimer = null;
		const retiring = retiringWorker;retiringWorker = null;
		if (retiring) {
			retiring.onmessage = null;retiring.onerror = null;
			try { retiring.terminate(); } catch { /* ownership still ends here */ }
		}
		for (const url of ownedBlobUrls) {
			try { URL.revokeObjectURL(url); } catch { /* revoke the remaining URLs too */ }
		}
		ownedBlobUrls.clear();assetUrls.clear();objectUrl = null;
		if (!closedResolved) { closedResolved = true;resolveClosed(info); }
	}

	/** Stop is immediate while work is pending. Idle disposal first asks the
	 * owning worker to terminate its pthread pool, with a bounded hard fallback.
	 * An acknowledgement means cleanup requests were issued, not that the browser
	 * has physically reclaimed every shared-memory mapping yet. */
	function dispose({force = false} = {}) {
		if (disposed) {
			if (force && retiringWorker) finishClose({acknowledged: false, forced: true});
			return closed;
		}
		disposed = true;
		failAll(new Error('The compiler was disposed.'));
		retiringWorker = worker;worker = null;
		if (!retiringWorker || force || !ready || operations > 0) {
			finishClose({acknowledged: false, forced: true});
		} else {
			retirementId = nextId++;
			retirementTimer = setTimeout(() => finishClose({acknowledged: false}), SHUTDOWN_TIMEOUT_MS);
			try { retiringWorker.postMessage({type: 'dispose', id: retirementId}); }
			catch { finishClose({acknowledged: false, forced: true}); }
		}
		return closed;
	}

	return {
		start,
		loadModules,
		loadLayer,
		compile,
		reset,
		dispose,
		/** Resolves after terminal worker termination is requested and owned URLs revoked. */
		closed,
		/** What the worker has learned about the artifact and the layers, once each has been fetched. */
		get build() {
			return { ...build };
		}
	};
}
