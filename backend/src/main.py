import os
import random
import time
from datetime import datetime, timedelta
from enum import Enum

import aioredis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from pydantic import BaseModel

import cachetool
from db import init_db, retrieve_drops, retrieve_work

app = FastAPI(title="monKeybrigade API", description="made with <3 by kind monKeys", version="0.0.2")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class OrderChoose(str, Enum):
    desc = "desc"
    asc = "asc"


@app.on_event("startup")
def on_startup():
    
    init_db()
    try:
        start_iso = cachetool.get_cache("db")["last_elec"]
    except Exception as e:
        print("init cache with current time")
        cachetool.set_cache("db",{"last_elec":datetime.utcnow().isoformat().split('Z')[0][:-3]})

    redis = aioredis.from_url(
        os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379"),
        encoding="utf8",
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


@app.get("/")
def home(request: Request):
    return {"Yes this service is running fine!"}

@app.get("/healthc")
def home(request: Request):
    return {"Yes this service is running fine!"}
    
@app.get("/status_db")
async def get_db_status():
    start = time.time()
    db_cache = cachetool.get_cache("db")
    
    return {"query_time":time.time()-start,"db_state":db_cache}

@app.get("/drops")
@cache(expire=5)
async def get_drops(
    before: str = None, after: str = None, limit: int = None, order: OrderChoose = OrderChoose.desc
):

    start = time.perf_counter()
    qry = list(retrieve_drops(before, after, limit, order.value))

    return {"query_time": time.perf_counter() - start, "count": len(qry), "data": qry}

@app.get("/work")
@cache(expire=5)
async def get_work(
    user:str=None, before: str = None, after: str = None, limit: int = None, mnky: bool= False, order: OrderChoose = OrderChoose.desc
):

    start = time.perf_counter()
    qry = list(retrieve_work(before, after, order.value, limit, mnky, user))

    return {"query_time": time.perf_counter() - start, "count": len(qry), "data": qry}


@app.get("/cmc_list")
async def get_cached_cmc_wallet_list():

    start = time.time()
    val = cachetool.get_cache("cmcs")    
    
    return {"query_time":time.time()-start,"data":val}

@app.get("/get_cooldown_raffle")
async def retrieve_cd_raffle_from_redis():

    start = time.time()
    resp = cachetool.get_cache("targetCD")
    
    return {"query_time":time.time()-start,"data":resp}

@app.get("/get_personal")
async def retrieve_personal_info():

    start = time.time()
    resp = cachetool.get_cache("targetCD")
    val = cachetool.get_cache("cmcs")
    db = cachetool.get_cache("db")
        
    return {"query_time":time.time()-start,"cds":resp,"db":db,"cmcs":val}
