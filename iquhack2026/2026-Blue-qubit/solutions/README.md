# iQuHACK 2026 - BlueQubit Challenge Solutions

This document summarizes the results for the BlueQubit quantum circuit challenges.

## Solved Problems

| Problem | Qubits | Bitstring | Method |
| :--- | :--- | :--- | :--- |
| **P1** | 4 | `1001` | Exact Statevector |
| **P2** | 20 | `11000001000100011000` | Exact Statevector |
| **P3** | 30 | `001110001111101100001101010001` | BlueQubit Cloud (CPU) |
| **P4** | 40 | `1011011000101000010011001110100001010110` | Local MPS (BD=64) |
| **P5** | 50 | `01101000100100001010101011100000010111100011111110` | BlueQubit PPS Attack |
| **P6** | 60 | `101000110000100000100111100010101011101001000101100010001000` | Approximate Transpilation (0.99) |
| **P7** | 46 | `0110001011111111110011110001000010011011100000` | Factored (20q + 26q) |
| **P8** | 72 | `101111100101111000100010110001011101110011100011110000100111010010001010` | Factored (22q + 24q + 26q) |
| **P10** | 56 | `00111111100000110001010111111001011101100001100100010010` | Hybrid PyZX + Approx + MPO |

## Pending Challenges

| Problem | Status | Solver Running |
| :--- | :--- | :--- |
| **P9** | **Running** (Iterative Annealing) | `solve_iterative.py` (PyZX <-> Qiskit Loop) |
| **Bitcoin P1** | **Pending** | - |


## Methodology

### 1. Factoring
For disconnected circuits (P7, P8), we used a `networkx` graph analysis to identify independent qubit clusters. We then simulated each cluster separately using the BlueQubit SDK or local Aer simulators and concatenated the results.

### 2. Matrix Product State (MPS)
For larger connected circuits (P3, P4), we employed Matrix Product State (MPS) simulation. For P4, a bond dimension of 64 was sufficient to resolve the peak.

### 3. Cloud Execution
We utilized the BlueQubit SDK to run simulations on high-performance cloud backends where local memory was insufficient.

---

### File Organization
- `/solutions`: Contains the primary solver scripts used for the successful submissions.
- `/challenge`: Original QASM circuit files.
