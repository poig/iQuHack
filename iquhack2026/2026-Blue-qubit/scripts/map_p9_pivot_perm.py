from qiskit import QuantumCircuit
from collections import defaultdict

def map_pivot_permutation():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    qubit_time = [0] * qc.num_qubits
    
    # Store instructions with their layer index
    layer_instructions = defaultdict(list)
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(qubit_time[i] for i in qargs)
        duration = 1
        for i in qargs:
            qubit_time[i] = start_time + duration
        
        layer_instructions[start_time].append(instruction)
        
    pivot = 43
    print(f"Analyzing structure around pivot Layer {pivot}...")
    
    def get_layer_graph(layers):
        # returns set of edges (u,v)
        edges = set()
        for l in layers:
            for inst in layer_instructions[l]:
                if len(inst.qubits) == 2:
                    u, v = sorted([qc.find_bit(inst.qubits[0]).index, 
                                   qc.find_bit(inst.qubits[1]).index])
                    edges.add((u, v))
        return edges

    # Compare 5 layers before and 5 layers after
    for dist in range(1, 6):
        e_pre = get_layer_graph([pivot - dist])
        e_post = get_layer_graph([pivot + dist])
        
        print(f"Layer {pivot-dist} edges ({len(e_pre)}): {sorted(list(e_pre))}")
        print(f"Layer {pivot+dist} edges ({len(e_post)}): {sorted(list(e_post))}")
        
if __name__ == "__main__":
    map_pivot_permutation()
