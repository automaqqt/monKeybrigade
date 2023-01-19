import os
import random
import time
from concurrent.futures.thread import _worker
from datetime import datetime, timedelta

import requests
from celery import Celery
from sqlalchemy import exists, func
from sqlmodel import select, Session

import cachetool
import config
from db import (
    commit_or_rollback,
    db_session,
    fetch_cmc_pub,
    update_done,
    update_elected,
    engine
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
    for winner in elected:
        cachetool.set_target_cooldown(winner,cur_time.isoformat()[:-3])
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

        cut = cachetool.get_cache("db")["last_elec"]
        if cut == "None":
            cut = datetime.utcnow().isoformat()
        cmcs = fetch_cmc_pub()
        cachetool.set_cache("cmcs", list(cmcs))
        dat = datetime.fromisoformat(cut)+timedelta(seconds=7200)
        eligs = fetch_cmc_pub(dat,True)
        db_cache = retrieve_db_status(eligs)
        cachetool.set_cache("db",db_cache)

    except Exception as e:
        print(e)

    return f"cmc routine done,took: {(time.time()-start)} "

def retrieve_db_status(eligs):
    query = select([func.count()])
    start = time.perf_counter()
    with Session(engine) as session:  
        lastelec = session.query(Drop).where(Drop.type=="raffle").order_by(Drop.issue_time.desc()).first()
        drops_7d = session.query(Drop).where(Drop.issue_time>=(datetime.utcnow()-timedelta(days=7)).isoformat()[:-3]).all()
        drops_30d = session.query(Drop).where(Drop.issue_time>=(datetime.utcnow()-timedelta(days=30)).isoformat()[:-3]).all()
        drops_365d = session.query(Drop).where(Drop.issue_time>=(datetime.utcnow()-timedelta(days=365)).isoformat()[:-3]).all()
        
        countmonkeywork_60 = len(session.query(Work).where(Work.block_time>=(datetime.utcnow()-timedelta(seconds=3600)).isoformat()[:-3]).where(Work.mnky).all())
        countmonkeywork_1440 = len(session.query(Work).where(Work.block_time>=(datetime.utcnow()-timedelta(hours=24)).isoformat()[:-3]).where(Work.mnky).all())
        count_all_1440 = len(session.query(Work).where(Work.block_time>=(datetime.utcnow()-timedelta(hours=24)).isoformat()[:-3]).all())

    count_7d = sum([len(r.winners.split(",")) for r in drops_7d])
    count_30d = sum([len(r.winners.split(",")) for r in drops_30d])
    count_365d = sum([len(r.winners.split(",")) for r in drops_365d])
    db_info={
        "count_work": [countmonkeywork_60,countmonkeywork_1440,count_all_1440],
        "eligible": len(eligs),
        "last_elec": lastelec.issue_time if lastelec else "None",
        "mining_hist":[count_7d,count_30d,count_365d]
    }
    print(f"db_retrieve took {time.perf_counter()-start}")
    return db_info
