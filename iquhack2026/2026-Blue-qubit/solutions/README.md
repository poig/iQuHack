# iQuHack 2026: Challenge Solutions (P1-P10)

We have successfully cracked all ten circuits in the **BlueQubit / IBM HQAP Challenge** set using advanced circuit simplification and Matrix Product State (MPS) simulation.

## Methodology: "Soft Reduction + MPS"

The solving strategy leverages the fact that these "obfuscated" circuits are mathematically equivalent to much simpler "peaked" units. Our pipeline bypasses the high depth and non-Clifford noise through a three-stage attack:

1.  **PyZX Algebraic Reduction**: We use `zx.simplify.clifford_simp()` to collapse internal identity circuits and cancel redundant gates. For P9/P10, this reduced gate counts from ~5000+ down to < 350.
2.  **Measurement-Basis Transpilation**: We sequence our pipeline to **add measurements before final transpilation**. This allows the Qiskit Level 3 optimizer to aggressively prune logic that doesn't affect the final bitstring.
3.  **Local MPS Simulation**: Using the `matrix_product_state` backend with a Bond Dimension of 128, we resolved the probability peaks that were previously buried under depth.

## Final Results

| Challenge | Circuit Name | Final Bitstring (Peaked Answer) | Peak Confidence |
| :--- | :--- | :--- | :--- |
| **P1** | Little Peak | `1001` | 100% |
| **P2** | Small Bump | `11000001000100011000` | 100% |
| **P3** | Tiny Ripple | `001110001111101100001101010001` | 10.1% |
| **P4** | Gentle Mound | `1011011000101000010011001110100001010110` | 22.1% |
| **P5** | Soft Rise | `01101000100100001010101011100000010111100011111110` | 22.1% |
| **P6** | Low Hill | `101000110000100000100111100010101011101001000101100010001000` | 99.7% |
| **P7** | Rolling Ridge | `0110001011111111110011110001000010011011100000` | 41.2% |
| **P8** | Bold Peak | `101111100101111000100010110001011101110011100011110000100111010010001010` | 22.3% |
| **P9** | Grand Summit | `11011000111011100000101000110001010111100100000101101110` | 41.3% |
| **P10** | Eternal Mountain | `00111111100000110001010111111001011101100001100100010010` | 9.9% |

## How to Run the Solver

To replicate these results or solve new QASM files:

```bash
# Process all circuits in the /challenge folder
python solutions/run_all.py

# Solve a specific circuit with custom bond dimension
python solutions/solve_circuit.py challenge/P9_grand_summit.qasm --bond-dim 256
```

## Special Cases
*   **P6 (Low Hill)**: This circuit responded best to approximate transpilation rather than PyZX. We used `approximation_degree=0.99` to reveal the peak.
*   **Marginal Attack**: For extreme cases where sampling is flat, our `cloud_solver.py` provides a **Marginal Reconstruction** mode that builds the bitstring qubit-by-qubit from expectation values.

---
**Submission Team: poig**
**Status: All Targets Resized and Solved.**
