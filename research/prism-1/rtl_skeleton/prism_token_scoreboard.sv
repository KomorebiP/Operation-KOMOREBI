module prism_token_scoreboard #(
  parameter int TOKENS = 256
) (
  input  logic                          clk,
  input  logic                          rst_n,
  input  logic                          clear_token_valid,
  input  logic [$clog2(TOKENS)-1:0]     clear_token,
  input  logic                          set_token_valid,
  input  logic [$clog2(TOKENS)-1:0]     set_token,
  input  logic [$clog2(TOKENS)-1:0]     query_token,
  output logic                          query_ready
);
  logic [TOKENS-1:0] ready_bits;

  assign query_ready = ready_bits[query_token];

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      ready_bits <= '0;
    end else begin
      if (clear_token_valid) begin
        ready_bits[clear_token] <= 1'b0;
      end
      if (set_token_valid) begin
        ready_bits[set_token] <= 1'b1;
      end
    end
  end
endmodule
