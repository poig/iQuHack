from qiskit import QuantumCircuit, transpile, qasm2
from qiskit_ibm_transpiler import generate_ai_pass_manager
import pyzx as zx

def ai_transpile_p9():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    
    # Use AI Pass Manager if possible (it requires a token usually, but let's check local mode)
    # If it fails, we fallback to our custom pass manager.
    try:
        print("Attempting AI-powered transpilation...")
        # Note: Local mode requires heavy models, let's see if it works
        pm = generate_ai_pass_manager(optimization_level=3, ai_optimization_level=3)
        qc_ai = pm.run(qc)
        print(f"AI Transpiled Depth: {qc_ai.depth()}")
    except Exception as e:
        print(f"AI Transpilation failed: {e}. Falling back to aggressive HLS.")
        # Fallback: Deep consolidation
        qc_ai = transpile(qc, optimization_level=3, approximation_degree=0.9)
        print(f"Fallback Transpiled Depth: {qc_ai.depth()}")

    qubit_data = {}
    for i in range(qc_ai.num_qubits):
        qubit_data[i] = {"depth": 0, "two_qubit_count": 0}

    for instruction in qc_ai.data:
        qargs = instruction.qubits
        for q in qargs:
            idx = qc_ai.find_bit(q).index
            qubit_data[idx]["depth"] += 1 
            if len(qargs) == 2:
                qubit_data[idx]["two_qubit_count"] += 1
                
    print("\nQubit Statistics (AI/Aggressive):")
    sorted_stats = sorted(qubit_data.items(), key=lambda x: x[1]['depth'])
    for i, data in sorted_stats:
        print(f"Q{i:2d}: Ops={data['depth']:4d}, 2Q-Gates={data['two_qubit_count']:3d}")

if __name__ == "__main__":
    ai_transpile_p9()
