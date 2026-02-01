import bluequbit
import json
import os
import sys

TOKEN = "API_here"
bq = bluequbit.init(TOKEN)

def harvest():
    print("=== Harvesting P9 PPS Results from Cloud ===")
    
    # Determine correct list method.
    try:
        print("Searching for completed jobs...")
        # search() returns a list of JobResult objects
        jobs = bq.search(run_status="COMPLETED")
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return

    print(f"Found {len(jobs)} completed jobs. Filtering for P9...")
    
    results_map = {}
    
    # Load existing if any, to merge (optional, but good for safety)
    if os.path.exists("results/final_P9.json"):
        try:
            with open("results/final_P9.json", "r") as f:
                content = json.load(f)
                if isinstance(content, dict):
                    results_map = content
        except:
            pass

    count_new = 0
    # Debug: print first 5 names

    for job in jobs:
        # JobResult object has attributes: job_id, job_name, run_status, etc.
        try:
            name = job.job_name
            # If name is None, skip
            if not name:
                continue
        except AttributeError:
            continue
            
        # We are looking for PPS jobs. 
        # if "P9" not in name:
        #     continue
        
        # P9 has 56 qubits. 
        # Most other challenges have different qubit counts.
        # But let's check anything with q in name.
            
        # Try to parse qubit index
        idx = -1
        try:
            # Look for q followed by digits
            import re
            match = re.search(r'q(\d+)', name)
            if match:
                idx = int(match.group(1))
        except:
            continue
            
        if idx == -1:
            continue
            
        idx_str = str(idx)
        
        # Retrieve result if not already in map or if it's new
        try:
            # get the result value
            # For PPS, it's expectation_value
            val = job.expectation_value
            
            # Convert to bit
            bit = '1' if val < 0 else '0'
            
            if idx_str not in results_map:
                 print(f"  [Recovered] Q{idx}: {bit} (val={val:.4f}) ID={job.job_id[-4:]}")
                 count_new += 1
            
            # Store data
            results_map[idx_str] = {
                "bit": bit,
                "val": val,
                "job_id": job.job_id,
                "name": name
            }
            
        except Exception as e:
            # print(f"  Failed to get result for {name}: {e}")
            pass

    # Save
    os.makedirs("results", exist_ok=True)
    with open("results/final_P9.json", "w") as f:
        json.dump(results_map, f, indent=2)
        
    print(f"\nHarvest Complete.")
    print(f"  New Recovered: {count_new}")
    print(f"  Total Solved: {len(results_map)} / 56")
    
    # Calculate String if complete
    if len(results_map) == 56:
        # Reconstruct bitstring (q55...q0)
        # Check endianness. Usually q0 is far right.
        bits = ['?'] * 56
        for k, v in results_map.items():
            if k.isdigit():
                bits[int(k)] = v['bit']
        
        final_str = "".join(list(reversed(bits)))
        print(f"  [FULL SOLUTION]: {final_str}")
        
        # Confidence analysis
        confidences = [abs(v['val']) for v in results_map.values()]
        avg_conf = sum(confidences) / len(confidences)
        print(f"  Average Confidence: {avg_conf:.4f}")
        
        uncertain = [int(k) for k, v in results_map.items() if abs(v['val']) < 0.1]
        if uncertain:
            print(f"  Uncertain Bits (|val| < 0.1): {sorted(uncertain)}")
        else:
            print("  All bits are reasonably certain (|val| >= 0.1).")
    else:
        print(f"  Missing {56 - len(results_map)} qubits.")


if __name__ == "__main__":
    harvest()
