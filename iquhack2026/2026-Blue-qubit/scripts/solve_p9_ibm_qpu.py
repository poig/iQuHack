try:
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
except ImportError:
    print("Warning: qiskit_ibm_runtime not found. QPU submission will be skipped.")
    QiskitRuntimeService = None
    Sampler = None

from qiskit import QuantumCircuit, transpile, qasm2
import pyzx as zx
from qiskit.transpiler import PassManager
import json
import os
import time

# P9: Grand Summit
TARGET_QASM = "challenge/P9_grand_summit.qasm"
OUTPUT_FILE = "results/final_P9_ibm_qpu.json"

def solve_p9_qpu():
    print(f"\n=== Solving P9 on IBM Quantum QPU (PyZX + Approx 0.99) ===")
    
    # 1. Initialize Service
    service = None
    if QiskitRuntimeService:
        try:
            
            MY_TOKEN = "API_here"
            MY_CRN = "API_here"
            
            print(f"  [1] Connecting to IBM Cloud (CRN ending in ...{MY_CRN[-5:]})...")
            service = QiskitRuntimeService(channel="ibm_cloud", token=MY_TOKEN, instance=MY_CRN)
            print("      Success: Authenticated.")
            
        except Exception as e:
            print(f"      [Warning] IBM Cloud auth failed: {e}")
            print("      Attempting to load saved default account...")
            try:
                service = QiskitRuntimeService()
                print("      Success: Saved credentials loaded.")
            except Exception as e2:
                print(f"      [Error] Could not initialize service: {e2}")
    else:
        print("  [1] Skipping IBM Service initialization (module not found).")
    
    # 2. Select Backend
    backend = None
    if service:
        print("  [2] Selecting backend (>56 qubits)...")
        backends = service.backends(min_num_qubits=57, simulator=False)
        if not backends:
            print("  [Error] No available backends with >56 qubits.")
            return
        
        # Specific selection: ibm_fez
        try:
            backend = service.backend("ibm_fez")
            print(f"      Selected: {backend.name} (Pending jobs: {backend.status().pending_jobs})")
        except Exception as e:
            print(f"      [Error] Could not select ibm_marrakesh: {e}")
            print("      Falling back to least busy...")
            backend = min(backends, key=lambda b: b.status().pending_jobs)
            print(f"      Selected: {backend.name} (Pending jobs: {backend.status().pending_jobs})")
    else:
        print("  [2] Skipping Backend selection (no service).")

    # 3. Load & Preprocess Circuit
    print("  [3] Loading and Preprocessing...")
    try:
        # A. PyZX Reduction
        qc_orig = QuantumCircuit.from_qasm_file(TARGET_QASM)
        print(f"      Original: {qc_orig.depth()} Depth")
        
        # qasm_str = qasm2.dumps(qc_orig)
        # g = zx.Circuit.from_qasm(qasm_str).to_graph()
        # zx.full_reduce(g)
        # circ_reduced = zx.extract_circuit(g)
        # qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
        # print(f"      After PyZX: {qc_zx.depth()} Depth")
        
        # B. Approximate Transpilation (Local)
        # We start with a generic pass to simplify structure 
        # before targeting the specific backend
        qc_approx = transpile(qc_orig, 
                              basis_gates=['u3', 'cx'], 
                              optimization_level=3, 
                              approximation_degree=0.99)
        print(f"      After Approx(0.99): {qc_approx.depth()} Depth")
        
    except Exception as e:
        print(f"      [Error] Preprocessing failed: {e}")
        return

    # 2.1 Local MPS Simulation (Safeguard)
    # Check depth to ensure it's safe to simulate locally
    current_depth = qc_approx.depth()
    print(f"      Approx Depth: {current_depth}")

    SIM_DEPTH_THRESHOLD = 50 # Lowered to skip slow simulation for P9 (Depth ~83)
    if current_depth < SIM_DEPTH_THRESHOLD:
        print(f"  [2.1] Running Local MPS Simulation (Depth {current_depth} < {SIM_DEPTH_THRESHOLD})...")
        try:
            from qiskit_aer import AerSimulator
            
            # Create a simulation copy
            qc_sim = qc_approx.copy()
            # Ensure measurements exist for simulation
            qc_sim.measure_all()
            
            sim = AerSimulator(method='matrix_product_state')
            sim.set_options(matrix_product_state_max_bond_dimension=64)
            
            # Simple transpile for simulator
            qc_sim_trans = transpile(qc_sim, backend=sim, optimization_level=1)
            
            print("      Executing MPS simulation...")
            result = sim.run(qc_sim_trans, shots=2000).result()
            counts_sim = result.get_counts()
            
            # Show top results
            top_sim = dict(sorted(counts_sim.items(), key=lambda item: item[1], reverse=True)[:5])
            print(f"      [MPS RESULT] Top candidates: {top_sim}")
            
            best_sim_str = max(counts_sim, key=counts_sim.get)
            print(f"      [MPS BEST]   {best_sim_str}")
            
        except ImportError:
            print("      [Warning] qiskit-aer not found. Skipping simulation.")
        except Exception as e:
            print(f"      [Warning] Simulation failed: {e}")
    else:
        print(f"      [Skip] Circuit depth {current_depth} > {SIM_DEPTH_THRESHOLD}. Skipping local simulation.")

    # Add measurements to the main circuit for QPU if not present?
    # Usually PyZX circuits don't have measurements.
    # Note: For SamplerV2, we usually need measurements unless we use estimator.
    # We will add measure_all to qc_approx for the QPU path as well, 
    # but strictly speaking we should check if they exist. 
    # Since PyZX strips them, we add them safely.
    # However, 'qc_approx' was already used for sim copy. 
    # Let's modify qc_approx in place for the QPU path to match.
    if  qc_approx.num_clbits == 0:
        print("      Adding measurements for QPU execution...")
        qc_approx.measure_all()

    # 4. Final Transpilation & Run
    if backend:
        print(f"  [4] Final Transpilation for {backend.name}...")
        qc_final = transpile(qc_approx, backend=backend, optimization_level=3)
        print(f"      Final H/W Depth: {qc_final.depth()}")
    else:
        print("  [4] Skipping final transpilation (no backend).")
        return

    # 5. Submit
    print("  [5] Submitting Job...")
    try:
        sampler = Sampler(mode=backend)
    except TypeError:
        # Fallback if 'mode' isn't arguably the right keyword in some versions, try positional
        print("      [Info] Retrying Sampler init with positional argument...")
        sampler = Sampler(backend)
    job = sampler.run([qc_final], shots=10000)
    print(f"      Job ID: {job.job_id()}")
    
    # Wait for result (blocking)
    print("      Waiting for result (this may take hours/days depending on queue)...")
    # In a real run, user might simply want the ID. 
    # But here we block to be consistent with other scripts.
    result = job.result()
    pub_result = result[0]
    counts = pub_result.data.meas.get_counts()
    
    # Top bitstring
    best_str = max(counts, key=counts.get)
    best_count = counts[best_str]
    
    print(f"  *** IBM QPU SOLUTION: {best_str} (Count: {best_count}) ***")
    
    os.makedirs("results", exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump({
            "bitstring": best_str,
            "counts": counts,
            "backend": backend.name,
            "job_id": job.job_id()
        }, f, indent=2)
    print(f"      Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    solve_p9_qpu()
