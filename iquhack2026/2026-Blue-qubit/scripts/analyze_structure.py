import pyzx as zx
from qiskit import QuantumCircuit, transpile, qasm2
from qiskit.dagcircuit import DAGCircuit, DAGOpNode
from qiskit.converters import circuit_to_dag
import numpy as np
import matplotlib.pyplot as plt
import json

TARGET_QASM = "../challenge/P9_grand_summit.qasm"

def analyze_circuit():
    print(f"--- Analyzing {TARGET_QASM} ---")
    
    # 1. Load Original
    try:
        qc = QuantumCircuit.from_qasm_file(TARGET_QASM)
    except FileNotFoundError:
        print(f"Error: Could not find {TARGET_QASM}")
        return

    print(f"Original Depth: {qc.depth()}, Qubits: {qc.num_qubits}")
    
    # 2. PyZX Reduction
    print("Running PyZX reduction...")
    qasm_str = qasm2.dumps(qc)
    g = zx.Circuit.from_qasm(qasm_str).to_graph()
    zx.full_reduce(g)
    circ_reduced = zx.extract_circuit(g)
    qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
    print(f"PyZX Depth: {qc_zx.depth()}")
    
    # 3. Approx Transpilation
    print("Running Approx Transpilation (0.99)...")
    qc_approx = transpile(qc_zx, 
                          basis_gates=['u3', 'cx'], 
                          optimization_level=3, 
                          approximation_degree=0.99)
    print(f"Approx Depth: {qc_approx.depth()}")
    
    # 4. Analyze Per Qubit Depth/Ops
    print("\n--- Per Qubit Analysis (Approx Circuit) ---")
    dag = circuit_to_dag(qc_approx)
    
    qubit_depths = {}
    qubit_ops = {}
    
    for qubit in qc_approx.qubits:
        ops = 0
        gate_types = {}
        for node in dag.nodes_on_wire(qubit):
            if not isinstance(node, DAGOpNode):
                continue
            if node.op.name not in ['barrier', 'measure']:
                ops += 1
                gate_types[node.op.name] = gate_types.get(node.op.name, 0) + 1
        
        qubit_index = qc_approx.find_bit(qubit).index
        qubit_depths[qubit_index] = ops
        qubit_ops[qubit_index] = gate_types

    # Print stats
    if not qubit_depths:
        print("No operations found!")
        return

    sorted_depths = sorted(qubit_depths.items(), key=lambda x: x[1], reverse=True)
    print(f"Max Ops on Qubit: {sorted_depths[0]}")
    print(f"Min Ops on Qubit: {sorted_depths[-1]}")
    print(f"Average Ops: {np.mean(list(qubit_depths.values()))}")
    
    print("\nTop 10 Heavy Qubits:")
    for q, d in sorted_depths[:10]:
        print(f"  Q{q}: {d} ops {qubit_ops[q]}")

    print("\nBottom 10 Light Qubits:")
    for q, d in sorted_depths[-10:]:
        print(f"  Q{q}: {d} ops {qubit_ops[q]}")
        
    print("\n--- Connectivity Analysis ---")
    interactions = []
    for instruction in qc_approx.data:
        if instruction.operation.num_qubits == 2:
            indices = [qc_approx.find_bit(q).index for q in instruction.qubits]
            interactions.append(tuple(sorted(indices)))
            
    from collections import Counter
    interaction_counts = Counter(interactions)
    
    print("Most Frequent Interactions (Pairs):")
    for pair, count in interaction_counts.most_common(10):
        print(f"  {pair}: {count}")
        
    # Save raw data
    with open("results/p9_structure_analysis.json", "w") as f:
        json.dump({
            "qubit_ops": {str(k): v for k, v in qubit_ops.items()},
            "interaction_counts": {str(k): v for k, v in interaction_counts.items()}
        }, f, indent=2)
    print("Saved analysis to results/p9_structure_analysis.json")

if __name__ == "__main__":
    analyze_circuit()
