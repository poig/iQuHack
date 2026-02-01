from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import time

qc = QuantumCircuit.from_qasm_file("challenge/P4_gentle_mound.qasm")
qc.measure_all()

# Try MPS with medium Bond Dimension
BD = 64
print(f"Simulating P4 (Depth {qc.depth()}) with MPS (BD={BD})...")
sim = AerSimulator(method='matrix_product_state', matrix_product_state_max_bond_dimension=BD)

start = time.time()
try:
    job = sim.run(transpile(qc, sim), shots=4096)
    counts = job.result().get_counts()
    print(f"Time: {time.time() - start:.2f}s")
    
    sorted_c = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    winner = sorted_c[0][0]
    prob = sorted_c[0][1] / 4096
    print(f"Winner: {winner} (Prob {prob:.4f})")
    
except Exception as e:
    print(f"Failed: {e}")
