import bluequbit
from concurrent.futures import ThreadPoolExecutor
import time

TOKEN = "API_here"
bq = bluequbit.init(TOKEN)

# known IDs from previous logs
known_ids = [
]

def cancel_job(jid):
    try:
        bq.cancel(jid)
        return jid, True
    except:
        return jid, False

print(f"Starting parallel cancellation of {len(known_ids)} known IDs...")
with ThreadPoolExecutor(max_workers=20) as executor:
    results = list(executor.map(cancel_job, known_ids))

success_count = sum(1 for _, ok in results if ok)
print(f"Parallel Sweep Finished. Successes: {success_count}")

print("\nScanning for any remaining active jobs via search...")
try:
    # Based on inspection, we need to find the ID attribute
    jobs = bq.search() # Returns some iterable
    remaining_ids = []
    for job in jobs:
        # Try to find ID property
        jid = getattr(job, 'job_id', getattr(job, 'id', None))
        if not jid:
             # JobResult objects from bq.get() don't have ID, 
             # but search might return something else.
             continue
        
        # We don't have status here easily without checking 
        # so let's just attempt to cancel if it's recent? 
        # Actually bq.search likely returns job summaries.
        remaining_ids.append(jid)

    if remaining_ids:
        print(f"Found {len(remaining_ids)} IDs via search. Canceling...")
        with ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(cancel_job, remaining_ids)
    else:
        print("No IDs found via bq.search().")

except Exception as e:
    print(f"Search sweep failed: {e}")
