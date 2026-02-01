import networkx as nx
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np
import time

def solve_factored(name, path):
    print(f"\n=== Factoring {name} ({path}) ===")
    qc = QuantumCircuit.from_qasm_file(path)
    num_qubits = qc.num_qubits
    
    # 1. Build Interaction Graph
    G = nx.Graph()
    G.add_nodes_from(range(num_qubits))
    for instr in qc.data:
        if len(instr.qubits) == 2:
            q1 = instr.qubits[0]._index
            q2 = instr.qubits[1]._index
            G.add_edge(q1, q2)
            
    # 2. Get Components
    comps = list(nx.connected_components(G))
    print(f"Components found: {len(comps)} (Sizes: {[len(c) for c in comps]})")
    
    # Map from qubit index to its component index and relative index
    qubit_map = {}
    for c_idx, comp in enumerate(comps):
        comp_sorted = sorted(list(comp))
        for rel_idx, abs_idx in enumerate(comp_sorted):
            qubit_map[abs_idx] = (c_idx, rel_idx)

    # 3. Create sub-circuits
    sub_circuits = [QuantumCircuit(len(c)) for c in comps]
    for instr in qc.data:
        # Get target component(s)
        q_indices = [q._index for q in instr.qubits]
        # All qubits in a gate MUST belong to the same component in a factored circuit
        c_idx, rel_indices = qubit_map[q_indices[0]][0], [qubit_map[q][1] for q in q_indices]
        sub_circuits[c_idx].append(instr.operation, rel_indices)

    # 4. Solve each sub-circuit
    # Use high-bond MPS for reliability in low-RAM environments
    comp_winners = []
    sim_mps = AerSimulator(method='matrix_product_state', matrix_product_state_max_bond_dimension=1024)
    
    for i, sub_qc in enumerate(sub_circuits):
        print(f"  Solving Component {i} ({sub_qc.num_qubits} qubits)...")
        sub_qc.measure_all()
        start_comp = time.time()
        t_sub = transpile(sub_qc, sim_mps)
        job = sim_mps.run(t_sub, shots=2000)
        counts = job.result().get_counts()
        winner = max(counts, key=counts.get)
        print(f"    Winner {i}: {winner} (Prob {counts[winner]/2000:.4f}, Time {time.time()-start_comp:.2f}s)")
        comp_winners.append(winner)

    # 5. Recombine Results
    # The output bitstring should satisfy bit_i = Winner[comp(i)][rel_i]
    # Qiskit bitstrings are little-endian (q0 is rightmost)
    final_bits = [''] * num_qubits
    for abs_idx in range(num_qubits):
        c_idx, rel_idx = qubit_map[abs_idx]
        # Winner string is Big-endian-ish (index 0 is left-most)? 
        # Actually in get_counts() it's [N-1 ... 0]
        # So Winner[i][-(rel_idx+1)] is qubit abs_idx
        final_bits[abs_idx] = comp_winners[c_idx][-(rel_idx + 1)]
    
    # Join back to little-endian string (q_n ... q_0)
    final_solution = "".join(final_bits[::-1])
    print(f"\n[FINAL SOLUTION for {name}]: {final_solution}")
    return final_solution

# Run for P7 and P8
p7_sol = solve_factored("P7", "challenge/P7_rolling_ridge.qasm")
p8_sol = solve_factored("P8", "challenge/P8_bold_peak.qasm")

# Update solutions artifact with these high-confidence results
