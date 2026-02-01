
import bluequbit
import json

TOKEN = "API_here"
bq = bluequbit.init(TOKEN)

def check_job(job_id):
    print(f"Fetching job {job_id}...")
    job = bq.get(job_id)
    
    try:
        result = job
        counts = result.get_counts()
        if counts:
            print(f"Total Unique Bitstrings: {len(counts)}")
            sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            print("\nTop 10 samples:")
            for b, c in sorted_counts[:10]:
                print(f"  {b}: {c}")
            
            # Check if distribution is flat
            if all(c == 1 for c in counts.values()):
                print("\n[!] Distribution is FLAT (all counts = 1).")
            else:
                max_c = sorted_counts[0][1]
                print(f"\n[OK] Distribution is PEAKED. Max count: {max_c}")
        else:
            print("No counts found in job result. (Maybe job only computed expectation values?)")
            
        # Also check expectation value if present
        try:
            exp_vals = job.expectation_value
            if exp_vals:
                print(f"\nExpectation values found: {len(exp_vals)} marginals.")
                import numpy as np
                bits = (np.array(exp_vals) < 0).astype(int)
                marginal_str = "".join(str(b) for b in bits[::-1])
                print(f"Marginal Reconstructed Bitstring: {marginal_str}")
        except:
            pass
            
    except Exception as e:
        print(f"Error fetching result: {e}")

if __name__ == "__main__":
    check_job("xYkd2Jv1K5Sp8Qzm")
