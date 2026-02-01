# iQuHACK 2026 - BlueQubit Challenge Walkthrough

We have successfully tackled the majority of the BlueQubit quantum circuit challenges using a combination of local simulation, cloud-based MPS, and structural factoring.

## Final Status
- **Solved**: P1, P2, P3, P4, P7, P8.
- **In Progress**: P5 (Simulating locally with high precision).
- **Research Phase**: P6, P9, P10 (Deep circuits requiring advanced de-obfuscation).

## Key Highlights

### 1. Factoring (P7, P8)
By analyzing the qubit interaction graph, we discovered that P7 and P8 were composed of disconnected clusters. This allowed us to solve them perfectly despite their large total qubit counts (46 and 72).

```python
# From scripts/check_connectivity.py
G = nx.Graph()
for instr in qc.data:
    if len(instr.qubits) == 2:
        G.add_edge(instr.qubits[0]._index, instr.qubits[1]._index)
# Found independent components of size < 30
```

### 2. Matrix Product State (P4)
For the 40-qubit P4 circuit, local statevector simulation was impossible. We used the Matrix Product State (MPS) method with a bond dimension of 64 to find the peak bitstring with high confidence.

### 3. Cloud Simulation (P3)
P3 (30 qubits) was solved using the BlueQubit Cloud CPU backend, providing a reliable baseline for the rest of the challenge.

## Organization
The project has been organized for clarity:
- `solutions/`: Operational scripts for solved problems.
- `scripts/`: Analysis tools (angle distribution, symmetry mapping, boundary search).
- `solutions.md`: A summary table of all obtained bitstrings.

## Future Recommendations
### 4. Structural De-Scrambling (P9)
For P9 (Grand Summit), we identified an "Obfuscated Identity" structure:
- **Zero-Invariant Core**: The middle block (Layers 40-52) maps $|0\rangle \to |0\rangle$ deterministically, simplifying to an identity on the computational basis ground state.
- **Outer Periodicity**: The outer layers exhibit strict Period-2 connectivity, allowing for efficient compression.
- **Scrambling Map**: Global isomorophism analysis revealed a permutation $S$ connecting the two halves of the circuit.
By replacing the complex Core with the permutation $S$, we reduced the problem to simulating two periodic outer blocks, which is tractable with MPS.

## Future Recommendations
For P6 and P10, similar structural attacks should be prioritized over brute-force simulation. Look for:
1.  **Connectivity Periodicity**: Repeating layer patterns (Trotterization).
2.  **Rational Parameters**: Layers with $\pi/2$ or $\pi$ multiples often indicate Clifford frames.
3.  **Core Invariants**: Simulate sub-blocks on $|0\rangle$ to check for trivial action.

---

*Thank you for the collaboration during iQuHACK 2026!*
