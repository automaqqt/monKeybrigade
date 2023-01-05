import json

import redis

conn = redis.Redis(host="redis", port=6379, db=1)


def set_cache(key, value):
    write = json.dumps(value)
    conn.set(key, write)
    return True


def get_cache(key):
    read = conn.get(key)
    cache = {}
    if read:
        cache = json.loads(read)
    return cache


def set_target_cooldown(miner, timestamp):
    read = get_cache("targetCD")
    read[miner] = timestamp
    out = json.dumps(read)
    conn.set("targetCD", out)
    return True


def clear_target_cooldown():
    read = {}
    out = json.dumps(read)
    conn.set("targetCD", out)
    return True
