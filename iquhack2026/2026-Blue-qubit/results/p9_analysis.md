# P9 Circuit Analysis: Grand Summit

## Executive Summary
The P9 circuit is an obfuscated peaked circuit of depth 93 on 56 qubits. Our analysis identifies a clear structure composed of periodic outer transformation blocks and a unique, deterministic core.

## Structural Findings
1.  **Outer Blocks (Layers 0-40 and 52-92)**:
    *   Exhibit **Period-2 connectivity symmetry**.
    *   Parameters follow a non-periodic "sweeping" pattern.
    *   Isomorphism analysis confirms a permutation $S$ maps the boundary of the first block (Layer 39) to the second (Layer 53).
2.  **Core Block (Layers 41-51)**:
    *   Functions as a **deterministic operator** on the $|0\rangle$ state ($Core |0\rangle = |0\rangle$).
    *   Contains a central "hinge" at **Layer 46** with irrational (non-Clifford) parameters (~$\pi/3$ and ~$2\pi/3$).
    *   Other core layers (42, 44, 48, 50) use Clifford-like angles ($\pi/2$, $\pi$).

## Invariants and Properties
*   **Zero-State Stability**: The core's preservation of the ground state is a critical invariant. This suggests the circuit is an "Identity on $|0\rangle$" obfuscated by complex scrambling.
*   **Permutation Mapping**: The scrambling map $S$ suggests a $U \triangleright S \triangleright U^\dagger$ structure, where $S$ is a graph-isomorphic permutation that effectively rotates the basis across the core.

## Simulation Insights
*   **PPS Failure**: The Pauli Path Simulator (PPS) returns zero marginals, indicating that the path-interference in such an obfuscated identity is perfectly destructive for truncated path-sums.
*   **MPS Viability**: Low-bond MPS simulation (bond dim 32) captures a partial signal, supporting the "peaked" nature of the circuit.

## Proposed Invariant
The total circuit likely acts as a **Global Identity** ($U_{total} \approx I$) or a **Permuted Identity** ($U_{total} \approx S$). If $|0\rangle$ is preserved throughout, the expected output bitstring is `00...0`.
