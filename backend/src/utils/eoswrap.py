from datetime import datetime, timedelta
import datetime as dt
import eospyabi.cleos
import eospyabi.keys
from eospyabi.types import Abi, Action
from eospyabi.utils import parse_key_file
import os
import pytz, time
import json, requests

from utils.waxapis import AH, WAXMonitor
import random
from config import drop_account

from utils.disclog import postHook

drive = AH()
wax = WAXMonitor()


def scan_assets(account, rarity: str = None, template_id: str = None):
    scanning = True
    page = 1
    out = []
    res_total = []
    while scanning:
        if template_id:
            resp = drive.assets(owner=account, page=page, template_id=template_id).json()["data"]
        else:
            resp = drive.assets(owner=account, page=page).json()["data"]
        res_total += [res for res in resp]
        if len(resp) == 0:
            scanning = False
        page += 1
        time.sleep(0.7)
    # print(len(resp))
    if rarity:
        for res in res_total:
            if "rarity" in res["template"]["immutable_data"].keys():
                if res["template"]["immutable_data"]["rarity"].lower() == rarity:
                    out.append(res["asset_id"])
    else:
        out = [res["asset_id"] for res in res_total]
    # print(out)
    return out


def grab_winners(winners, rarity: str = None, template_id: str = None):
    asset_list = scan_assets(drop_account, rarity, template_id)
    if len(asset_list) < len(winners):
        print("NOT ENOUGH ASSETS IN THE DROP ACCOUNT! REFILL PLOX...SLEEPING THE TASK")
        time.sleep(7200)
    out = {}
    for winner in winners:
        rnd = random.randint(0, len(asset_list) - 1)
        asset = asset_list.pop(rnd)
        out[winner] = asset
    return out


def pick_best_waxnode(type, cutoff: int = 8):

    resp = wax.endpoints(type=type).json()
    out = []
    for node in resp:
        if node["weight"] > cutoff:
            out.append(node["node_url"])
    if len(out) < 1:
        out = ["https://api.waxsweden.org"]
    return out


def get_local_key():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    key_file = os.path.join(script_dir, f"{drop_account}_eosio.key")
    key = parse_key_file(key_file)
    return key


def build_memo(mode, n):
    memo = "Placeholder you lucky dude"
    if mode == "raffle":
        memo = f"monKeybrigade: You are winner #{n+1} of the raffle @hour {datetime.utcnow().hour} on the {datetime.utcnow().date()}"
    return memo


def transfer_assets(node, targets, mode, memo = None):
    try:
        key = get_local_key()
        ce = eospyabi.cleos.Cleos(url=node)
        payloads = []
        for n, target in enumerate(targets):
            if memo is None:
                memo = build_memo(mode, n)
            payload = {
                "account": "atomicassets",
                "name": "transfer",
                "authorization": [
                    {
                        "actor": drop_account,
                        "permission": "active",
                    }
                ],
            }
            act_params = {
                "from": drop_account,
                "to": f"{target}",
                "asset_ids": [int(targets[target])],
                "memo": memo,
            }
            # Converting payload to binary
            data = ce.abi_json_to_bin(payload["account"], payload["name"], act_params)

            # Inserting payload binary form as "data" field in original payload
            payload["data"] = data["binargs"]
            payloads.append(payload)
        # final transaction formed
        trx = {"actions": payloads}
        trx["expiration"] = str(
            (dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC)
        )

        resp = ce.push_transaction(trx, eospyabi.keys.EOSKey(key), broadcast=True)
        print(resp["transaction_id"])
        for n, target in enumerate(targets):
            memo = build_memo(mode, n)
            postHook(f"Congrats {target}: {memo}")
        return True, resp["transaction_id"]
    except Exception as e:
        print(e)
        return False, None


def transfer_wrap(winners, mode, rarity: str = None,template_id: str = None, memo: str = None):
    nodes_avail = pick_best_waxnode("api")
    winrs = grab_winners(winners, rarity, template_id)
    print(mode, rarity, winrs)
    trying = True
    retry = 10
    round = 0
    while trying and round < retry:
        node = nodes_avail.pop(random.randint(0, len(nodes_avail) - 1))
        print(round, node)

        transfered, tx_id = transfer_assets(node, winrs, mode, memo)
        # transfered,tx_id = transfer_assets('https://testnet.waxsweden.org',winrs,mode)
        round += 1
        if transfered:
            trying = False
        else:
            time.sleep(10 * (2**round))

    return tx_id
