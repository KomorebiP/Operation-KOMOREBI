module prism_generation_guard #(
  parameter int GEN_W = 24
) (
  input  logic [GEN_W-1:0] consumed_generation,
  input  logic [GEN_W-1:0] current_generation,
  output logic             generation_current
);
  always_comb begin
    generation_current = (consumed_generation == current_generation);
  end
endmodule
