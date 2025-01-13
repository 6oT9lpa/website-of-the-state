from flask_limiter import Limiter # type: ignore
from flask_limiter.util import get_remote_address # type: ignore
from redis import Redis

# Инициализация Redis
redis = Redis(host='localhost', port=6379, db=0)

# Инициализация Limiter с использованием Redis
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri='redis://localhost:6379'
)