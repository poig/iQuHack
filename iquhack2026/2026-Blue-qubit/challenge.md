Loading Circuits

Try to crack these circuits in .qasm2 format - they grow in difficulty and points 📈

Crack = find the peak bitstring that has the max amplitude and stands out from the rest of amplitudes! 

    To submit the peak bitstring use the submission tab 👆

    We will count both the peak bitstring and its reverse as correct (so you don’t have to worry about bit ordering)

    You can use the below script to load .qasm2 files in qiskit 👇

from qiskit import QuantumCircuit

qc = QuantumCircuit.from_qasm_file('P1.qasm')

Problem 1: Little Dimple 🫧

qubits: 4

Points: 10

This circuit is intentionally simple — inspect the gates and their order carefully. The peak bitstring can be inferred directly from the visual structure without running any simulator.
 

Download problem circuit:
P1_little_peak.qasm
Problem 2: Small Bump 🪨

qubits: 20

Points: 20

A full classical statevector simulation on a CPU is sufficient here. Try running the circuit end-to-end and inspect the output amplitudes to identify the dominant bitstring.

Download problem circuit:
P2_small_bump.qasm
Problem 3: Tiny Ripple 🌊

qubits: 30

Points: 30

Similar to the previous challenge, brute-force classical simulation is still viable. Focus on extracting the highest-probability outcome from the final state rather than optimizing compilation.

Download problem circuit:
P3_tiny_ripple.qasm
Problem 4: Gentle Mound 🌿

qubits: 40

Points: 40

The circuit size starts pushing statevector limits, but its depth and entanglement remain manageable. Use an MPS simulator to efficiently approximate the distribution and locate the peak.
 

Download problem circuit:
P4_gentle_mound.qasm
Problem 5: Soft Rise 🌄

qubits: 50

Points: 50

If your simulator returns a near-uniform  flat distribution, the circuit is likely highly entangling or scrambling. Increase bond dimension, sample multiple runs and use the fact that the high signal of the peak bitstring can be “hidden” in the flat distribution.

Download problem circuit:
P5_soft_rise.qasm
Problem 6: Low Hill ⛰️

qubits: 60

Points: 60

Direct simulation becomes impractical here. Instead, search for canceling gates and simplifying the circuit before simulating it. Qiskit has good tools for approximate transpilation and simplification of circuits.

Download problem circuit:
P6_low_hill.qasm
Problem 7: Rolling Ridge 🏞️

qubits: 46

Points: 70

This circuit can be decomposed into smaller subcircuits. Analyze qubit interaction graphs and factor the problem into parts before recombining the results.

Download problem circuit:
P7_rolling_ridge.qasm
Problem 8: Bold Peak 🏜

qubits: 72

Points: 80

Reuse decomposition and compilation strategies, but expect fewer obvious simplifications. You may need iterative refinement.

Download problem circuit:
P8_bold_peak.qasm
Problem 9: Grand Summit 🏔️

qubits: 56

Points: 90

This challenge blends multiple patterns from earlier problems. Combine visual inspection, partial simulation, decomposition, and compilation tricks to expose the hidden bias toward the peak bitstring.

Download problem circuit:
P9_grand_summit.qasm
Problem 10: Eternal Mountain 🗻

qubits: 56

Points: 100

Use everything you learned in previous problems and try to solve the final circuit!

Download problem circuit:
P10_eternal_mountain.qasm