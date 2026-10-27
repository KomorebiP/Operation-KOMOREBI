module prism_top (
  input  logic         clk,
  input  logic         rst_n,
  input  logic         command_valid,
  input  logic [255:0] command_data,
  output logic         command_ready,
  output logic         completion_valid,
  output logic [31:0]  completion_token
);
  logic fifo_empty;
  logic fifo_full;
  logic [255:0] fifo_data;
  logic fifo_pop;

  prism_command_fifo #(.WIDTH(256), .DEPTH(32)) command_fifo (
    .clk(clk),
    .rst_n(rst_n),
    .push(command_valid && command_ready),
    .push_data(command_data),
    .pop(fifo_pop),
    .pop_data(fifo_data),
    .empty(fifo_empty),
    .full(fifo_full)
  );

  assign command_ready = !fifo_full;
  assign fifo_pop = !fifo_empty;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      completion_valid <= 1'b0;
      completion_token <= '0;
    end else begin
      completion_valid <= fifo_pop;
      if (fifo_pop) begin
        completion_token <= fifo_data[95:64];
      end
    end
  end
endmodule
