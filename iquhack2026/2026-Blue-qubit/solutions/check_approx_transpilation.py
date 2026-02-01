from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import time

TARGETS = {
    "P6": "challenge/P6_low_hill.qasm",
}

def check_approx(name, path):
    print(f"\n--- Checking {name} for Approximate Collapse ---")
    qc = QuantumCircuit.from_qasm_file(path)
    #qc.measure_all() # No, original circuit might have measures or not. Usually challenge has no measures until end.
    # The file likely has gates only? Let's assume standard challenge format.
    
    orig_depth = qc.depth()
    orig_ops = qc.count_ops()
    print(f"  Original: Depth={orig_depth}, Ops={sum(orig_ops.values())}")
    
    # Try aggressive approx
    for degree in [1.0, 0.99, 0.95, 0.90]:
        start = time.time()
        # Use AerSimulator as target to allow optimizing for simulator
        qc_tr = transpile(qc, 
                          basis_gates=['u3', 'cx'], # force standard basis
                          approximation_degree=degree, 
                          optimization_level=3)
        dt = time.time() - start
        
        new_depth = qc_tr.depth()
        new_ops = sum(qc_tr.count_ops().values())
        print(f"  [Approx {degree}] Depth={new_depth} (-{100*(1-new_depth/orig_depth):.1f}%), Ops={new_ops} (t={dt:.2f}s)")
        
        if new_depth < 20:
            print(f"  [SUCCESS] Collapsed! Simulating locally with MPS...")
            # Use MPS method to avoid 2^60 pure state memory usage
            # Even if depth is 1, default Aer might try statevector if not careful.
            sim = AerSimulator(method='matrix_product_state')
            # Ensure measurements
            qc_tr.measure_all()
            job = sim.run(qc_tr, shots=1024)
            counts = job.result().get_counts()
            top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[0]
            print(f"  [RESULT] {top[0]} (count {top[1]})")
            return

if __name__ == "__main__":
    for name, path in TARGETS.items():
        check_approx(name, path)
