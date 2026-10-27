from __future__ import annotations

import json
import sys


def version(module: object) -> str:
    return str(getattr(module, "__version__", "installed"))


def main() -> int:
    try:
        import arc_agi
        import arcengine
        import komorebi_arc3_offline
    except Exception as exc:
        print(json.dumps({"ok": False, "error": repr(exc)}, indent=2))
        return 2
    print(
        json.dumps(
            {
                "ok": True,
                "python": sys.executable,
                "python_version": sys.version,
                "arc_agi": version(arc_agi),
                "arcengine": version(arcengine),
                "runner": version(komorebi_arc3_offline),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
