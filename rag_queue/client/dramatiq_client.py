import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend

# Create result backend with longer expiration (10 minutes = 600000 ms)
result_backend = RedisBackend(url="redis://localhost:6379/1")

# Create Redis broker
redis_broker = RedisBroker(url="redis://localhost:6379/0")

# Add results middleware to broker with result_ttl
redis_broker.add_middleware(Results(backend=result_backend, result_ttl=600000))

# Set the broker AFTER adding middleware
dramatiq.set_broker(redis_broker)

# Export both for use in other modules
__all__ = ['redis_broker', 'result_backend']