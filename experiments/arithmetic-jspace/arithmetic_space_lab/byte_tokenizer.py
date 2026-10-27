from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class ByteTokenizer:
    """Fixed UTF-8 tokenizer whose vocabulary is independent of every dataset split."""

    pad_id: int = 256
    bos_id: int = 257
    sep_id: int = 258
    eos_id: int = 259
    vocab_size: int = 260
    version: str = "utf8-byte-v1"

    def encode(self, text: str) -> list[int]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        return list(text.encode("utf-8"))

    def decode(self, ids: Iterable[int]) -> str:
        values = []
        for token in ids:
            value = int(token)
            if 0 <= value <= 255:
                values.append(value)
            elif value in {self.pad_id, self.bos_id, self.sep_id, self.eos_id}:
                continue
            else:
                raise ValueError(f"token id outside vocabulary: {value}")
        return bytes(values).decode("utf-8", errors="replace")

    def prefix(self, prompt: str) -> list[int]:
        return [self.bos_id, *self.encode(prompt), self.sep_id]

    def sequence(self, prompt: str, completion: str) -> tuple[list[int], list[int], int]:
        if not completion:
            raise ValueError("completion must be nonempty")
        prefix = self.prefix(prompt)
        full = [*prefix, *self.encode(completion), self.eos_id]
        inputs = full[:-1]
        labels = full[1:]
        prompt_position = len(prefix) - 1
        labels[:prompt_position] = [-100] * prompt_position
        if labels[prompt_position] == -100:
            raise AssertionError("first completion token must be supervised")
        return inputs, labels, prompt_position

    def completion(self, ids: Sequence[int]) -> str:
        kept: list[int] = []
        for token in ids:
            value = int(token)
            if value == self.eos_id:
                break
            if 0 <= value <= 255:
                kept.append(value)
        return bytes(kept).decode("utf-8", errors="replace")
