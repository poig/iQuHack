
import pyzx as zx
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import *
import numpy as np
import collections

def analyze_simplified_p9():
    print("Loading P9...")
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    print(f"Original: {len(qc.data)} gates, Depth: {qc.depth()}")

    print("\nRunning PyZX full_reduce...")
    g = zx.Circuit.from_qasm_file("challenge/P9_grand_summit.qasm").to_graph()
    zx.full_reduce(g)
    print("Running PyZX extract_circuit...")
    # full_reduce makes graph generic, so we must use extract_circuit which returns a PyZX Circuit
    qc_zx_circuit = zx.extract_circuit(g)
    # Convert PyZX Circuit to Qiskit via QASM
    qasm_str = qc_zx_circuit.to_qasm()
    qc_zx = QuantumCircuit.from_qasm_str(qasm_str)
    print(f"Post-PyZX: {len(qc_zx.data)} gates, Depth: {qc_zx.depth()}")

    print("\nRunning Qiskit Transpile (Level 3)...")
    qc_opt = transpile(qc_zx, optimization_level=3, basis_gates=['u3', 'cx'])
    print(f"Post-Transpile L3: {len(qc_opt.data)} gates, Depth: {qc_opt.depth()}")

    # Analyze Gate Content
    ops = collections.defaultdict(int)
    non_clifford_u3 = 0
    clifford_u3 = 0
    
    for inst in qc_opt.data:
        name = inst.operation.name
        ops[name] += 1
        
        if name == 'u3':
            # Check if U3 is Clifford
            # Clifford U3s have parameters as multiples of pi/2
            params = [float(p) for p in inst.operation.params]
            is_cliff = True
            for p in params:
                # Check if p / (pi/2) is close to integer
                if not np.isclose(p % (np.pi/2), 0, atol=1e-5) and not np.isclose(p % (np.pi/2), np.pi/2, atol=1e-5):
                     is_cliff = False
                     break
            if is_cliff:
                clifford_u3 += 1
            else:
                non_clifford_u3 += 1

    print("\nGate Counts (Simplified):")
    for k, v in ops.items():
        print(f"  {k}: {v}")
    print(f"  Clifford U3: {clifford_u3}")
    print(f"  Non-Clifford U3: {non_clifford_u3}")

    # Connectivity Analysis (Active Qubits)
    active_qubits = set()
    for inst in qc_opt.data:
        for q in inst.qubits:
            active_qubits.add(q)
    print(f"\nActive Qubits in Simplified: {len(active_qubits)}")

    # Check for Identity Block Structure (Layer Density)
    # Basic depth profile
    print("\nApproximate Layer Density (first 20 layers):")
    # This is a rough heuristic since transpile output is not strictly layered
    # But checking if gates bunch up or sparse out
    # We can just check depth
    
if __name__ == "__main__":
    analyze_simplified_p9()
