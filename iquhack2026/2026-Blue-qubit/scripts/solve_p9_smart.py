import bluequbit
from qiskit import QuantumCircuit
import json
import os
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = "API_here"
bq = bluequbit.init(TOKEN)

TARGETS = {
    "P9": {"path": "../challenge/P9_grand_summit.qasm", "qubits": 56},
}

def get_solved_indices(name):
    path = f"results/final_{name}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            solved_indices = set()
            for k in data.keys():
                if k.isdigit():
                    solved_indices.add(int(k))
            return solved_indices
    return set()

def get_pauli_str(i, n):
    # Reverse order for Qiskit/BlueQubit endianness matches job name q{i}
    # q0 is rightmost. String index n-1.
    return "I" * (n - 1 - i) + "Z" + "I" * i

def submit_job(name, qc, i, n, dry_run=False):
    if dry_run:
        print(f"  [DRY-RUN] Would submit {name} Qubit {i}")
        return None
    
    pauli_str = get_pauli_str(i, n)
    pauli_sum = [(pauli_str, 1.0)]
    job_name = f"{name}_q{i}_smart_v2" # v2 to distinguish
    tags = {"name": name, "qubit": i, "strategy": "smart-pps-v2"}
    
    try:
        # Use threshold 1e-4 as before
        job = bq.run(qc, device="pauli-path", pauli_sum=pauli_sum, 
                     job_name=job_name, tags=tags, 
                     options={'pauli_path_truncation_threshold': 1e-4})
        print(f"  [SUBMITTED] {name} Q{i}: {job.job_id}")
        return job
    except Exception as e:
        print(f"  [FAILED] {name} Q{i}: {e}")
        return None

def solve_smart(dry_run=False, batch_size=5):
    print("Starting Smart PPS Solver (v2)...")
    
    tasks = []
    
    for name, info in TARGETS.items():
        n = info['qubits']
        solved = get_solved_indices(name)
        # Note: Harvest only looks for 'P9' in name, so my new jobs P9_qX_smart_v2 should be picked up.
        # But 'solved' indices come from harvest.py.
        
        missing = [i for i in range(n) if i not in solved]
        
        print(f"\n{name}: {len(solved)}/{n} solved. Missing {len(missing)} qubits.")
        if not missing:
            continue
            
        qc = QuantumCircuit.from_qasm_file(info['path'])
        qc.remove_final_measurements(inplace=True) # Ensure no measurements
        
        # Add to global task list
        for i in missing:
            tasks.append((name, qc, i, n))
            
    print(f"\nTotal tasks to run: {len(tasks)}")
    
    if dry_run:
        for t in tasks:
            submit_job(*t, dry_run=True)
        return

    # Execute in batches
    # We use a simple loop with sleep to be gentle on the queue
    for idx, task in enumerate(tasks):
        if idx > 0 and idx % batch_size == 0:
            print(f"Batch limit reached. Sleeping for 5s...")
            time.sleep(5)
            
        submit_job(*task, dry_run=False)


def solve_local_mps(dry_run=False):
    print("Starting Local MPS Marginal Attack...")
    try:
        from qiskit_aer import AerSimulator
        from qiskit import transpile
    except ImportError:
        print("Error: qiskit-aer not installed.")
        return

    name = "P9"
    info = TARGETS[name]
    qc_orig = QuantumCircuit.from_qasm_file(info['path'])
    qc_orig.remove_final_measurements(inplace=True)
    
    # Add measurements for all qubits to get marginals from counts
    qc_orig.measure_all()
    
    print("  Transpiling for MPS...")
    sim = AerSimulator(method='matrix_product_state', 
                       matrix_product_state_max_bond_dimension=32) # Low bond dim for speed/robustness
    
    # Enable logging? standard run doesn't show much.
    
    # Use optimization_level=3 to optimize layout (minimize swaps for 1D MPS)
    qc_trans = transpile(qc_orig, backend=sim, optimization_level=3)
    
    if dry_run:
        print("  [DRY-RUN] Would run MPS simulation.")
        return

    print("  Running MPS Simulation (shots=10000, bond_dim=32)...")
    start_t = time.time()
    result = sim.run(qc_trans, shots=10000).result()
    print(f"  Simulation done in {time.time() - start_t:.2f}s")
    counts = result.get_counts()
    
    # Calculate Marginals <Zi> from counts
    # counts keys are "q55...q0" (bitstring)
    
    n = qc_orig.num_qubits # 56
    
    # Initialize expectations
    z_exp = {i: 0.0 for i in range(n)}
    total_shots = sum(counts.values())
    
    for bitstr, count in counts.items():
        # bitstr is little-endian reversed string from qiskit: "b_n-1 ... b_0"
        # So index 0 in string is qubit n-1. 
        # Index k in string corresponds to qubit (n - 1 - k).
        
        for k, char in enumerate(bitstr):
            qubit_idx = n - 1 - k
            # Z eigenvalue is +1 for '0', -1 for '1'
            val = 1 if char == '0' else -1
            z_exp[qubit_idx] += val * count
            
    # Normalize
    for i in range(n):
        z_exp[i] /= total_shots
        
    print("\nLocal MPS Results:")
    results_map = {}
    
    for i in range(n):
        val = z_exp[i]
        bit = '1' if val < 0 else '0' # Negative Z expectation favors |1>
        
        # Determine confidence/magnitude
        # If val is close to 0, it's uncertain.
        
        results_map[str(i)] = {
            "bit": bit,
            "val": val,
            "job_id": "local_mps",
            "name": f"P9_q{i}_local"
        }
        # Print high confidence ones
        if abs(val) > 0.5:
             print(f"  Q{i}: {bit} (<Z>={val:.4f})")
             
    # Save to file compatible with harvest
    os.makedirs("results", exist_ok=True)
    with open(f"../results/final_{name}_local.json", "w") as f:
        json.dump(results_map, f, indent=2)
    print(f"  Saved to results/final_{name}_local.json")
    
    # Also save to main final if user wants
    with open(f"../results/final_{name}.json", "w") as f:
        json.dump(results_map, f, indent=2)
    print(f"  Updated results/final_{name}.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--local", action="store_true", help="Run with Local MPS instead of Cloud")
    args = parser.parse_args()
    
    if args.local:
        solve_local_mps(dry_run=args.dry_run)
    else:
        solve_smart(dry_run=args.dry_run)
