from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import json

def diagnose_pinched():
    # Load what we built in solve_p9_pinched.py
    # We can't load the dynamic circuit directly unless we output QASM.
    # Let's recreate the "Outer 1 + Outer 2" circuit without the S map logic for a moment to see complexity.
    
    qc_full = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc_full.num_qubits
    
    q_t = [0] * n
    layer_insts = []
    
    for instruction in qc_full.data:
        qargs = [qc_full.find_bit(q).index for q in instruction.qubits]
        start_time = max(q_t[i] for i in qargs)
        duration = 1
        for i in qargs:
            q_t[i] = start_time + duration
        layer_insts.append((start_time, instruction))
    
    # Construct "Direct Pinched" (Outer 1 then immediately Outer 2 on same qubits)
    # If S is identity, this should be low entanglement?
    # Or check entanglement of Outer 1 alone.
    
    qc_outer1 = QuantumCircuit(n)
    for t, inst in layer_insts:
        if t <= 39:
            qc_outer1.append(inst.operation, inst.qubits)
            
    # Measure entanglement entropy of Outer 1 output?
    # MPS simulation can estimate it?
    # Or just simulate Outer 1 and see if it's peaked.
    
    sim = AerSimulator(method='matrix_product_state')
    qc_outer1.measure_all()
    
    print("Simulating Outer 1 (Layer 0-39)...")
    result = sim.run(transpile(qc_outer1, sim), shots=100).result().get_counts()
    print(f"Outer 1 unique outcomes: {len(result)}")
    
    if len(result) > 50:
        print("Outer 1 is highly scrambled.")
    else:
        print("Outer 1 is peaked/low-entanglement.")

if __name__ == "__main__":
    diagnose_pinched()
