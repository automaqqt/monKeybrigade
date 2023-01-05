import os
import random
import time
from concurrent.futures.thread import _worker
from datetime import datetime, timedelta

import requests
from celery import Celery
from sqlalchemy import exists
from sqlmodel import Session

import cachetool
import config
from db import (
    commit_or_rollback,
    db_session,
    fetch_cmc_pub,
    update_done,
    update_elected,
)
from models import Drop, Work
from utils.eoswrap import transfer_wrap

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


class SqlAlchemyTask(celery.Task):
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        db_session.remove()


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60.0, cmc_routine.s(), name="cmc routine")
    sender.add_periodic_task(3600.0 * 2.0, elect.s(), name="elect every 2 hr")


@celery.task(base=SqlAlchemyTask)
def elect() -> str:
    start1 = time.time()
    cur_time = datetime.utcnow()
    handle = f"{str(cur_time.date())}-{str(cur_time.hour)}"
    print(handle)
    if not db_session.query(exists().where(Drop.handle == handle)).scalar():
        drop = Drop(
            handle=handle,
            state="VERIFY",
            type="raffle",
            issue_time=cur_time.isoformat()[:-3],
            day=str(cur_time.date()),
            hour=str(cur_time.hour),
            winners="",
            trx_id="",
        )
        commit_or_rollback(drop)
    else:
        return "Election for this hr already existst"
    verifying = True
    while verifying:
        if db_session.query(
            exists().where(Work.block_time >= (cur_time + timedelta(seconds=60)).isoformat()[:-3])
        ).scalar():
            elected = draw(cur_time)
            verifying = False
        else:
            print("filler behind, waiting 60 seconds and verify again")
            time.sleep(60)

    update_elected(handle, elected)
    dropping = True
    while dropping:
        try:
            tx_id = transfer_wrap(elected, "raffle")
            # tx_id = transfer_wrap(["greentestede","pigapigapiga"],"raffle")

            dropping = False
        except Exception as e:
            print(f"drop failed with error: {e}, waiting 60 seconds and verify again")
            time.sleep(60)
    suc = update_done(handle, tx_id)

    return f"{(time.time()-start1)} elected {len(elected)}, tx: {tx_id}"


def draw(cur_time):

    elig = fetch_cmc_pub(cur_time,True)
    drops_per_hour = config.drops_per_6_hour
    elected = [elig.pop(random.randint(0, len(elig) - 1)) for l in range(drops_per_hour)]

    return elected

@celery.task(base=SqlAlchemyTask)
def cleaner() -> str:
    start = time.time()
    try:

        delete_q = Work.__table__.delete().where(
            Work.block_time <= (datetime.utcnow() - timedelta(hours=1444)).isoformat()[:-3]
        )
        db_session.execute(delete_q)
        db_session.commit()

    except Exception as e:
        print(e)

    return f"clean done,took: {(time.time()-start)} "


@celery.task()
def cmc_routine() -> str:
    start = time.time()
    print("fetching the hacky cache")
    try:

        cmcs = fetch_cmc_pub()
        cachetool.set_cache("cmcs", list(cmcs))

    except Exception as e:
        print(e)

    return f"cmc routine done,took: {(time.time()-start)} "

