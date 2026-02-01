from qiskit_ibm_runtime import QiskitRuntimeService

def list_jobs():
    print("--- Listing Recent IBM Jobs ---")
    try:
        service = QiskitRuntimeService()
    except Exception:
        # Fallback creds
        MY_TOKEN = "API_here"
        MY_CRN = "API_here"
        service = QiskitRuntimeService(channel="ibm_cloud", token=MY_TOKEN, instance=MY_CRN)

    jobs = service.jobs(limit=5, descending=True)
    for job in jobs:
        print(f"Job ID: {job.job_id()} | Status: {job.status()} | Backend: {job.backend().name}")
        
if __name__ == "__main__":
    list_jobs()
