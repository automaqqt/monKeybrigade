import ast
import time
from datetime import datetime, timedelta

import requests  # , aioredis, os,
from sqlalchemy import desc, exists, func, update
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlmodel import Field, Session, SQLModel, create_engine, or_, select

import cachetool, config
from models import Drop, Work

engine = create_engine(
    "postgresql://postgres:postgres@db:5432/foo",
    pool_recycle=3600,
    pool_size=12,
)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def init_db():
    trying = True
    while trying:
        if engine:
            try:
                SQLModel.metadata.create_all(engine)
                trying = False
            except Exception as e:
                print(e)


def commit_or_rollback(new_obj):
    with Session(engine) as session:
        try:
            session.add(new_obj)
            session.commit()
            session.refresh(new_obj)
        except Exception as e:
            print(e, "rolling back")
            session.rollback()
            return None
        return new_obj


def exc_statement(statement):
    with Session(engine) as session:
        try:
            result = session.execute(statement)
            session.commit()
        except Exception as e:
            print(e, "rolling back")
            session.rollback()
            return None
        return True



def update_elected(handle, elected):
    stmt = (
        update(Drop)
        .where(Drop.handle == handle)
        .values(winners=str(elected), state="ELECTED")
        .execution_options(synchronize_session="fetch")
    )
    return exc_statement(stmt)

def update_done(handle, tx_id):
    stmt = (
        update(Drop)
        .where(Drop.handle == handle)
        .values(trx_id=tx_id, state="DONE")
        .execution_options(synchronize_session="fetch")
    )
    return exc_statement(stmt)          


def retrieve_drops(before: str = None, after: str = None, limit: int = 100, sort: str = "asc"):
    with Session(engine) as session:

        qry = session.query(Drop)

        if before:
            qry = qry.filter(Drop.issue_time <= before)
        if after:
            qry = qry.filter(Drop.issue_time >= after)

        if sort == "desc":
            qry = qry.order_by(desc("issue_time"))
        else:
            qry = qry.order_by("issue_time")
        if limit:
            qry = qry.limit(limit).distinct()
        else:
            qry = qry.limit(100).distinct()
        out = [
            {
                "issue_time": q.issue_time,
                "type": q.type,
                "winners": [n.strip() for n in ast.literal_eval(q.winners)] if q.winners != "" else [],
                "trx_id": q.trx_id,
                "state": q.state,
            }
            for q in qry
        ]
        return out

def retrieve_work(before: str = None, after: str = None, sort: str = "asc", limit: int= 100, monkeysOnly: bool= False, user:str = None):
    with Session(engine) as session:

        qry = session.query(Work)
        if user:
            qry = qry.filter(Work.user == user)
        if before:
            qry = qry.filter(Work.block_time <= before)
        if after:
            qry = qry.filter(Work.block_time >= after)
        if monkeysOnly:
            qry = qry.filter(Work.mnky == True)

        if sort == "desc":
            qry = qry.order_by(desc("block_time"))
        else:
            qry = qry.order_by("block_time")
        
        if limit:
            qry = qry.limit(limit).distinct()
        else:
            qry = qry.limit(100).distinct()
        
        out = qry.distinct()

        return out



def get_cmc():
    cmcs = requests.get(
        f"https://connect.cryptomonkeys.cc/accounts/api/v1/user_list/?code={config.cmc_key}"
    ).json()["data"]
    return cmcs


def fetch_cmc_pub(cur_time=None, worker_only: bool = False):
    cmcs = get_cmc()
    cmc_full = []
    for cm in cmcs:
        cmc_full.append(cm["mainUser"])
        for wal in cm["wallets"]:
            cmc_full.append(wal)
    cmc_full = set(cmc_full)

    if worker_only:
        worker = list(
            retrieve_work(
                cur_time.isoformat()[:-3], (cur_time - timedelta(hours=2)).isoformat()[:-3], "desc", monkeysOnly=True
            )
        )

        eligible = []
        for work in worker:
            if work.user in cmc_full:
                eligible.append(work.user)
        return list(set(eligible))
    else:
        return cmc_full
