# Publication gate

No repository or registry was changed while building this handoff. The owner
must choose the intended public license before this can be described as an
open-source release. The inherited LICENSE still reserves all rights.

Before creating a public release, replace that license only with an explicitly
authorized license and update pyproject.toml and the documentation consistently.
Then run the prepared CI matrix, the repository checks and the clean distribution
checks. Official ARC results are not a prerequisite for the declared core signal
scope, but must not be claimed without the corresponding runtime execution.

The release workflow builds on a tag but does not publish automatically. Its
publication step is gated by an explicit manual invocation and the license check.
The full preservation handoff contains separate upstream archives and is not the
same object as the clean repository source ZIP. Review third-party companion
licenses before publishing the preservation collection.
