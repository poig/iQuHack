import pyzx as zx
from qiskit import QuantumCircuit, qasm2
import time

def test_reduction():
    path = "challenge/P9_grand_summit.qasm"
    print(f"Loading {path}...")
    qc = QuantumCircuit.from_qasm_file(path)
    
    print("Converting to PyZX and reducing...")
    start = time.time()
    qasm_str = qasm2.dumps(qc)
    c = zx.Circuit.from_qasm(qasm_str)
    g = c.to_graph()
    zx.full_reduce(g)
    
    # Check graph size
    print(f"Original Gates: {len(qc.data)}")
    print(f"Reduced Graph Vertices: {g.num_vertices()}")
    print(f"Reduced Graph Edges: {g.num_edges()}")
    
    # Try to extract circuit
    print("Extracting circuit from graph...")
    c_red = zx.extract_circuit(g)
    print(f"Reduced Gate Count: {len(c_red.gates)} (Time: {time.time()-start:.1f}s)")
    
    # Convert back to Qiskit to check depth
    qc_red = QuantumCircuit.from_qasm_str(c_red.to_qasm())
    print(f"Reduced Depth: {qc_red.depth()}")

if __name__ == "__main__":
    test_reduction()
