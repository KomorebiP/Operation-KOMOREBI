from sim.prism1r_reference_model import *

def test_valid_commit():
    cmd = PacketCommand(1, 7, 3, State.PROVISIONAL)
    pred = CommitPredicate(True, True, True, True)
    assert resolve_provisional(cmd, pred).state is State.COMMITTED

def test_stale_generation_never_commits():
    cmd = PacketCommand(1, 7, 3, State.PROVISIONAL)
    pred = CommitPredicate(True, False, True, True)
    assert resolve_provisional(cmd, pred).state is State.REPLAY

def test_fatal_fault_aborts():
    cmd = PacketCommand(1, 7, 3, State.PROVISIONAL)
    pred = CommitPredicate(False, True, False, True)
    assert resolve_provisional(cmd, pred, retryable=False).state is State.ABORTED
