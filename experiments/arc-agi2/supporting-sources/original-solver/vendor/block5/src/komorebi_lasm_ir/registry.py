"""Typed operator registry for LASM Program IR v2."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable, Iterable, Mapping

from .types import ValueType


@dataclass(frozen=True)
class OperatorDefinition:
    """One pure or explicitly effect-tagged runtime operator."""

    name: str
    input_types: tuple[ValueType, ...]
    output_type: ValueType
    function: Callable[..., object]
    cost: int = 1
    description: str = ""
    pure: bool = True

    def __post_init__(self) -> None:
        if not self.name or self.name.strip() != self.name:
            raise ValueError("operator names must be nonempty and trimmed")
        if not callable(self.function):
            raise TypeError(f"operator {self.name!r} is not callable")
        if isinstance(self.cost, bool) or int(self.cost) <= 0:
            raise ValueError("operator cost must be a positive integer")

    def signature_record(self) -> dict[str, object]:
        return {
            "name": self.name,
            "inputs": [item.value for item in self.input_types],
            "output": self.output_type.value,
            "cost": int(self.cost),
            "pure": bool(self.pure),
            "description": self.description,
        }


class OperatorRegistry:
    """Immutable, hashable collection of typed operator definitions."""

    def __init__(self, definitions: Iterable[OperatorDefinition]) -> None:
        by_name: dict[str, OperatorDefinition] = {}
        for definition in definitions:
            if definition.name in by_name:
                raise ValueError(f"duplicate operator {definition.name!r}")
            by_name[definition.name] = definition
        self._definitions = MappingProxyType(by_name)

    def resolve(self, name: str) -> OperatorDefinition:
        try:
            return self._definitions[name]
        except KeyError as error:
            raise KeyError(f"unregistered operator {name!r}") from error

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._definitions))

    @property
    def definitions(self) -> tuple[OperatorDefinition, ...]:
        """Definitions in canonical name order for audit and registry extension."""

        return tuple(self._definitions[name] for name in self.names)

    def signature_record(self) -> dict[str, object]:
        return {
            "schema": "komorebi.lasm_operator_registry",
            "schema_version": 1,
            "operators": [self._definitions[name].signature_record() for name in self.names],
        }

    def contract_hash(self) -> str:
        payload = json.dumps(
            self.signature_record(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def __len__(self) -> int:
        return len(self._definitions)

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self._definitions


__all__ = ["OperatorDefinition", "OperatorRegistry"]
