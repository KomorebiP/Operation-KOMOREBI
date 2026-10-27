OPENQASM 3.0;
include "stdgates.inc";
// Three-qubit restricted witness; swap-free primitive-count metric
qubit[3] q;
cx q[0], q[2];
cz q[1], q[2];
cx q[2], q[0];
cx q[0], q[2];
cx q[0], q[1];
cx q[1], q[0];
cx q[0], q[1];
