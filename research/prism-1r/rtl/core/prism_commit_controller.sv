module prism_commit_controller (
  input  logic clk,
  input  logic rst_n,
  input  logic provisional_valid,
  input  logic cert_done,
  input  logic cert_pass,
  input  logic generation_current,
  input  logic no_uncorrectable_fault,
  input  logic dependencies_valid,
  input  logic retryable_failure,
  output logic commit_pulse,
  output logic replay_pulse,
  output logic abort_pulse
);
  logic allow_commit;

  always_comb begin
    allow_commit = cert_pass && generation_current &&
                   no_uncorrectable_fault && dependencies_valid;
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      commit_pulse <= 1'b0;
      replay_pulse <= 1'b0;
      abort_pulse  <= 1'b0;
    end else begin
      commit_pulse <= 1'b0;
      replay_pulse <= 1'b0;
      abort_pulse  <= 1'b0;

      if (provisional_valid && cert_done) begin
        if (allow_commit)
          commit_pulse <= 1'b1;
        else if (retryable_failure && no_uncorrectable_fault)
          replay_pulse <= 1'b1;
        else
          abort_pulse <= 1'b1;
      end
    end
  end
endmodule
