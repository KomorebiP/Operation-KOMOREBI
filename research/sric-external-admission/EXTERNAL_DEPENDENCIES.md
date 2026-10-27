# External Dependencies

The external assets are intentionally not redistributed.

## Source repository

- `connordilgren/are-lrms-easily-interpretable`
- pinned commit: `32f413d8d55239d9bc54bb6b6ec37b0630891ed4`

The package verifies the wrapper, latent runtime, requirements, and selected dataset Git blobs listed in `external_source_lock.json`.

## Primary checkpoint

- repository: `connordilgren/gpt2-prontoqa-multimode-coconut`
- revision: `4ec759a9f9b8a8e7e1a8d1e3e2d43eef969ac83f`
- file: `checkpoint_37`

## Base model

- repository: `openai-community/gpt2`
- revision: `607a30d783dfa663caf39e06633721c8d4cfcd7e`
- required local files: `config.json`, `generation_config.json`, `model.safetensors`, `merges.txt`, `tokenizer.json`, `tokenizer_config.json`, and `vocab.json`

Version 0.3.2 downloads only this allowlisted payload. Alternate PyTorch, TensorFlow, and Flax weight variants are not acquired.

## Runtime

The isolated real environment pins PyTorch 2.5.1 and Transformers 4.46.2, matching the reviewed external requirements where exact pins were available.

## Secondary planned checkpoint

ProsQA source and checkpoint revisions are recorded in `external_source_lock.json`. They are not executed by the frozen primary v0.3.0 scientific run path or by the v0.3.2 infrastructure patch.
