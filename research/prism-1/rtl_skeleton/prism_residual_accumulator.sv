module prism_residual_accumulator #(
  parameter int DATA_W = 32,
  parameter int ACC_W = 96
) (
  input  logic                         clk,
  input  logic                         rst_n,
  input  logic                         clear,
  input  logic                         valid,
  input  logic signed [DATA_W-1:0]     direct_value,
  input  logic signed [DATA_W-1:0]     reconstructed_value,
  output logic signed [ACC_W-1:0]      l1_accumulator
);
  logic signed [DATA_W:0] difference;
  logic signed [DATA_W:0] absolute_difference;

  always_comb begin
    difference = direct_value - reconstructed_value;
    absolute_difference = difference < 0 ? -difference : difference;
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n || clear) begin
      l1_accumulator <= '0;
    end else if (valid) begin
      l1_accumulator <= l1_accumulator + absolute_difference;
    end
  end
endmodule
