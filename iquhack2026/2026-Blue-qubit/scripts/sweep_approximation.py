import pyzx as zx
from qiskit import QuantumCircuit, transpile, qasm2
import numpy as np

TARGET_QASM = "../challenge/P9_grand_summit.qasm"

def sweep():
    print(f"--- Sweeping Approx Degrees for {TARGET_QASM} ---")
    
    # 1. Load Original
    qc = QuantumCircuit.from_qasm_file(TARGET_QASM)
    print(f"Original Depth: {qc.depth()}, Qubits: {qc.num_qubits}")
    
    # 2. PyZX Reduction first?
    print("Running PyZX reduction base...")
    qasm_str = qasm2.dumps(qc)
    g = zx.Circuit.from_qasm(qasm_str).to_graph()
    zx.full_reduce(g)
    circ_reduced = zx.extract_circuit(g)
    qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
    print(f"PyZX Base Depth: {qc_zx.depth()}")
    
    # 3. Sweep Transpilation
    print("\nDegree | Depth | Ops")
    print("--------------------")
    
    degrees = np.linspace(1.0, 0.90, 11) # 1.0, 0.99, ... 0.90
    
    best_depth = 9999
    best_deg = 1.0
    
    for deg in degrees:
        qc_approx = transpile(qc_zx, 
                              basis_gates=['u3', 'cx'], 
                              optimization_level=3, 
                              approximation_degree=deg)
        d = qc_approx.depth()
        ops = qc_approx.count_ops()
        total_ops = sum(ops.values())
        
        print(f" {deg:.2f}  |  {d:3d}  | {total_ops}")
        
        if d < best_depth:
            best_depth = d
            best_deg = deg
            
    print(f"\nBest Depth: {best_depth} at Degree {best_deg:.2f}")
    
    if best_depth < 30:
        print("FOUND CLIFF! Generating candidate from best circuit...")
        # Simulate?
        from qiskit_aer import AerSimulator
        qc_best = transpile(qc_zx, 
                              basis_gates=['u3', 'cx'], 
                              optimization_level=3, 
                              approximation_degree=best_deg)
                              
        qc_best.measure_all()
        sim = AerSimulator()
        result = sim.run(qc_best, shots=1000).result()
        counts = result.get_counts()
        best_str = max(counts, key=counts.get)
        print(f"Candidate: {best_str}")

if __name__ == "__main__":
    sweep()
