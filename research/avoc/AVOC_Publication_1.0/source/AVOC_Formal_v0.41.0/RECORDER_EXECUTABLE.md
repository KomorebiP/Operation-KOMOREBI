# Operation recorder executable contract

The v0.41 recorder turns a finite command sequence into a deterministic snapshot. Every request starts empty. It does not execute an operation, retry a failure, authenticate a report, or store a durable mutable journal.

The inherited calibration parser accepts immutable completed reports. Appending an `intent` and then a changed terminal event with the same operation ID to that parser causes a conflicting replay error. The recorder solves this lifecycle mismatch by keeping pending intents outside the completed log. Finalization removes the pending entry and appends exactly one terminal event. The old parser is unchanged.

## Request and response

```json
["observation-recorder-v1", [
  ["begin", 0, 1],
  ["finish", 0, 1, "success"],
  ["finish", 0, 1, "success"],
  ["begin", 0, 1]
]]
```

This returns:

```json
{"status":"recorded","pending":[],"log":[[0,1,"success"]],"ready":true}
```

The terminal outcomes are `success`, `rejection`, and `fault`. A replay with identical ID, key, and outcome is a no-op. Repeating a pending begin with the same key is a no-op. A late begin with the same completed ID and key does not reopen the operation. A changed key, changed terminal outcome, or finish without matching pending intent is rejected.

A semantic rejection returns only `status`, zero-based `index`, and `error`:

```json
{"status":"rejected","index":2,"error":"command_rejected"}
```

There is no final snapshot or calibration export on that branch. A malformed request is a separate input error. The entire request is parsed before any response is exposed. The batch format is `["observation-recorder-batch-v1", [commands, commands, ...]]`, with independent empty initial states for each word.

`ready` is true precisely when no operation is pending across any identity. It does not mean that a calibration checkpoint has enough samples. Completed events remain in finalization order. Faults are retained in the completed log for accountability but add no binary sample.

## Exact input bounds

IDs and keys must be JSON integers from 0 through 2,147,483,647. Boolean values, decimal or exponent numeric tokens, nonfinite numbers, duplicate object fields, unknown schemas, unknown command tags, and wrong arities are rejected. Single requests have at most 4,096 commands. Batches contain at most 256 requests and 16,384 commands in total. Input files are regular nonsymlink files of at most 4 MiB. The endpoint uses arrays; object-shaped commands and additional object fields are rejected.

## Run the Python and Lean endpoints

From the project root:

```bash
python3 tools/observation_recorder.py examples/observation_recorder/complete.json
python3 tools/run_recorder_lean.py examples/observation_recorder/complete.json
```

The Lean command requires `AVOC_LEAN_KIT` and a compiled `tools/RecorderMain.olean`, as described in the release reproduction guide. Both produce the same parsed JSON format. The wrapper has a default 180 second timeout and a maximum of 300 seconds.

The optional registry maps natural-number keys injectively to exact protected nine-field quote identities:

```bash
python3 tools/observation_recorder.py examples/observation_recorder/complete.json --registry examples/observation_recorder/registry.json
```

This attaches `calibration_events` in the inherited parser's format. Every completed key must be registered. Repeated registry keys and two keys mapped to the same protected identity are rejected. Any pending operation blocks export globally. The adapter is syntactic: `evidence_id` is a deterministic label for a recorder terminal record, not a checker certificate or signature. The caller still supplies genuine checked outcomes, authentic complete input, fixed identity meaning, and any statistical assumptions. This command does not issue a policy or a plan.

## Bounded implementation evidence

`checks/test_observation_recorder.py` compares the list-based production reducer with a separate dictionary lifecycle automaton. It enumerates all 69,905 command words of lengths zero through four over two IDs, two keys, and sixteen commands. It also checks twelve focused scenarios covering longer replay chains, reversed completion order, global pending state, and conflicting suffixes.

With `--lean`, the test invokes the actual Lean endpoint on all 4,369 words of lengths zero through three, plus the twelve focused scenarios, for 4,381 exact parsed-JSON comparisons. Additional checks cover structural and resource rejections, accepted resource boundaries, pure reducer behavior, registry injectivity, missing registry keys, pending export rejection, actual host CLI behavior, and compatibility with the inherited calibration parser. The synthetic complete fixture produces a two-report prefix with one success and retains a fault without counting it as a rejection.

The canonical bounded-run record is `results/v0.41.0/oracle_run/manifest.json`, with its contract in `examples/observation_recorder/contract.json`. The final release gate pins its declared input and result hashes. Development outputs are retained separately. These finite checks do not prove universal Python/Lean equivalence. The uniform Lean lifecycle and reveal statements, and their exact assumptions, are in the formal recorder modules.

The raw recorder accepts caller-supplied terminal statuses. It cannot determine whether a report equals the next latent stream bit. The formal reveal theorem applies to a constructed model whose fresh accepted reports are generated from that next bit. It does not establish that arbitrary raw input comes from the constructed model, and no passing parser or test establishes this correspondence for a real process.
