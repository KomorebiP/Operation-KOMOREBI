"""Embedded source provenance for installed development releases.

The experiment runner hashes live files when it is executed from a complete
source checkout.  Wheels do not contain the project tests or ``pyproject.toml``,
so the build embeds their release hashes here for installed-mode receipts.
"""

from __future__ import annotations


V0_10_DEV2_SOURCE_HASHES: dict[str, str] = {
    "src/rrct/adaptive_feedback_experiment.py": "cb78d19ebbd992ff9c5d56f547966650c719df281ecb8e3800ee4ef8d3ec71aa",
    "src/rrct/__init__.py": "2adf8bf2aceb8298b823412b9e2cc9aface88e9794abd314853983cb6018e41e",
    "src/rrct/agent.py": "70431dab75fa8b961496ac0174bb775a290433d53eabe35e1484821b4ff0b39a",
    "src/rrct/components.py": "69cdb3cb55f18482d25556cec8e6c7c02d883d7edaedf2eab72f9d65d36893f1",
    "src/rrct/dynamics.py": "2218b2e48b7dba79243fa3f71067cf4710ac18ec67b2a5e5326238880eaea4f7",
    "src/rrct/feedback.py": "8acb14e8eaa3ca015df37a4a7ae69fa0c06de17fb51b5479a778317ad4f344a4",
    "src/rrct/environment.py": "dbb6e7a1f81a9a8f0bd01dfd5b10c35908f8751cf78640ca67430f46b60cbf66",
    "src/rrct/learning.py": "67e96a3438a97a040c2d25157dec8ef0ab0f020727956e3d8b436bef0559f91b",
    "src/rrct/_version.py": "6d46f28d7affd36bad001c252e837d871a20db7dfb48a126dd07e30389d25cc4",
    "tests/test_v10_adaptive_feedback.py": "7ce50ea0a8f6b0b9ab2d3fadbf9b486025405856e4d83ee5251cbcff17d0ccbf",
    "tests/test_v10_adaptive_feedback_experiment.py": "fe8027e71aadc96655edd6d4fdb990bd42b9bfcb16c67de54e2c61472c7c67a9",
    "pyproject.toml": "adb591890ce903a70f116b17167e33ac55e48573c7d7a8bb5c019f575b84877b",
}
