import pyzx as zx
from qiskit import QuantumCircuit, transpile, qasm2
from qiskit_aer import AerSimulator
import time
import json

TARGETS = {
    # "P9": "challenge/P9_grand_summit.qasm",
    "P10": "challenge/P10_eternal_mountain.qasm"
}

def solve_hybrid(name, path):
    print(f"\n--- Hybrid PyZX + Approx Transpilation for {name} ---")
    
    # 1. PyZX Reduction
    print("  [1] PyZX Simplification...")
    qc_orig = QuantumCircuit.from_qasm_file(path)
    qasm_str = qasm2.dumps(qc_orig)
    g = zx.Circuit.from_qasm(qasm_str).to_graph()
    zx.full_reduce(g)
    circ_reduced = zx.extract_circuit(g)
    
    # Convert back to Qiskit
    qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
    print(f"  PyZX Result: Depth {qc_zx.depth()}, Qubits {qc_zx.num_qubits}")
    n = qc_zx.num_qubits

    # Initialize mappings to identity for now, as no reordering is explicitly applied
    # If a reordering step is added later, this should be updated.
    phys_to_logic_indices = {i: i for i in range(n)}

    # 2. Exact Simulation of Reduced Circuit
    print("  [2] Exact Simulation of PyZX Circuit (MPO)...")
    
    # qc_zx is the reduced circuit.
    # We can simulate it directly.
    sim = AerSimulator(method='matrix_product_state')
    
    # MPO settings for precision vs speed
    sim.set_options(matrix_product_state_max_bond_dimension=128) 
    
    qc_zx.measure_all() # Measure all qubits in qc_zx
    trans_qc = transpile(qc_zx, basis_gates=['u3', 'cx'], optimization_level=3)
    print("circuit depth:", trans_qc.depth())
    job = sim.run(trans_qc, shots=2000)
    result = job.result().get_counts()
    print(dict(sorted(result.items(), key=lambda item: item[1], reverse=True)[:5]))
    best_measurement = max(result, key=result.get)
    
    # Reconstruction
    # best_measurement is bits for [phys_n-1...phys_0] (Qiskit's default big-endian string format)
    # We need to map back to logical.
    
    final_bits = ['?'] * n
    
    # Inverse mapping
    # phys_to_logic_indices maps Physical Line -> Logical Qubit Index
    # Qiskit's measurement string is big-endian: index 0 is the most significant bit (highest qubit index).
    # So, best_measurement[k] corresponds to physical qubit (n-1-k).
    
    for str_idx, bit_val in enumerate(best_measurement):
        phys_idx = n - 1 - str_idx # Physical qubit index corresponding to this character
        
        # Which logical qubit is at this physical location?
        # If no reordering, phys_idx == logic_idx
        logic_idx = phys_to_logic_indices[phys_idx]
        
        # Place the bit value into the final_bits array at the correct logical position
        # final_bits is ordered [logic_0, logic_1, ..., logic_n-1]
        final_bits[logic_idx] = bit_val
        
    # The problem statement for P10 expects the output string to be [q_N-1 ... q_0]
    # If final_bits is [q_0, q_1, ..., q_N-1], then we need to reverse it.
    final_bitstring = "".join(reversed(final_bits)) # To satisfy "P10" format (q0 rightmost)
    
    print(f"  [RESULT] {final_bitstring} (Count: {result[best_measurement]})")
    
    # Save
    with open(f"results/hybrid_solution_{name}.json", "w") as f:
        json.dump({"bitstring": final_bitstring}, f)

if __name__ == "__main__":
    for name, path in TARGETS.items():
        solve_hybrid(name, path)

