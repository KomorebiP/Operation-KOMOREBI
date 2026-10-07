# Source relocation

The frozen Research Preview 1 is preserved under `formal/research-preview-1`.
Its former standalone `komorebi-math/` export is a different component from the
installable mathematical software in the independent `komorebi-math` repository.
Every file in the retained preview remains byte-identical to its source archive.

Run the preview commands from `formal/research-preview-1`, where its sealed
hashes, dependency pins and relative paths retain their original meaning.
The collection workflow runs its checks with that working directory. The manual
Lean replay workflow also directs the bootstrap action to the relocated package.

Historical preview documents and its original upload helper retain their old
standalone destination as provenance. Use the collection instructions and the
three-repository build record for the current layout. Do not use the historical
preview helper to upload the installable mathematical library.

The root collection workflow checks source and artifact identity. A passing
result does not replay Lean proofs. The manual replay workflow performs that
separate check when its pinned toolchain and dependencies are available.
