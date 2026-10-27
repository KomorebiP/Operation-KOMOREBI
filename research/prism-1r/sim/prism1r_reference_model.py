from dataclasses import dataclass, replace
from enum import Enum, auto

class State(Enum):
    QUEUED = auto()
    READY = auto()
    DISPATCHED = auto()
    PROVISIONAL = auto()
    CERTIFIED = auto()
    COMMITTED = auto()
    REPLAY = auto()
    ABORTED = auto()

@dataclass(frozen=True)
class CommitPredicate:
    cert_pass: bool
    generation_current: bool
    no_uncorrectable_fault: bool
    dependencies_valid: bool

    @property
    def allowed(self) -> bool:
        return all((self.cert_pass, self.generation_current,
                    self.no_uncorrectable_fault, self.dependencies_valid))

@dataclass(frozen=True)
class PacketCommand:
    packet_id: int
    consumed_generation: int
    certificate_id: int
    state: State = State.QUEUED

class CommitError(RuntimeError):
    pass

def resolve_provisional(cmd: PacketCommand, pred: CommitPredicate,
                        retryable: bool = True) -> PacketCommand:
    if cmd.state is not State.PROVISIONAL:
        raise CommitError("commit resolution requires PROVISIONAL state")
    if pred.allowed:
        return replace(cmd, state=State.COMMITTED)
    if retryable and pred.no_uncorrectable_fault:
        return replace(cmd, state=State.REPLAY)
    return replace(cmd, state=State.ABORTED)

def generation_current(consumed: int, current: int) -> bool:
    return consumed == current
