module prism_command_fifo #(
  parameter int WIDTH = 256,
  parameter int DEPTH = 16
) (
  input  logic             clk,
  input  logic             rst_n,
  input  logic             push,
  input  logic [WIDTH-1:0] push_data,
  input  logic             pop,
  output logic [WIDTH-1:0] pop_data,
  output logic             empty,
  output logic             full
);
  localparam int ADDR_W = $clog2(DEPTH);
  logic [WIDTH-1:0] mem [0:DEPTH-1];
  logic [ADDR_W:0] write_ptr;
  logic [ADDR_W:0] read_ptr;

  assign empty = write_ptr == read_ptr;
  assign full = write_ptr[ADDR_W] != read_ptr[ADDR_W] &&
                write_ptr[ADDR_W-1:0] == read_ptr[ADDR_W-1:0];
  assign pop_data = mem[read_ptr[ADDR_W-1:0]];

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      write_ptr <= '0;
      read_ptr <= '0;
    end else begin
      if (push && !full) begin
        mem[write_ptr[ADDR_W-1:0]] <= push_data;
        write_ptr <= write_ptr + 1'b1;
      end
      if (pop && !empty) begin
        read_ptr <= read_ptr + 1'b1;
      end
    end
  end
endmodule
