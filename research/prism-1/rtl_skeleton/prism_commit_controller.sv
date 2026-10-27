module prism_commit_controller #(
  parameter int RESIDUAL_W = 96
) (
  input  logic                     clk,
  input  logic                     rst_n,
  input  logic                     request_valid,
  input  logic                     dependency_ready,
  input  logic                     kernel_complete,
  input  logic [RESIDUAL_W-1:0]    residual_value,
  input  logic [RESIDUAL_W-1:0]    residual_budget,
  output logic                     commit_valid,
  output logic                     replay_valid,
  output logic                     abort_valid
);
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      commit_valid <= 1'b0;
      replay_valid <= 1'b0;
      abort_valid <= 1'b0;
    end else begin
      commit_valid <= 1'b0;
      replay_valid <= 1'b0;
      abort_valid <= 1'b0;
      if (request_valid) begin
        if (!dependency_ready || !kernel_complete) begin
          abort_valid <= 1'b1;
        end else if (residual_value <= residual_budget) begin
          commit_valid <= 1'b1;
        end else begin
          replay_valid <= 1'b1;
        end
      end
    end
  end
endmodule
