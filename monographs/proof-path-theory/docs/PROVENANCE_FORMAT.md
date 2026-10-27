# Provenance tuple format and migration

Publication edition 1.6.0 includes Python distribution 1.4.0. The only changed
public algorithm is `provenance_digest(*parts)`. Its output remains a 64-character
lowercase SHA-256 hexadecimal digest, but its input encoding is intentionally changed.

## Version 2 contract

Each part must be a Python string consisting of Unicode scalar values. Surrogate
code points U+D800 through U+DFFF are rejected with `ValueError`; this prevents
an escaped surrogate pair from aliasing an actual supplementary Unicode scalar. The ordered tuple is serialized as a JSON
array with `ensure_ascii=True` and separators `(",", ":")`, then encoded as ASCII.
The bytes `b"proof-path-provenance:v2\x00"` precede that array. SHA-256 is applied
to the entire prefixed byte sequence. No Unicode normalization occurs. Empty
strings, zero parts, embedded control characters, order, and tuple boundaries
remain distinct before hashing on this accepted domain. Invalid part types raise `TypeError`.

```python
import hashlib
import json

parts = ("A", "B")
payload = b"proof-path-provenance:v2\x00" + json.dumps(
    list(parts), ensure_ascii=True, separators=(",", ":")
).encode("ascii")
digest = hashlib.sha256(payload).hexdigest()
```

The array parser recovers the original accepted sequence of strings from the payload
following the prefix. This explains why the framing removes the demonstrated
serialization ambiguity. It is not a proof that different byte strings cannot
have the same SHA-256 digest.

## What was wrong with the previous helper

The helper in Python 1.3.0 joined strings with `"\x1f"` before UTF-8 encoding.
The distinct tuples `("A\x1fB", "C")` and `("A", "B\x1fC")` produced the same
serialized bytes. Zero parts and one empty part also produced the same bytes.
No collision between distinct SHA-256 inputs was needed. The new tests reproduce
both defects against the untouched 1.3.0 baseline and pass with 1.4.0.

## Historical records

Do not compare version-1 and version-2 digest strings as though they used the
same format. Store a format marker with every digest, for example
`proof-path-provenance-v1-separator` or `proof-path-provenance-v2-json`.
The hexadecimal digest alone does not identify its format.

Preserve old records with their old version. When the original tuple is available,
compute its new digest and append a migration record linking both formats to that
same tuple. A new digest cannot in general be computed from an old digest alone.
Do not overwrite a historical digest while leaving its format marker unchanged.
A legacy record with unknown original tuple boundaries remains ambiguous.

The independent `LedgerSnapshot.digest()` method is unchanged. Its canonical JSON
payload has a different contract, which can intentionally normalize distinctions
in arbitrary metadata. Do not assume injectivity on every possible Python object.
File manifests also remain ordinary SHA-256 hashes of the delivered raw files.

## Verification scope

The tests exercise 2,801 ordered tuples of up to four parts drawn from seven
strings, including empty, control-character, and distinct Unicode forms. They
check payload round trips and the observed digest distinctions in that finite
set. They do not establish universal cryptographic collision resistance.
