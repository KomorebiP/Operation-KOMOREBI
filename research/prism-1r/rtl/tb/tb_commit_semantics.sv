`timescale 1ns/1ps
module tb_commit_semantics;
  logic clk = 0;
  logic rst_n = 0;
  logic provisional_valid, cert_done, cert_pass;
  logic generation_current, no_uncorrectable_fault, dependencies_valid;
  logic retryable_failure;
  logic commit_pulse, replay_pulse, abort_pulse;

  always #5 clk = ~clk;

  prism_commit_controller dut (
    .clk, .rst_n, .provisional_valid, .cert_done, .cert_pass,
    .generation_current, .no_uncorrectable_fault, .dependencies_valid,
    .retryable_failure, .commit_pulse, .replay_pulse, .abort_pulse
  );

  task drive(input logic cp, input logic gc, input logic nf,
             input logic dv, input logic retry);
    begin
      provisional_valid = 1; cert_done = 1; cert_pass = cp;
      generation_current = gc; no_uncorrectable_fault = nf;
      dependencies_valid = dv; retryable_failure = retry;
      @(posedge clk); #1;
    end
  endtask

  initial begin
    provisional_valid=0; cert_done=0; cert_pass=0; generation_current=0;
    no_uncorrectable_fault=0; dependencies_valid=0; retryable_failure=0;
    repeat (2) @(posedge clk); rst_n=1;

    drive(1,1,1,1,1);
    if (!commit_pulse) $fatal("valid command failed to commit");

    drive(1,0,1,1,1);
    if (!replay_pulse || commit_pulse) $fatal("stale generation was not replayed");

    drive(0,1,0,1,0);
    if (!abort_pulse || commit_pulse) $fatal("fatal fault was not aborted");

    $display("PASS: commit semantics smoke test");
    $finish;
  end
endmodule
