from qiskit import QuantumCircuit
from collections import defaultdict
import numpy as np

def compare_u3_around_pivot():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    qubit_time = [0] * qc.num_qubits
    
    # Store instructions with their layer index
    layer_instructions = defaultdict(lambda: defaultdict(list)) # layer -> qubit -> [inst]
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(qubit_time[i] for i in qargs)
        duration = 1
        for i in qargs:
            qubit_time[i] = start_time + duration
        
        for q in qargs:
            layer_instructions[start_time][q].append(instruction)
            
    pivot = 43
    print(f"Comparing U3 gates at Layer {pivot-1} vs Layer {pivot+1}...")
    
    layer_pre = pivot - 1
    layer_post = pivot + 1
    
    for q in range(qc.num_qubits):
        insts_pre = [i for i in layer_instructions[layer_pre][q] if i.name == 'u3']
        insts_post = [i for i in layer_instructions[layer_post][q] if i.name == 'u3']
        
        if insts_pre and insts_post:
            p_pre = insts_pre[0].params
            p_post = insts_post[0].params
            
            # U3(theta, phi, lambda) inverse is U3(theta, -lambda, -phi)? 
            # Actually, let's just see if they are related.
            print(f"Q{q:2d}: Pre={np.round(p_pre, 3)}, Post={np.round(p_post, 3)}")
        elif insts_pre or insts_post:
            print(f"Q{q:2d}: Mismatch (Pre has {len(insts_pre)}, Post has {len(insts_post)})")

if __name__ == "__main__":
    compare_u3_around_pivot()
