import redis
import json

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

key = "hotel:65881"
value = redis_client.get(key)

if value:
    data = json.loads(value)
    print(json.dumps(data, indent=4))
else:
    print("Key not found")