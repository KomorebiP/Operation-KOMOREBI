module prism_psm_top #(
  parameter int CMD_BITS = 256,
  parameter int GEN_W = 24
) (
  input  logic                 clk,
  input  logic                 rst_n,
  input  logic [CMD_BITS-1:0]  command_in,
  input  logic                 command_valid,
  output logic                 command_ready,
  output logic                 commit_pulse,
  output logic                 replay_pulse,
  output logic                 abort_pulse
);
  // Boundary skeleton only. This top-level intentionally exposes the semantic
  // partition that must remain stable while execution engines evolve.
  logic [GEN_W-1:0] consumed_generation;
  logic [GEN_W-1:0] current_generation;
  logic             generation_current;
  logic             provisional_valid;
  logic             cert_done;
  logic             cert_pass;
  logic             no_uncorrectable_fault;
  logic             dependencies_valid;
  logic             retryable_failure;

  assign command_ready = 1'b1;

  // Placeholder extraction consistent with the candidate command packing.
  // Replace with typed package unpacking once the ABI bit allocation freezes.
  assign consumed_generation = command_in[103:80];

  // Prototype tie-offs. Real blocks are deliberately not faked here.
  assign current_generation      = consumed_generation;
  assign provisional_valid       = command_valid;
  assign cert_done               = command_valid;
  assign cert_pass               = 1'b1;
  assign no_uncorrectable_fault  = 1'b1;
  assign dependencies_valid      = 1'b1;
  assign retryable_failure       = 1'b1;

  prism_generation_guard #(.GEN_W(GEN_W)) u_gen_guard (
    .consumed_generation(consumed_generation),
    .current_generation(current_generation),
    .generation_current(generation_current)
  );

  prism_commit_controller u_commit (
    .clk(clk), .rst_n(rst_n),
    .provisional_valid(provisional_valid),
    .cert_done(cert_done),
    .cert_pass(cert_pass),
    .generation_current(generation_current),
    .no_uncorrectable_fault(no_uncorrectable_fault),
    .dependencies_valid(dependencies_valid),
    .retryable_failure(retryable_failure),
    .commit_pulse(commit_pulse),
    .replay_pulse(replay_pulse),
    .abort_pulse(abort_pulse)
  );
endmodule
