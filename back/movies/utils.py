from django.core.cache import cache

def invalidate_user_cache(user_id):
    cache_key = f"recommendation:user:{user_id}"
    cache.delete(cache_key)