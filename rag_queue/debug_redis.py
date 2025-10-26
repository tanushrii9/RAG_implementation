import redis

# Connect to Redis
queue_client = redis.Redis.from_url("redis://localhost:6379/0", decode_responses=False)
result_client = redis.Redis.from_url("redis://localhost:6379/1", decode_responses=True)

print("=== Redis Debug Info ===")
print(f"✅ Redis Connection: OK")

# Check queue
queue_length = queue_client.llen("dramatiq:default.DQ")
print(f"📊 Jobs in queue: {queue_length}")

# Check all messages in queue
if queue_length > 0:
    messages = queue_client.lrange("dramatiq:default.DQ", 0, -1)
    print(f"📋 Queue messages:")
    for msg in messages:
        print(f"  - {msg[:100]}...")  # Print first 100 chars

# Check results
result_keys = result_client.keys("dramatiq:result:*")
print(f"📦 Result keys in Redis: {len(result_keys)}")
if result_keys:
    for key in result_keys:
        print(f"  - {key}")

# Check all dramatiq keys
all_keys = queue_client.keys("dramatiq:*")
print(f"🔑 All dramatiq keys: {len(all_keys)}")
for key in all_keys[:10]:  # Show first 10
    print(f"  - {key}")