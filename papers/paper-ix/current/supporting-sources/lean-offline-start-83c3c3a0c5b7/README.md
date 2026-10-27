# Komorebi P. Portable Lean: offline bundle

The large single-file save failed during preparation. The same verified archive
is supplied here as seven ZIP parts, plus this small assembly kit.

1. Download `Lean_Offline_01.zip` through `Lean_Offline_07.zip` to one folder.
2. Extract this starter ZIP into that same folder. Leave the seven part ZIPs intact.
3. Open a terminal in the folder and run:

```bash
python3 assemble.py --extract
```

Use `python` instead of `python3` on Windows. Assembly uses Python 3.9+ standard
libraries. Extraction and the offline Lean runtime require **Linux x86_64 / WSL2**,
plus `tar`, `zstd`, Bash, Python and Git. You can assemble on Windows, then extract
and run the result inside WSL. For native Windows, use the separate Windows setup
ZIP, which needs internet for its initial downloads and was not executed here.

If the files are elsewhere, pass `--parts /path/to/downloads`.
Use `--verify-only` to check all seven parts without writing another archive.
Each part's ZIP CRC and SHA-256 are checked, followed by the combined SHA-256.
Existing output archives and extraction directories are not overwritten.

The result is `Komorebi_Portable_Lean_4.34.0-rc2_Linux_Offline.tar.zst`.
It is 2.9 GB compressed and about 11 GB extracted. Allow **20 GB free space**
while retaining the parts, assembled archive and extracted directory together.

Inside the extracted `Komorebi_Portable_Lean_4.34.0-rc2` folder, run:

```bash
bash run.sh verify
bash run.sh check workspace/PortableCheck.lean
```

The kit contains Lean and Lake 4.34.0-rc2, all nine pinned dependency repositories,
and the full mathlib cache at `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
Its 23 Linux checks passed, including relocation to a path containing spaces,
full mathlib import, actual PRSC VI algebra compilation, rejection of false
proofs and placeholders, and safe exact-pin cache attachment.
It does not claim to finish remaining Paper VI proofs.

The extracted README explains attaching the cache to matching PRSC projects.
No Elan setup, administrator access or permanent PATH edits are required by
this kit. WSL and operating-system prerequisites are not included.
