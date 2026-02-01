from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag
from qiskit.dagcircuit import DAGOpNode
import matplotlib.pyplot as plt
import numpy as np

TARGET_QASM = "../challenge/P9_grand_summit.qasm"

def inspect():
    print(f"--- Inspecting {TARGET_QASM} ---")
    try:
        qc = QuantumCircuit.from_qasm_file(TARGET_QASM)
    except FileNotFoundError:
        print("File not found.")
        return
        
    print(f"Depth: {qc.depth()}")
    
    # Iterate layers
    dag = circuit_to_dag(qc)
    
    print("\nLayer | Gate Count | 2Q Gates | 1Q Gates")
    print("----------------------------------------")
    
    layers = list(dag.layers())
    
    counts_2q = []
    
    for i, layer in enumerate(layers):
        # layer is a list of nodes (generator actually yielded one 'graph' object sometimes? No, dag.layers yields dicts or iterator of nodes or graph depending on version. 
        # Actually in recent qiskit dag.layers() yields an iterator of LAYERS where each layer is a list of nodes?
        # Let's check typical usage: it yields nodes? Or generator?
        # Documentation: "Yields a shallow DAGCircuit for each layer"? No.
        # "Yields a list of nodes for each layer." Yes.
        
        # Wait, my previous code `for node in layer['graph'].nodes():` implies layer was a dict.
        # Actually `dag.layers()` yields `generator`. Each item is...
        # Let's assume it yields a list of nodes.
        # If it yields a DAGCircuit, then we need `layer.op_nodes()`.
        
        # Safe way:
        current_layer_nodes = layer['graph'].nodes() if isinstance(layer, dict) else layer
        
        n_2q = 0
        n_1q = 0
        
        # Check if it's iterable directly
        try:
            it = iter(current_layer_nodes)
        except TypeError:
            # Maybe it's a DAGCircuit?
            current_layer_nodes = current_layer_nodes.op_nodes()
            
        for node in current_layer_nodes:
            if isinstance(node, DAGOpNode) and node.op.name not in ['barrier', 'measure']:
                if len(node.qargs) == 2:
                    n_2q += 1
                else:
                    n_1q += 1
        
        counts_2q.append(n_2q)
        print(f" {i:3d}  | {n_2q + n_1q:4d}       | {n_2q:3d}      | {n_1q:3d}")
        
    # Check for symmetry
    print(f"\nSymmetry Check (First 10 vs Last 10 reversed):")
    print(f"Start: {counts_2q[:10]}")
    print(f"End:   {counts_2q[-10:]}")

if __name__ == "__main__":
    inspect()
