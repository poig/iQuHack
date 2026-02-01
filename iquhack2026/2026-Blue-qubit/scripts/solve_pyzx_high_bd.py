import pyzx as zx
from qiskit import QuantumCircuit, transpile, qasm2
from qiskit_aer import AerSimulator
import numpy as np

def solve_reduced_core():
    path = "challenge/P9_grand_summit.qasm"
    
    # 1. Get Reduced Circuit again
    qc_orig = QuantumCircuit.from_qasm_file(path)
    g = zx.Circuit.from_qasm(qasm2.dumps(qc_orig)).to_graph()
    zx.full_reduce(g)
    circ_reduced = zx.extract_circuit(g)
    qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
    qc_trans = transpile(qc_zx, basis_gates=['u3', 'cx'], optimization_level=3)
    
    # 2. Extract sparse middle layers (30 to 55)
    # Be careful with Qiskit layer slicing. We'll use the time-tracking manually.
    n = qc_trans.num_qubits
    qubit_depth = [0] * n
    
    qc_core = QuantumCircuit(n)
    
    # We want to capture the operation of the middle skeleton.
    # But wait, if Outers are Identity, then the whole circuit ~ Core?
    # Or is it Outer * Core * Outer_Inv?
    # If PyZX reduced it, the remaining graph *is* the simplified circuit.
    # So we should simulate the WHOLE reduced circuit?
    # The user said "p9_pyzx_mps.txt" solution was wrong.
    # That script simulated the whole reduced circuit.
    # Why was it wrong? Bond dim 32?
    # Or 'Approx Transpilation' broke it?
    # The layer density shows the middle is simple.
    # Maybe the "Dense" outer layers are just SWAPs or simple Cliffords that PyZX didn't optimize away fully?
    # 200 gates/layer is dense.
    
    # Let's try simulating the *entire* reduced circuit with HIGH bond dimension.
    # If the middle is sparse, entanglement might be manageable?
    # But outer blocks are dense.
    
    sim = AerSimulator(method='matrix_product_state', matrix_product_state_max_bond_dimension=128)
    qc_trans.measure_all()
    print("Simulating Full Reduced Circuit (BD=128)...")
    job = sim.run(qc_trans, shots=2000)
    counts = job.result().get_counts()
    
    top = max(counts, key=counts.get)
    print(f"Top Result: {top} (Cnt: {counts[top]})")

if __name__ == "__main__":
    solve_reduced_core()
