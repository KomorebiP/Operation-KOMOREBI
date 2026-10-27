module prism_packet_directory #(
  parameter int PACKETS = 4096,
  parameter int ADDR_W = 64
) (
  input  logic                          clk,
  input  logic                          rst_n,
  input  logic                          write_valid,
  input  logic [$clog2(PACKETS)-1:0]    write_packet,
  input  logic [ADDR_W-1:0]             write_address,
  input  logic                          write_provisional,
  input  logic                          write_committed,
  input  logic [$clog2(PACKETS)-1:0]    query_packet,
  output logic [ADDR_W-1:0]             query_address,
  output logic                          query_valid,
  output logic                          query_provisional,
  output logic                          query_committed
);
  logic [ADDR_W-1:0] address_mem [0:PACKETS-1];
  logic [PACKETS-1:0] valid_bits;
  logic [PACKETS-1:0] provisional_bits;
  logic [PACKETS-1:0] committed_bits;

  assign query_address = address_mem[query_packet];
  assign query_valid = valid_bits[query_packet];
  assign query_provisional = provisional_bits[query_packet];
  assign query_committed = committed_bits[query_packet];

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      valid_bits <= '0;
      provisional_bits <= '0;
      committed_bits <= '0;
    end else if (write_valid) begin
      address_mem[write_packet] <= write_address;
      valid_bits[write_packet] <= 1'b1;
      provisional_bits[write_packet] <= write_provisional;
      committed_bits[write_packet] <= write_committed;
    end
  end
endmodule
