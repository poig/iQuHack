from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import json
import os

def solve_full():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    qc.measure_all()
    # Using BD=64 as initial attempt for 56 qubits. Structure should help.
    sim = AerSimulator(method='matrix_product_state', matrix_product_state_max_bond_dimension=64)
    print("Running Full P9 MPS (BD=64)...")
    job = sim.run(transpile(qc, sim), shots=2000)
    counts = job.result().get_counts()
    
    print("Top results:")
    for k, v in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"{k}: {v}")
    
    os.makedirs("results", exist_ok=True)
    with open("results/p9_full_counts.json", "w") as f:
        json.dump(counts, f, indent=2)

if __name__ == "__main__":
    solve_full()
