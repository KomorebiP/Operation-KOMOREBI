OPENQASM 3.0;
include "stdgates.inc";
// Three-qubit ambient witness; swap-free primitive-count metric
qubit[3] q;
h q[1];
cx q[1], q[2];
cx q[2], q[1];
cx q[2], q[0];
cx q[0], q[2];
h q[0];
