# Block17 source layout

The current diagnostic retains the two tested replacement files in patches/. The authenticated original solver is under supporting-sources/original-solver/. Public evaluation records are under supporting-sources/public-evaluation/, with historical training replay and the original offline handoff in their own supporting directories.

The original and limitfix source versions remain separate. The original public result is 2/120 whole tasks and 2/172 outputs at pass@2. The six-task limitfix diagnostic introduces no new full evaluation score.

The historical restoration scripts describe their original sealed ZIP layout. The directly published source files and SOURCE_SELECTION.json identify the same underlying payloads. For the one compressed evaluation census, run the small restore_large_evidence.py helper beside COMPRESSED_DATA.json before using a script that requires the expanded JSON.
