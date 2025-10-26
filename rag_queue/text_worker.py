import time
import redis
import json
from rag_queue.queues.tasks import process_query_task

# Send a job
print("📤 Sending job...")
job = process_query_task.send("test query")
job_id = job.message_id
print(f"✅ Job ID: {job_id}")

# Wait for processing
print("⏳ Waiting for job to process...")
time.sleep(15)  # Wait 15 seconds

# Check Redis directly
redis_client = redis.Redis.from_url("redis://localhost:6379/1", decode_responses=True)

# Check all keys and their list contents
all_keys = redis_client.keys("*")
print(f"🔑 All keys in Redis DB 1: {all_keys}")

print("\n📦 Checking list contents:")
for key in all_keys:
    key_type = redis_client.type(key)
    print(f"\n  Key: {key}")
    print(f"  Type: {key_type}")
    
    if key_type == 'list':
        # Get all items from the list
        items = redis_client.lrange(key, 0, -1)
        print(f"  List length: {len(items)}")
        for i, item in enumerate(items):
            print(f"  Item {i}: {item[:200] if len(item) > 200 else item}")
            # Try to parse as JSON
            try:
                parsed = json.loads(item)
                print(f"    Parsed: {parsed}")
            except:
                pass

# Also try with the message ID hash
import hashlib
hashed_id = hashlib.md5(job_id.encode()).hexdigest()
print(f"\n🔐 MD5 hash of job_id: {hashed_id}")

if hashed_id in all_keys:
    print(f"✅ Found matching hash key!")
    items = redis_client.lrange(hashed_id, 0, -1)
    print(f"Items in this list: {items}")