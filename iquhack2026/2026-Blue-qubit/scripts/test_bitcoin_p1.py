
import pyzx as zx
from qiskit import QuantumCircuit, transpile
import collections

def test_bitcoin():
    path = "bitcoin_problem/P1_little_dimple.qasm"
    print(f"Testing {path}...")
    
    with open(path, 'r') as f:
        qasm = f.read()
    
    # Qiskit only
    qc_orig = QuantumCircuit.from_qasm_str(qasm)
    print(f"Original: {qc_orig.num_qubits} qubits, {qc_orig.size()} gates")
    
    strategies = ["clifford_simp", "full_reduce", "teleport_reduce"]
    
    for strategy in strategies:
        print(f"\n--- Strategy: {strategy} ---")
        try:
            c = zx.Circuit.from_qasm(qasm)
            g = c.to_graph()
            if strategy == "clifford_simp":
                zx.simplify.clifford_simp(g)
            elif strategy == "full_reduce":
                zx.full_reduce(g)
            elif strategy == "teleport_reduce":
                zx.teleport_reduce(g)
            
            extracted = zx.extract_circuit(g)
            print(f"  PyZX Extracted gates: {len(extracted.gates)}")
            
            # Convert to Qiskit and transpile
            qc = QuantumCircuit.from_qasm_str(extracted.to_qasm())
            qc_opt = transpile(qc, optimization_level=3, basis_gates=['u3', 'cz'])
            print(f"  Qiskit Optimized gates: {qc_opt.size()}")
            print(f"  Profile: {collections.Counter([inst.operation.name for inst in qc_opt.data])}")
        except Exception as e:
            print(f"  Failed: {e}")

if __name__ == "__main__":
    test_bitcoin()
