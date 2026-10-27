package prism_descriptor_pkg;
  typedef enum logic [7:0] {
    OP_PLOAD        = 8'h01,
    OP_PSELECT      = 8'h02,
    OP_PSPLIT       = 8'h03,
    OP_PCOARSEN     = 8'h04,
    OP_FFT_STAGE    = 8'h10,
    OP_WAVELET      = 8'h11,
    OP_POLYPHASE    = 8'h12,
    OP_BLK_GEMM     = 8'h20,
    OP_BDLR_APPLY   = 8'h21,
    OP_PMR_PLAN     = 8'h22,
    OP_HANKEL       = 8'h30,
    OP_SVD_SMALL    = 8'h31,
    OP_ROOT_PHASE   = 8'h32,
    OP_BAYES_FIT    = 8'h40,
    OP_GRAPH_RUN    = 8'h50,
    OP_GRAPH_REFINE = 8'h51,
    OP_RESIDUAL     = 8'h60,
    OP_COMMIT       = 8'h61
  } prism_opcode_e;

  typedef enum logic [3:0] {
    REP_EXPLICIT_ARRAY = 4'h0,
    REP_BLOCK          = 4'h1,
    REP_BLOCK_SPARSE   = 4'h2,
    REP_LOW_RANK       = 4'h3,
    REP_BDLR           = 4'h4,
    REP_KRONECKER      = 4'h5,
    REP_SPARSE_CHAIN   = 4'h6,
    REP_TRANSFORM      = 4'h7,
    REP_PACKET_GRAPH   = 4'h8
  } prism_representation_e;

  typedef enum logic [3:0] {
    OUT_APPLY               = 4'h0,
    OUT_COMPRESSED_OPERATOR = 4'h1,
    OUT_FACTOR_GRAPH        = 4'h2,
    OUT_TRANSFORM_PLAN      = 4'h3,
    OUT_EXPLICIT_ARRAY      = 4'h4
  } prism_output_contract_e;

  typedef struct packed {
    prism_opcode_e          opcode;
    logic [11:0]            src_packet;
    logic [11:0]            dst_packet;
    logic [7:0]             atlas_id;
    prism_representation_e  representation;
    prism_output_contract_e output_contract;
    logic [3:0]             precision;
    logic [15:0]            rows;
    logic [15:0]            cols;
    logic [7:0]             rank;
    logic [31:0]            dependency_token;
    logic [63:0]            payload_address;
    logic [63:0]            residual_address;
    logic [3:0]             reserved;
  } prism_command_t;
endpackage
