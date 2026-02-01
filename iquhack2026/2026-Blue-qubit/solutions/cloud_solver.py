import bluequbit
from qiskit import QuantumCircuit
import numpy as np
import time
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

TOKEN = "API_here"
bq = bluequbit.init(TOKEN)

def get_pauli_str(i, n):
    # BlueQubit convention: Leftmost char is qubit 0? 
    # Let's align with the check_endianness result if we had it, but 
    # based on P5 success: "I"*i + "Z" + "I"*(n-1-i) worked.
    return "I" * i + "Z" + "I" * (n - 1 - i)

def solve_qubit(name, qc, i, n, threshold):
    pauli_str = get_pauli_str(i, n)
    pauli_sum = [(pauli_str, 1.0)]
    job_name = f"{name}_q{i}"
    tags = {"name": name, "qubit": i}
    try:
        job = bq.run(qc, device="pauli-path", pauli_sum=pauli_sum, job_name=job_name, tags=tags, 
                     options={
                         'pauli_path_truncation_threshold': threshold,
                         'pauli_path_circuit_transpilation_level': 1
                     })
        val = job.expectation_value
        bit = '1' if val < 0 else '0'
        return i, bit, val, None
    except Exception as e:
        return i, None, None, str(e)

def run_pps(name, path, threshold=1e-4, workers=10):
    print(f"\n>>> Running PPS Attack on {name} (threshold={threshold})")
    qc = QuantumCircuit.from_qasm_file(path)
    n = qc.num_qubits
    bitstring = [None] * n
    
    out_file = f"results/pps_{name}.json"
    os.makedirs("results", exist_ok=True)
    results_cache = {}
    if os.path.exists(out_file):
        with open(out_file, "r") as f:
            results_cache = json.load(f)
            for k, v in results_cache.items():
                bitstring[int(k)] = v['bit']

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        for i in range(n):
            if bitstring[i] is None:
                futures.append(executor.submit(solve_qubit, name, qc, i, n, threshold))
                
        for future in as_completed(futures):
            idx, bit, val, err = future.result()
            if bit is not None:
                bitstring[idx] = bit
                results_cache[str(idx)] = {'bit': bit, 'val': val}
                with open(out_file, "w") as f:
                    json.dump(results_cache, f)
                print(f"  [{name}] Qubit {idx} DONE: {bit} ({val:.4f})")
            else:
                print(f"  [{name}] Qubit {idx} FAILED: {err}")

    if all(b is not None for b in bitstring):
        final_str = "".join(bitstring[::-1])
        print(f"\n[!!!] FINAL {name}: {final_str}")
        return final_str
    return None

def run_mps(name, path, shots=1000, bond_dim=16):
    print(f"\n>>> Running MPS Marginals on {name} (BD={bond_dim})")
    qc = QuantumCircuit.from_qasm_file(path)
    n = qc.num_qubits
    
    # Construct Z operators for each qubit to compute marginals
    z_ops = []
    for i in range(n):
        z_str = get_pauli_str(i, n)
        z_ops.append([(z_str, 1.0)])
    
    job_name = f"{name}_mps"
    options = {}
    if bond_dim:
        options["mps_bond_dimension"] = bond_dim
    
    # Run batch expectation value calculation
    job = bq.run(qc, device="mps.cpu", pauli_sum=z_ops, job_name=job_name, options=options)
    print(f"  [SUBMITTED] Job ID: {job.job_id}")
    
    result = job.expectation_value
    
    if result:
        vals = np.array(result)
        # Reconstruct: 1 if < 0, else 0
        bits = (vals < 0).astype(int)
        
        # Reverse to match Qiskit bitstring order (qn...q0)
        final_str = "".join(str(b) for b in bits[::-1])
        
        print(f"  [{name}] Reconstructed Bitstring: {final_str}")
        return final_str
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--mode", choices=["pps", "mps"], default="pps")
    parser.add_argument("--threshold", type=float, default=1e-4)
    parser.add_argument("--shots", type=int, default=1000)
    parser.add_argument("--bond_dim", type=int, default=None)
    args = parser.parse_args()
    
    if args.mode == "pps":
        run_pps(args.name, args.path, args.threshold)
    else:
        run_mps(args.name, args.path, args.shots, args.bond_dim)

# usage to solve p9 with pps:
# python solutions/cloud_solver.py --name P9_grand_summit --path challenge/P9_grand_summit.qasm --mode pps --threshold 1e-4
# python solutions/cloud_solver.py --name P9_grand_summit --path challenge/P9_grand_summit.qasm --mode mps --bond_dim 64
# python solutions/cloud_solver.py --name P9_simp --path challenge/P9_simplified.qasm --mode mps --bond_dim 256