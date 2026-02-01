# Research Paper Context

## Paper 1: On verifiable quantum advantage with peaked circuit sampling
**URL**: https://arxiv.org/html/2404.14493v2

### Key Definitions
- **Peaked Circuit**: A unitary $C$ is $\delta$-peaked if there exists a bitstring $s$ such that $|\langle s|C|0^n\rangle|^2 \ge \delta$.
- **Structure**: These circuits are typically constructed as $C = P \cdot R$, where:
    - $R$ is a block of $\tau_r$ layers of **Random Quantum Circuit (RQC)** gates.
    - $P$ is a block of $\tau_p$ layers of **Peaking** gates.
- **Role of $P$**: The parametric block $P$ is trained/chosen to maximize the overlap with a specific target bitstring, effectively "focusing" the scattered amplitude from $R$ into a single peak.

## Paper 2: Heuristic Quantum Advantage with Peaked Circuits
**URL**: https://arxiv.org/html/2510.25838v1

### HQAP Circuit Protocol
The specific construction used in this challenge (HQAP) is more complex:
$$ C = T[R] \triangleright T[U] \triangleright U^\dagger \triangleright P $$
Where:
- $\triangleright$ denotes left-to-right composition.
- $U \triangleright U^\dagger$: A large **Identity Block** inserted to increase depth without changing the unitary.
- $T$: A "scrambling" wrapper consisting of:
    - **Swap**: Qubit permutations.
    - **Sweep**: Variational parameter changes to hide angle correlations between $U$ and $U^\dagger$.
    - **Mask**: Connectivity changes (gate replacements).

### Vulnerabilities & Attack Vectors
1.  **Identity Block Elimination**: The core weakness is the $U \triangleright U^\dagger$ block. If this can be identified and removed, the circuit collapses to a shallow depth ($R \triangleright P$), which is easy to simulate.
2.  **Middle MPO Attack**:
    -   Idea: Insert a rank-1 MPO (Identity) in the *middle* of the circuit and evolve it outwards (forward through $U^\dagger$, backward through $U$).
    -   If the segments are truly inverses, the MPO bond dimension will remain low (rank 1), revealing the hidden identity structure.
3.  **Angle/Connectivity Correlation**:
    -   Despite sweeping, angles in $U^\dagger$ might still correlate with $U$.
    -   Graph isomorphism techniques could potentially identify the qubit permutations (Swaps).
4.  **Circuit Simplification**: Standard Qiskit transpilation might fail due to "bottleneck" swaps, but aggressive simplification routines (like Clifford simplification or template matching) might work.

### Recommended Strategy for Higher Levels (P6-P10)
- **Do not just simulate**: The depth is artificially inflated.
- **Search for Cancellations**: Try to find the "cut point" where $U$ ends and $U^\dagger$ begins (the "middle").
- **De-scramble**: If the permutation can be found, the circuit simplifies massively.

## Tutorial: Breaking Peaked Circuits Classically
**Source**: `tutorial_breaking_peaked_quantum_circuits_classically.ipynb`

### Key Attack Vector: Approximate Transpilation
The tutorial demonstrates that the "obfuscated identity" block ($U \triangleright U^\dagger$) is susceptible to **Approximate Transpilation**:
-   **Technique**: Use Qiskit's transpiler with `approximation_degree < 1.0` (e.g., 0.999) and `optimization_level=3`.
-   **Result**: This allows the transpiler to cancel out gates that are mathematically inverses (or close to it) but might be essentially separated by small numerical noise or logical identity insertions.
-   **Indicator of Success**: A "sudden drop" in gate depth (e.g., removing whole layers of `RX`, `RY`, `CZ`) indicates the identity block has been collapsed.

### Practical Steps for Problems
1.  **Load Circuit**: `qc = QuantumCircuit.from_qasm_file('P#.qasm')`
2.  **Transpile with Approximation**:
    ```python
    qc_tr = transpile(qc,
                      basis_gates=set(qc.count_ops()),
                      approximation_degree=0.99, # Allow 1% error to catch identity cancellations
                      optimization_level=3)
    ```
3.  **Check Depth**: Compare `qc.depth()` vs `qc_tr.depth()`. If significantly smaller, simulate `qc_tr`.

# Additional Structural Insights (ArXiv:2510.25838v1)

## "Middle MPO Attack"
The paper discusses a "Middle MPO Attack" for circuits constructed as $U \triangleright U^{\dagger}$ (random unitary followed by its adjoint).
- **Concept:** Start with a rank-1 MPO initialized to Identity in the *middle* of the circuit.
- **Execution:** Jointly evolve gates on either side (from the middle outwards).
- **Result:** If the circuit is indeed $U U^{\dagger}$, the MPO remains low-rank (Identity) throughout the process.
- **Countermeasures:** The paper suggests "sweeping, masking, and applying permutations" prevents this attack. **However**, for our P9 challenge, if such defenses are weak or absent, this MPO technique could aggressively compress the circuit.

## Structural Correlation Attacks
- **Angle Correlation:** In standard random circuits, angles in $U^{\dagger}$ mirror $U$. Tensor patch optimization can hide this, but if the sweeping is insufficient, correlations remain.
- **Connectivity Correlation:** Attackers can solve graph isomorphism on the gate connectivity graph to identify how qubits effectively map to each other, potentially undoing permutations.

## Transpiler Simplifications
- A "sanity check" involves testing if standard transpilers (like Qiskit's) can simplify the identity block.
- Swap transformations act as "bottlenecks," preventing full simplification.
- **Implication for P9:** If P9 is a peaked circuit (pseudo-identity or targeted unitary), standard transpilation might fail, but *targeted* simplification (like finding the "bottleneck" swaps) could unravel it.

## Takeaway for P9 Solver
- **Trotter/Layered Structure:** The user suspects a Trotter-like structure. If P9 is $P \circ R$ (Parametric $\circ$ Random) or similar, identifying the boundary is key.
- **Strategy:** Instead of full simulation, try:
    1.  **Inverse Layer Peeling:** If we suspect the circuit is "peaked" because it's close to Identity or a simple state, try applying inverse layers of hypothesized gates (e.g., inverse Trotter steps) to see if the state complexity (entanglement entropy) decreases.
    2.  **Middle-Out Contraction:** If we can identify a "middle" point (e.g., layer ~40 of 80?), try contracting tensor networks from both ends towards the center to check for low-rank intermediates.