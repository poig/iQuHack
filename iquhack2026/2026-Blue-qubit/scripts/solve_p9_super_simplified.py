
import pyzx as zx
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import collections
import time

def solve_super_simplified():
    print("Loading P9...")
    g = zx.Circuit.from_qasm_file("challenge/P9_grand_summit.qasm").to_graph()
    
    print("Running PyZX full_reduce...")
    zx.full_reduce(g)
    
    print("Extracting circuit...")
    # Using extract_circuit which usually produces a lot of CX/CZ
    qc_zx_circuit = zx.extract_circuit(g)
    qasm_str = qc_zx_circuit.to_qasm()
    qc_zx = QuantumCircuit.from_qasm_str(qasm_str)
    
    print(f"Pre-optimization: {len(qc_zx.data)} gates")
    
    print("Running Aggressive Qiskit Transpile (L3, Basis=[u3, cz])...")
    # Using 'cz' as requested by the user's result profile
    qc_opt = transpile(qc_zx, optimization_level=3, basis_gates=['u3', 'cz'])
    
    counts_gates = collections.Counter([inst.operation.name for inst in qc_opt.data])
    print(f"Post-optimization Profile: {counts_gates}")
    print(f"Total Gates: {len(qc_opt.data)}")
    
    # Check if we hit the ~450 range
    if len(qc_opt.data) > 600:
         print("Reduction not aggressive enough. Trying another pass...")
         qc_opt = transpile(qc_opt, optimization_level=3, basis_gates=['u3', 'cz'])
         counts_gates = collections.Counter([inst.operation.name for inst in qc_opt.data])
         print(f"Pass 2 Profile: {counts_gates}")

    print("\nRunning local MPS Simulation (BD=128)...")
    qc_opt.measure_all()
    sim = AerSimulator(method='matrix_product_state', matrix_product_state_max_bond_dimension=128)
    
    start = time.time()
    job = sim.run(qc_opt, shots=1000)
    result = job.result()
    counts = result.get_counts()
    print(f"Sim Time: {time.time() - start:.2f}s")
    
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    print("\nTop 5 Results:")
    for b, c in sorted_counts[:5]:
        print(f"  {b}: {c}")
        
    winner = sorted_counts[0][0]
    print(f"\nFinal Winner: {winner}")
    
    # Save to verify against user's result
    with open("results/p9_super_simplified.json", "w") as f:
        import json
        json.dump(counts, f)

if __name__ == "__main__":
    solve_super_simplified()
