# External Dependencies

The release contains no third-party model weights and no copy of the target repository.

## Reviewed repository

```text
connordilgren/are-lrms-easily-interpretable
commit 32f413d8d55239d9bc54bb6b6ec37b0630891ed4
```

Reviewed source objects:

| Object | Path | Git blob SHA |
|---|---|---|
| Multimode wrapper | `models/multimode_coconut/multimode_coconut_model.py` | `d0b353cd78f98ab7aae0d20ce4e8859d9fd9958e` |
| Coconut latent runtime | `src_coconut_multimode/coconut.py` | `646acb08f149afec075eefb212c8aa1f3ac8ceda` |
| PrOntoQA test data | `data/prontoqa_test.json` | `7222832226883a545328f2398dc4976b1bb85c7d` |
| Declared requirements | `requirements.txt` | `4a63ea4b92f0dd565f5d632241e36299695237e4` |

## Target checkpoint

```text
repository: connordilgren/gpt2-prontoqa-multimode-coconut
file: checkpoint_37
```

The setup script downloads the raw checkpoint file and the GPT-2 base model. The real pre-audit seal records the downloaded checkpoint's complete SHA-256.

## Dependency pinning

`requirements-real.txt` matches the external repository's exact PyTorch and Transformers pins where declared:

```text
torch==2.5.1
transformers==4.46.2
peft==0.15.2
```

Using another dependency stack is an implementation-foreign replication and requires a separate replay tolerance and receipt.

## Licensing

Users must comply with the external repository, checkpoint, base-model, and dataset licenses. This SRIC package does not alter or supersede those terms.
