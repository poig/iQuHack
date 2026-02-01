import pyzx as zx
from qiskit import QuantumCircuit, transpile
import collections
from qiskit_aer import AerSimulator
import time

def run_sim(qc, name):
    print(f"\n--- Simulating {name} ---")
    qc.measure_all()
    # Using low Bond Dimension to see if the peak survives truncation
    sim = AerSimulator(method='matrix_product_state', matrix_product_state_max_bond_dimension=64)
    start = time.time()
    job = sim.run(qc, shots=500)
    result = job.result()
    counts = result.get_counts()
    print(f"Time: {time.time() - start:.2f}s")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for b, c in sorted_counts[:3]:
        print(f"  {b}: {c}")
    return counts

def test_soft_reduction():
    print("Loading P9 QASM...")
    # Load as ZX graph
    g_base = zx.Circuit.from_qasm_file("challenge/P9_grand_summit.qasm").to_graph()
    
    # Strategy 1: Clifford Simp
    print("\n[Strategy 1] clifford_simp")
    g1 = g_base.copy()
    zx.simplify.clifford_simp(g1)
    qc1 = QuantumCircuit.from_qasm_str(zx.extract_circuit(g1).to_qasm())
    qc1_opt = transpile(qc1, optimization_level=3, basis_gates=['u3', 'cz'])
    print(f"Gates: {len(qc1_opt.data)} | {collections.Counter([inst.operation.name for inst in qc1_opt.data])}")
    run_sim(qc1_opt, "clifford_simp")

    # Strategy 2: Teleport Reduce
    print("\n[Strategy 2] teleport_reduce")
    g2 = g_base.copy()
    zx.simplify.teleport_reduce(g2)
    qc2 = QuantumCircuit.from_qasm_str(zx.extract_circuit(g2).to_qasm())
    qc2_opt = transpile(qc2, optimization_level=3, basis_gates=['u3', 'cz'])
    print(f"Gates: {len(qc2_opt.data)} | {collections.Counter([inst.operation.name for inst in qc2_opt.data])}")
    # run_sim(qc2_opt, "teleport_reduce") # Likely too large for BD=64

    # Strategy 3: Full Reduce (Standard)
    print("\n[Strategy 3] full_reduce")
    g3 = g_base.copy()
    zx.full_reduce(g3)
    qc3 = QuantumCircuit.from_qasm_str(zx.extract_circuit(g3).to_qasm())
    qc3_opt = transpile(qc3, optimization_level=3, basis_gates=['u3', 'cz'])
    print(f"Gates: {len(qc3_opt.data)} | {collections.Counter([inst.operation.name for inst in qc3_opt.data])}")
    run_sim(qc3_opt, "full_reduce")

    # Strategy 4: Hybrid (teleport_reduce -> clifford_simp)
    print("\n[Strategy 4] teleport_reduce -> clifford_simp")
    g4 = g_base.copy()
    zx.simplify.teleport_reduce(g4)
    zx.simplify.clifford_simp(g4)
    qc4 = QuantumCircuit.from_qasm_str(zx.extract_circuit(g4).to_qasm())
    qc4_opt = transpile(qc4, optimization_level=3, basis_gates=['u3', 'cz'])
    print(f"Gates: {len(qc4_opt.data)} | {collections.Counter([inst.operation.name for inst in qc4_opt.data])}")
    run_sim(qc4_opt, "teleport -> clifford")

    # Strategy 5: teleport_reduce -> full_reduce
    # This is "softer" than starting with full_reduce
    print("\n[Strategy 5] teleport_reduce -> full_reduce")
    g5 = g_base.copy()
    zx.simplify.teleport_reduce(g5)
    zx.full_reduce(g5)
    qc5 = QuantumCircuit.from_qasm_str(zx.extract_circuit(g5).to_qasm())
    qc5_opt = transpile(qc5, optimization_level=3, basis_gates=['u3', 'cz'])
    print(f"Gates: {len(qc5_opt.data)} | {collections.Counter([inst.operation.name for inst in qc5_opt.data])}")
    run_sim(qc5_opt, "teleport -> full_reduce")
    
if __name__ == "__main__":
    test_soft_reduction()
