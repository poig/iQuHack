
import pyzx as zx
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import collections
import time

def solve_simplified_mps():
    print("Loading P9 QASM...")
    # Use generic graph conversion then extract_circuit for safety
    g = zx.Circuit.from_qasm_file("challenge/P9_grand_summit.qasm").to_graph()
    zx.full_reduce(g)
    
    print("Extracting simplified circuit from PyZX...")
    # Use extract_circuit, then to_qasm, then Qiskit for robustness
    qc_zx_circuit = zx.extract_circuit(g)
    qasm_str = qc_zx_circuit.to_qasm()
    qc_zx = QuantumCircuit.from_qasm_str(qasm_str)
    
    print(f"Simplified Circuit Stats (Pre-Opt): {len(qc_zx.data)} gates")
    
    # Add measurements
    qc_zx.measure_all()
    
    # MPS Simulation
    # Try Bond Dimension 64 first (fast check)
    sim = AerSimulator(method='matrix_product_state', matrix_product_state_max_bond_dimension=64)
    print("Transpiling for MPS (L3)...")
    # Must use optimization_level=3 to reduce the PyZX output (~10k gates) to ~2.6k
    qc_mps = transpile(qc_zx, sim, optimization_level=3)
    print(f"Final Sim Circuit Gates: {len(qc_mps.data)}")
    
    print("Running MPS Simulation (BD=64)...")
    start = time.time()
    job = sim.run(qc_mps, shots=2000)
    result = job.result()
    counts = result.get_counts()
    print(f"Time: {time.time() - start:.2f}s")
    
    # Sort and print top results
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    print("\nTop Results:")
    for bitstring, count in sorted_counts[:5]:
        print(f"{bitstring}: {count}")
        
    print(f"\nWinner: {sorted_counts[0][0]}")
    
    # Save result
    import json
    with open("results/p9_simplified_mps_64.json", "w") as f:
        json.dump(counts, f)

if __name__ == "__main__":
    solve_simplified_mps()
