import argparse
from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag
from qiskit.dagcircuit import DAGOpNode
import collections

def inspect(qasm_path):
    print(f"--- Inspecting {qasm_path} ---")
    try:
        qc = QuantumCircuit.from_qasm_file(qasm_path)
    except Exception as e:
        print(f"Error loading QASM: {e}")
        return
        
    print(f"Qubits: {qc.num_qubits}")
    print(f"Gates: {len(qc.data)}")
    print(f"Depth: {qc.depth()}")
    
    # Gate distribution
    ops = collections.Counter([inst.operation.name for inst in qc.data])
    print("\nGate Types:")
    for name, count in ops.items():
        print(f"  {name}: {count}")
        
    # Layer analysis
    dag = circuit_to_dag(qc)
    layers = list(dag.layers())
    print(f"\nLayers: {len(layers)}")
    
    # Symmetry / Density (first/last 5 layers)
    counts_2q = []
    for layer in layers:
        n_2q = 0
        current_layer_nodes = layer['graph'].nodes() if isinstance(layer, dict) else layer
        if not isinstance(current_layer_nodes, list):
            try:
                current_layer_nodes = current_layer_nodes.op_nodes()
            except:
                pass
        
        for node in current_layer_nodes:
            if isinstance(node, DAGOpNode) and len(getattr(node, 'qargs', [])) == 2:
                n_2q += 1
        counts_2q.append(n_2q)
        
    if len(counts_2q) >= 10:
        print(f"\n2Q Gate Density (Start vs End):")
        print(f"  Start 5: {counts_2q[:5]}")
        print(f"  End   5: {counts_2q[-5:]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("qasm", help="Path to QASM file")
    args = parser.parse_args()
    inspect(args.qasm)
