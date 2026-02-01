from qiskit import QuantumCircuit, transpile
import time

def check_depth_drop():
    path = "challenge/P9_grand_summit.qasm"
    print(f"Loading {path}...")
    qc = QuantumCircuit.from_qasm_file(path)
    orig_depth = qc.depth()
    orig_gates = len(qc.data)
    print(f"Original Depth: {orig_depth}, Gates: {orig_gates}")
    
    # Try levels of approximation
    for deg in [1.0, 0.99, 0.95]:
        start = time.time()
        print(f"\nTranspiling with approximation_degree={deg}...")
        qc_tr = transpile(qc, 
                          basis_gates=['u3', 'cx'], 
                          optimization_level=3, 
                          approximation_degree=deg)
        tr_depth = qc_tr.depth()
        tr_gates = len(qc_tr.data)
        print(f"  Result -> Depth: {tr_depth} ({tr_depth/orig_depth:.2%}), Gates: {tr_gates} (Time: {time.time()-start:.1f}s)")

if __name__ == "__main__":
    check_depth_drop()
