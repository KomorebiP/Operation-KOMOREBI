# PRISM-1 RTL boundary modules

These files define control and interface boundaries for the final updated architecture. They are not production RTL. No HDL simulation, synthesis, timing, formal verification, or place-and-route result is claimed.

## Modules

- `prism_descriptor_pkg.sv` defines opcodes and packed records
- `prism_command_fifo.sv` buffers commands
- `prism_token_scoreboard.sv` tracks dependency tokens
- `prism_packet_directory.sv` tracks packet representation and state
- `prism_representation_router.sv` chooses an execution form
- `prism_psm_scheduler.sv` issues packet warps to execution groups
- `prism_execution_group.sv` defines one matrix and vector execution boundary
- `prism_residual_accumulator.sv` accumulates a wide residual
- `prism_commit_controller.sv` chooses commit, replay, or abort
- `prism_tile_shell.sv` remains a compatibility wrapper for staged bring-up
- `prism_top.sv` defines the queue-facing top-level shell

The next hardware milestone is a bit-accurate FPGA Packet Streaming Multiprocessor using the same descriptor and Packet IR contracts.
