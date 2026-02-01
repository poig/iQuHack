
import pyzx as zx
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def export_simplified_p9():
    print("Loading P9 QASM...")
    g = zx.Circuit.from_qasm_file("challenge/P9_grand_summit.qasm").to_graph()
    zx.full_reduce(g)
    
    print("Extracting simplified circuit...")
    qc_zx_circuit = zx.extract_circuit(g)
    qasm_str = qc_zx_circuit.to_qasm()
    qc_zx = QuantumCircuit.from_qasm_str(qasm_str)
    
    print("Transpiling (L3)...")
    # Optimize to reduce gate count before export
    qc_opt = transpile(qc_zx, optimization_level=3, basis_gates=['u3', 'cz'])
    
    import qiskit.qasm2
    out_path = "challenge/P9_simplified.qasm"
    print(f"Saving to {out_path} (Gates: {len(qc_opt.data)})...")
    qiskit.qasm2.dump(qc_opt, out_path)
    print("Done.")

if __name__ == "__main__":
    export_simplified_p9()
