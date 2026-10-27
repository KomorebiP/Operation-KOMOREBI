# Reproduce the stationary-separation checkpoint

Python 3.12 and standard-library arithmetic suffice. Run from the extracted root.

Verify all saved bytes and current manifests with `python3 verify_checkpoint.py`.

Current runs are listed in `stationary_separation/CURRENT_EVIDENCE.json`.

The commands below write fresh replay files. They do not overwrite saved evidence.

Working directory: `.`.
```bash
python3 stationary_separation/root/check_actual_reinsertion.py replay_01.json
```

Working directory: `.`.
```bash
python3 stationary_separation/ordinary/check_quadratic_compression.py replay_02.json
```

Working directory: `.`.
```bash
python3 stationary_separation/ordinary/check_projective_reconstruction.py replay_03.json
```

Working directory: `.`.
```bash
python3 stationary_separation/coefficient/check_full_recurrence.py replay_04.json
```

Working directory: `.`.
```bash
python3 stationary_separation/coefficient/integer_shift/check_integer_shift.py replay_05.json
```

Working directory: `.`.
```bash
python3 stationary_separation/contact/check_source_contact.py replay_06.json
```

Working directory: `.`.
```bash
python3 stationary_separation/ordinary/exponential_model/check_exponential_dictionary.py replay_07.json
```

Working directory: `.`.
```bash
python3 stationary_separation/root/check_actual_reinsertion.py replay_08.json
```

Working directory: `.`.
```bash
python3 stationary_separation/ordinary/check_quadratic_compression.py replay_09.json
```

Working directory: `.`.
```bash
python3 stationary_separation/ordinary/check_projective_reconstruction.py replay_10.json
```

Working directory: `.`.
```bash
python3 stationary_separation/ordinary/exponential_model/check_exponential_dictionary.py replay_11.json
```

Inherited proofs and historical runs retain their original status. The parent
ZIP is included unchanged and can be extracted separately for its full context.
The new actual convergence theorem and quadratic reduction do not establish
the remaining nonvanishing assertion.
