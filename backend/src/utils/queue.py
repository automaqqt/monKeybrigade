import datetime as dt
from typing import List, Dict
import eospy.cleos
import eospy.keys
from eospy.types import Abi, Action
from eospy.utils import parse_key_file
import os
import pytz, time
import random

from utils.disclog import postHook
from utils.waxapis import AH


class DropInterface:
    def __init__(
        self,
        winners: List[str],
        memo: str,
        rarity: str = None,
        template_id: str = None
    ):
        self.winners = winners
        self.memo = memo
        self.rarity = rarity
        self.template_id = template_id

class DropQueue:
    def __init__(
        self,
        pool_account: str = 'cmcdrops4all',
        pool_account_key: eospy.keys.EOSKey = None,
        leap_rpc: str = "http://waxapi.ledgerwise.io",
        wait_sec_until_confirm: int = 7,
        new_node_after_retries: int = 10
    ):
        self.cleos = eospy.cleos.Cleos(url=leap_rpc)
        self.pool_account = pool_account
        self.pool_account_key = pool_account_key
        self.load_eos_key()
        self.wait_until_confirm = wait_sec_until_confirm
        self.new_node = new_node_after_retries
        self.last_asset_refresh = (dt.datetime.utcnow() + dt.timedelta(seconds=60)).isoformat()
        self.queue : List[DropInterface] = []
        self.assets = []
        

    def add(self, drop: DropInterface):
        self.queue.append(drop)

    def process_queue(self):
        while True:
            try:
                current = self.queue.pop(0)
                if current:
                    winrs = self.grab_winners(current.winners, current.rarity, current.template_id)
                    self.retry_push_tx(winrs, current.memo)
            except IndexError:
                print("no item in queue")
                pass
            time.sleep(0.5)

    def load_eos_key(self):
        if not self.pool_account_key:
            script_dir = os.path.dirname(os.path.realpath(__file__))
            key_file = os.path.join(script_dir, f"{self.pool_account}_eosio.key")
            self.pool_account_key = parse_key_file(key_file)

    def retry_push_tx(self, winrs, memo) -> bool:
        round = 0
        while round < self.new_node:
            transfered = self.transfer_assets(winrs, memo)
            round += 1
            if transfered:
                return True
            else:
                time.sleep(10 * (2**round))

        return False

    def update_asset_cache(self):
        page = 1
        res_total = []
        print('updatin gasset cache')
        while True:
            resp = AH().assets(owner=self.pool_account, page=page).json()["data"]
            res_total.append(resp)
            if len(resp) == 0:
                self.assets = res_total
                self.last_asset_refresh = (dt.datetime.utcnow() + dt.timedelta(seconds=60)).isoformat()
                return True
            page += 1
            time.sleep(0.7)

    def filter_assets(self, rarity: str = None, template_id: str = None):
        out = [res["asset_id"] for res in self.assets]

        if rarity:
            out = []
            for res in self.assets:
                if "rarity" in res["template"]["immutable_data"].keys():
                    if res["template"]["immutable_data"]["rarity"].lower() == rarity:
                        out.append(res["asset_id"])

        if template_id:
            out = []
            for res in self.assets:
                if res["template"]["template_id"].lower() == template_id:
                    out.append(res["asset_id"])

        return out
        
    
    def grab_winners(self, current_drop:DropInterface):
        if self.last_asset_refresh < dt.datetime.utcnow().isoformat():
            self.update_asset_cache()

        asset_list = self.filter_assets(current_drop.rarity, current_drop.template_id)
        if len(asset_list) < len(current_drop.winners):
            print("NOT ENOUGH ASSETS IN THE DROP ACCOUNT! REFILL PLOX...SLEEPING THE TASK")
            time.sleep(7200)

        out = {}
        for winner in current_drop.winners:
            assets = []
            for x in range(current_drop.winners[winner]):
                rnd = random.randint(0, len(asset_list) - 1)
                asset = asset_list.pop(rnd)
                assets.append(asset)
            out[winner] = assets
        return out

    
    def transfer_assets(self, targets, memo):
        try:
            payloads = []
            for n, target in enumerate(targets):
                payload = {
                    "account": "atomicassets",
                    "name": "transfer",
                    "authorization": [
                        {
                            "actor": self.pool_account,
                            "permission": "active",
                        }
                    ],
                }
                act_params = {
                    "from": self.pool_account,
                    "to": f"{target}",
                    "asset_ids": targets[target],
                    "memo": memo,
                }

                data = self.cleos.abi_json_to_bin(payload["account"], payload["name"], act_params)

                payload["data"] = data["binargs"]
                payloads.append(payload)

            trx = {"actions": payloads}
            trx["expiration"] = str(
                (dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC)
            )

            resp = self.cleos.push_transaction(trx, self.pool_account_key, broadcast=True)
            print(resp["transaction_id"])

            time.sleep(self.wait_until_confirm)

            success = self.cleos.get_transaction(resp["transaction_id"])
            print(success)

            postHook(f"Congrats {target}: {memo}")
            return True
            
        except Exception as e:
            print(e)
            return False

        
