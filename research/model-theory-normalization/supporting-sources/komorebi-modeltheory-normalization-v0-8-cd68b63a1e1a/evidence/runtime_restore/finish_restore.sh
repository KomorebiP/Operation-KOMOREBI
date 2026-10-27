#!/bin/bash
set -o pipefail
D=/mnt/data/model_v03_work
# Fully extracted files retain their historical mtime; remove any interrupted payload.
find "$D/runtime" -type f -newer "$D/runtime_start.txt" -print -delete > "$D/runtime_incomplete_removed.txt"
(for f in /mnt/data/lean_restore_parts/Lean_Compact_0{1,2,3,4,5}.zip; do unzip -p "$f"; done) | xz -dc -T4 | tar --skip-old-files -x -C "$D/runtime"
s=$?
printf '{"exit_code":%d,"finished_at":"%s"}\n' "$s" "$(date -u +%FT%TZ)" > "$D/runtime_restored.json"
exit $s
