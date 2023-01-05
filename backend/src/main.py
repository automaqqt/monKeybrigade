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

app = FastAPI(title="monkeybrigade API", description="made with <3 by green", version="0.0.1")

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
    redis = aioredis.from_url(
        os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379"),
        encoding="utf8",
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


@app.get("/")
def home(request: Request):
    return {"Yes this service is running fine!"}

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
async def get_drops(
    before: str = None, after: str = None, limit: int = None, mnky: bool= False, order: OrderChoose = OrderChoose.desc
):

    start = time.perf_counter()
    qry = list(retrieve_work(before, after, order.value, limit, mnky))

    return {"query_time": time.perf_counter() - start, "count": len(qry), "data": qry}

