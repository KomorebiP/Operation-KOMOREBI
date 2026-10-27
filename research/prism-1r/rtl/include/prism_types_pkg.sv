package prism_types_pkg;
  parameter int PSC_BITS = 256;

  typedef enum logic [2:0] {
    ST_QUEUED      = 3'd0,
    ST_READY       = 3'd1,
    ST_DISPATCHED  = 3'd2,
    ST_PROVISIONAL = 3'd3,
    ST_CERTIFIED   = 3'd4,
    ST_COMMITTED   = 3'd5,
    ST_ABORTED     = 3'd6
  } prism_cmd_state_e;

  // Candidate v0 command envelope. Bit allocation is deliberately marked
  // provisional until synthesis and firmware packing studies are complete.
  typedef struct packed {
    logic [7:0]  opcode;
    logic [7:0]  flags;
    logic [7:0]  abi_version;
    logic [7:0]  format;
    logic [31:0] packet_id;
    logic [31:0] src_desc;
    logic [31:0] dst_desc;
    logic [23:0] dependency_token;
    logic [23:0] generation;
    logic [23:0] certificate_id;
    logic [55:0] payload_or_imm;
  } prism_seed_cmd_t;

  typedef struct packed {
    logic        cert_pass;
    logic        generation_current;
    logic        no_uncorrectable_fault;
    logic        dependencies_valid;
  } prism_commit_predicate_t;

  function automatic logic commit_allowed(prism_commit_predicate_t p);
    return p.cert_pass && p.generation_current &&
           p.no_uncorrectable_fault && p.dependencies_valid;
  endfunction
endpackage
