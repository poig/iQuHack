import pyzx as zx
from qiskit import QuantumCircuit, transpile, qasm2
from qiskit.transpiler import PassManager
from qiskit_aer import AerSimulator
from qiskit_ibm_transpiler.ai.synthesis import (
    AICliffordSynthesis, 
    AILinearFunctionSynthesis, 
    AIPauliNetworkSynthesis
)
from qiskit_ibm_transpiler.ai.collection import (
    CollectLinearFunctions,
    CollectPauliNetworks
)
import json
import os
import time

# P9: Grand Summit
TARGET_QASM = "challenge/P9_grand_summit.qasm"
OUTPUT_FILE = "results/final_P9_ibm.json"

def solve_p9_ibm():
    print(f"\n=== Solving P9 (Hybrid PyZX + IBM AI + MPO) ===", flush=True)
    
    # 1. Load and Reduce with PyZX
    print("  [1] PyZX Reduction...", flush=True)
    qc_orig = QuantumCircuit.from_qasm_file(TARGET_QASM)
    qasm_str = qasm2.dumps(qc_orig)
    g = zx.Circuit.from_qasm(qasm_str).to_graph()
    zx.full_reduce(g)
    circ_reduced = zx.extract_circuit(g)
    qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
    print(f"      Reduced Size: {qc_zx.num_qubits} Qubits, {qc_zx.depth()} Depth")
    
    # 2. IBM AI Synthesis
    # We provide a full coupling map (all-to-all) to allow maximal optimization
    # for a simulator target.
    from qiskit.transpiler import CouplingMap
    cmap = CouplingMap.from_full(56)
    
    print("  [2] IBM AI Synthesis Passes...", flush=True)
    
    # Define a pass manager with AI synthesis
    # Note: Local mode is used for free execution
    pm = PassManager([
        # Collect and synthesize Pauli Networks (limit to 5 qubits for safety)
        CollectPauliNetworks(max_block_size=5),
        AIPauliNetworkSynthesis(coupling_map=cmap, local_mode=True),
        
        # Collect and synthesize Linear Function blocks (limit to 8 qubits)
        CollectLinearFunctions(max_block_size=8),
        AILinearFunctionSynthesis(coupling_map=cmap, local_mode=True),
    ])
    
    try:
        t0 = time.time()
        qc_ai = pm.run(qc_zx)
        # Final cleanup transpilation to base gates
        qc_final = transpile(qc_ai, basis_gates=['u3', 'cx'], optimization_level=3)
        dt = time.time() - t0
        print(f"      AI Optimization Depth: {qc_final.depth()} (t={dt:.2f}s)", flush=True)
    except Exception as e:
        print(f"      [Error] IBM AI Synthesis failed: {e}", flush=True)
        # Fallback to standard transpilation if AI fails
        qc_final = transpile(qc_zx, basis_gates=['u3', 'cx'], optimization_level=3)
        print(f"      Fallback Depth: {qc_final.depth()}", flush=True)

    # 3. MPO Simulation
    print("  [3] Final Simulation (MPO, BD=128)...", flush=True)
    sim = AerSimulator(method='matrix_product_state')
    sim.set_options(matrix_product_state_max_bond_dimension=128)
    
    qc_final.measure_all()
    
    job = sim.run(qc_final, shots=4000)
    result = job.result().get_counts()
    
    # Get top candidate
    best_str = max(result, key=result.get)
    best_count = result[best_str]
    top_results = dict(sorted(result.items(), key=lambda item: item[1], reverse=True)[:5])
    
    print(f"  *** IBM AI SOLUTION: {best_str} (Count: {best_count}) ***")
    
    output_data = {
        "bitstring": best_str,
        "counts": top_results,
        "method": "PyZX + IBM AI Synthesis + MPO"
    }
    
    os.makedirs("results", exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"      Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    solve_p9_ibm()
