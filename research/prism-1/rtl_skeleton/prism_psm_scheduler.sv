module prism_psm_scheduler #(
  parameter int GROUPS = 4
) (
  input  logic                  clk,
  input  logic                  rst_n,
  input  logic                  warp_valid_i,
  input  logic [31:0]           dependency_token_i,
  input  logic [GROUPS-1:0]     group_ready_i,
  output logic                  warp_ready_o,
  output logic [GROUPS-1:0]     group_issue_o,
  output logic [31:0]           issued_token_o
);
  integer i;
  always_comb begin
    warp_ready_o = 1'b0;
    group_issue_o = '0;
    issued_token_o = dependency_token_i;
    for (i = 0; i < GROUPS; i = i + 1) begin
      if (warp_valid_i && !warp_ready_o && group_ready_i[i]) begin
        group_issue_o[i] = 1'b1;
        warp_ready_o = 1'b1;
      end
    end
  end
endmodule
