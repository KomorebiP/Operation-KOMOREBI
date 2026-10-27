module prism_representation_router (
  input  logic       valid_i,
  input  logic [3:0] representation_i,
  input  logic [3:0] output_contract_i,
  output logic [2:0] engine_o,
  output logic       materialize_o,
  output logic       valid_o
);
  localparam logic [2:0] ENG_GENERIC   = 3'd0;
  localparam logic [2:0] ENG_MATRIX    = 3'd1;
  localparam logic [2:0] ENG_FACTOR    = 3'd2;
  localparam logic [2:0] ENG_TRANSFORM = 3'd3;
  localparam logic [2:0] ENG_SOLVER    = 3'd4;
  localparam logic [2:0] ENG_GRAPH     = 3'd5;

  always_comb begin
    valid_o = valid_i;
    materialize_o = (output_contract_i == 4'h4);
    unique case (representation_i)
      4'h1, 4'h2: engine_o = ENG_MATRIX;
      4'h3, 4'h4, 4'h5, 4'h6: engine_o = ENG_FACTOR;
      4'h7: engine_o = ENG_TRANSFORM;
      4'h8: engine_o = ENG_GRAPH;
      default: engine_o = ENG_GENERIC;
    endcase
  end
endmodule
