import os
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import csv

# Problems to solve
problems = [
    {"name": "P1", "file": "challenge/P1_little_peak.qasm", "qubits": 4},
    {"name": "P2", "file": "challenge/P2_small_bump.qasm", "qubits": 20},
]

sim_sv = AerSimulator(method='statevector')
sim_mps = AerSimulator(method='matrix_product_state')

results = []

for p in problems:
    print(f"\n--- Solving {p['name']} ({p['qubits']} qubits) ---")
    
    # Choose Simulator
    if p['qubits'] <= 24:
        sim = sim_sv
        print("Method: Statevector (Exact)")
    else:
        sim = sim_mps
        print("Method: MPS (Approximate/Factorized)")
        
    try:
        qc = QuantumCircuit.from_qasm_file(p['file'])
        qc.measure_all()
        
        # Transpile
        qc_t = transpile(qc, sim)
        
        # Run
        job = sim.run(qc_t, shots=1024)
        counts = job.result().get_counts()
        
        # Find Winner
        winner = max(counts, key=counts.get)
        prob = counts[winner] / 1024.0
        
        print(f"Winner: {winner}")
        print(f"Prob: {prob:.4f}")
        
        results.append((p['name'], winner, prob))
        
    except Exception as e:
        print(f"Failed to solve {p['name']}: {e}")

print("\n=== FINAL RESULTS ===")
for name, bitstring, prob in results:
    print(f"{name}: {bitstring} (Prob: {prob:.4f})")
