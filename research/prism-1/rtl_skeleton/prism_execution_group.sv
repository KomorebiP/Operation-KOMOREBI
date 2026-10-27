module prism_execution_group #(
  parameter int COMMAND_W = 256,
  parameter int DATA_W = 32
) (
  input  logic                 clk,
  input  logic                 rst_n,
  input  logic                 issue_i,
  input  logic [COMMAND_W-1:0] command_i,
  output logic                 ready_o,
  output logic                 provisional_valid_o,
  output logic [31:0]          completion_token_o
);
  assign ready_o = 1'b1;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      provisional_valid_o <= 1'b0;
      completion_token_o <= '0;
    end else begin
      provisional_valid_o <= issue_i;
      if (issue_i) begin
        completion_token_o <= command_i[99:68];
      end
    end
  end
endmodule
