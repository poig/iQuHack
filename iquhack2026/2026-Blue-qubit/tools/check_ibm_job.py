from qiskit_ibm_runtime import QiskitRuntimeService
import json
import os

JOB_ID = "d5vj7at7fc0s73au35r0" # Active Marrakesh Job

def check_job():
    print(f"--- Checking IBM Job {JOB_ID} ---")
    
    try:
        # Auth (using hardcoded creds from solve_p9_ibm_qpu.py logic, or saved account)
        # Try loading saved first
        try:
            service = QiskitRuntimeService()
        except:
            # Fallback
             MY_TOKEN = "API_here"
             MY_CRN = "API_here"
             service = QiskitRuntimeService(channel="ibm_cloud", token=MY_TOKEN, instance=MY_CRN)

        job = service.job(JOB_ID)
        status = job.status()
        
        if hasattr(status, 'name'):
            status_name = status.name
        else:
            status_name = str(status)
            
        print(f"Status: {status_name}")
        
        if status_name in ["DONE", "COMPLETED"]:
            print("Job DONE! Retrieving results...")
            result = job.result()
            # PubResult -> data -> meas -> counts
            pub_result = result[0]
            counts = pub_result.data.meas.get_counts()
            
            best_str = max(counts, key=counts.get)
            print(f"Best Bitstring: {best_str}")
            print(f"Counts: {counts}")
            
            with open("solutions/p9_ibm_results.json", "w") as f:
                json.dump({"counts": counts, "best": best_str}, f)
            print(f"      Saved to solutions/p9_ibm_results.json")
            
        elif status_name == "ERROR":
            print(f"Job Failed: {job.error_message()}")
            
    except Exception as e:
        print(f"Error checking job: {e}")

if __name__ == "__main__":
    check_job()
