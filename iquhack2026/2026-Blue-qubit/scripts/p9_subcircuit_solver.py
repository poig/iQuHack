from qiskit import QuantumCircuit, transpile, qasm2
from qiskit_aer import AerSimulator
import pyzx as zx

def solve_for_qubit(target_idx):
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    
    # 1. PyZX Reduction
    qasm_str = qasm2.dumps(qc)
    g = zx.Circuit.from_qasm(qasm_str).to_graph()
    zx.full_reduce(g)
    circ_reduced = zx.extract_circuit(g)
    qc_reduced = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
    
    # 2. Extract lightcone for target_idx
    dependencies = set([target_idx])
    # Iterate in REVERSE to find everything that affects target_idx
    # This is slightly wrong for a dependency graph, better to build it once.
    # But let's just use a simple set-based approach going forward.
    
    # Build dependency map
    influent_qubits = set([target_idx])
    instructions_to_keep = []
    
    # Actually, iterate forward and track sets?
    # No, iterate REWARD.
    
    data = list(qc_reduced.data)
    for i in range(len(data)-1, -1, -1):
        instr = data[i]
        qargs = [qc_reduced.find_bit(q).index for q in instr.qubits]
        if any(q in influent_qubits for q in qargs):
            influent_qubits.update(qargs)
            instructions_to_keep.append(instr)
            
    print(f"Target Q{target_idx} influent qubits: {len(influent_qubits)}")
    
    # If influent qubits > 30, it's still hard.
    if len(influent_qubits) > 30:
        print("Still too many qubits. Trying approximation on the subcircuit.")
        # We can't easily build a subcircuit from data[] because indices change.
        # Let's just use the full circuit but only measure the target.
        # (This is just as slow as full simulation unless we transpile with measurement).
        pass

if __name__ == "__main__":
    solve_for_qubit(36)
