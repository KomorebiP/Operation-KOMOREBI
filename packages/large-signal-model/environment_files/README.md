# Optional local ARC-AGI-3 environments

Downloaded or user-supplied ARC-AGI-3 game sources are intentionally not
tracked in this repository. Place a local environment tree here when using
the optional ARC integration. The expected layout is:

```text
environment_files/
  <game-prefix>/
    <content-id>/
      metadata.json
      <game-prefix>.py
```

The separate `Komorebi_PR_LASM_Local_ARC3_25_Fixtures.zip` archive from the
handoff can be extracted into the repository root. Git will continue to ignore
the extracted game files.
