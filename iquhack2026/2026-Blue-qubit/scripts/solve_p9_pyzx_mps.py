import pyzx as zx
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import json

def pyzx_mps_solve():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    
    from qiskit import qasm2
    # PyZX reduction
    print("Performing PyZX reduction...")
    c = zx.Circuit.from_qasm(qasm2.dumps(qc))
    g = c.to_graph()
    zx.full_reduce(g)
    c_red = zx.extract_circuit(g)
    
    # Use qasm2.loads if possible, otherwise from_qasm_str
    try:
        qc_red = qasm2.loads(c_red.to_qasm())
    except:
        qc_red = QuantumCircuit.from_qasm_str(c_red.to_qasm())
    print(f"Reduced Gate Count: {len(qc_red.data)}")
    
    # MPS simulation
    sim = AerSimulator(method='matrix_product_state', 
                       matrix_product_state_max_bond_dimension=32) # Low bond for speed
    
    qc_trans = transpile(qc_red, backend=sim, optimization_level=3)
    qc_trans.measure_all()
    
    print("Running MPS on reduced circuit...")
    job = sim.run(qc_trans, shots=1024)
    result = job.result()
    counts = result.get_counts()
    
    # Find most frequent bitstring
    top_str = max(counts, key=counts.get)
    print(f"Top Bitstring (Reduced): {top_str}")
    
    with open("solutions/p9_pyzx_mps.txt", "w") as f:
        f.write(top_str)

if __name__ == "__main__":
    pyzx_mps_solve()
