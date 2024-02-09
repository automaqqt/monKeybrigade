import time, datetime, eospyabi.cleos
from typing import Dict
from listener.types.config import ListenerConfig

from listener.util import DictObj

class LeapListener:
    def __init__(
        self,
        config: Dict[str,ListenerConfig],
        leap_rpc: str = "http://waxapi.ledgerwise.io",
        start_block_num: int = 0,
        time_to_run_behind: int = 10
    ):
        self.cleos = eospyabi.cleos.Cleos(url=leap_rpc)
        self.backup_cleos = ['https://wax.eosdac.io', 'https://wax.blacklusion.io', 'https://history-wax-mainnet.wecan.dev', 'https://wax.eosdublin.io', 'https://wax.cryptolions.io'] 
        if leap_rpc not in self.backup_cleos:
            self.backup_cleos.append(leap_rpc)

        self.time_to_run_behind = time_to_run_behind
        self.current_block_num = self.cleos.get_info()["head_block_num"]
        if start_block_num != 0:
            self.current_block_num = start_block_num
        self.current_block = self.cleos.get_block(self.current_block_num)
        self.config = config
        self.plugins = {}
        self.load_all_plugins()
        self.wanted_actions = [key for key in self.config]
        self.error_log = []
        self.last_failed = 0

    def load_all_plugins(self):
        for key in self.config: 
            for t in self.config[key].wanted_traces:
                self.plugins[t] = self.config[key].plugin

    async def process_blocks(self):
        start_time = time.time()
        while True:  
            new_block_available = False
            try:
                new_block_available = await self.next_block()
                if new_block_available:
                        for tx in self.current_block['transactions']:
                            if type(tx['trx']) != str:
                                actions_to_process = await self.extract_wanted_actions(tx)
                                if actions_to_process:
                                    for trace in actions_to_process:
                                        self.plugins[trace['name']].process(trace, self.current_block)
                                    
            except Exception as e:
                self.error_log.append(f"ERROR | {datetime.datetime.now().isoformat()}: {e}\nContext: \ncurrent_block_num: {self.current_block_num} ")
            
            if not new_block_available:
                time.sleep(0.51)

            if self.current_block_num % 1000 == 0 and new_block_available:
                time.sleep(1)
                head_block = int(self.cleos.get_info()["head_block_num"])
                sec_to_sync = (head_block-self.current_block_num)*((time.time()-start_time)/1000)
                formatted_time_to_sync = f'{int(sec_to_sync/60)}:{int(sec_to_sync%60)} m:s'
                print(f'INFO | current processed block: {self.current_block_num} | blocks behind: {head_block-self.current_block_num} | estimate time to sync: {formatted_time_to_sync if self.is_x_seconds_behind(self.current_block,30) else "synced"} | error_log length: {len(self.error_log)}')
                start_time = time.time()

    async def extract_wanted_actions(self, tx):
        actions_to_process = []
        for act_raw in tx['trx']['transaction']['actions']:
            act = DictObj(act_raw)
            if act.name in self.wanted_actions:
                if act.name in self.config[act.name].wanted_traces:
                    actions_to_process.append(act_raw)
                if self.config[act.name].fetch_traces:
                    trace = await self.find_first_trace(tx['trx']['id'],act.name)
                    if trace:
                        actions_to_process.append(trace)

        return actions_to_process
    
    async def find_first_trace(self, tx_id, act):
        fetching = True
        full_tx = None
        while fetching:
            try:
                full_tx = self.cleos.get_transaction(tx_id)
                if "traces" not in full_tx.keys():
                    raise Exception("No traces")
                fetching=False
            except Exception as e:
                print(e)
                time.sleep(0.5)
                next_index = (self.backup_cleos.index(self.cleos._prod_url) + 1) % len(self.backup_cleos)
                self.cleos = eospyabi.cleos.Cleos(url=self.backup_cleos[next_index])

        for trace in full_tx['traces']:
            if trace['act']['name'] in self.config[act].wanted_traces:
                return trace['act']

        return None

    async def next_block(self) -> bool:
        if self.is_x_seconds_behind(block=self.current_block, seconds=self.time_to_run_behind) and time.time() - self.last_failed > 0.2:
            try:
                self.current_block = self.cleos.get_block(self.current_block_num)
            except Exception as e:
                self.last_failed = time.time()
                next_index = (self.backup_cleos.index(self.cleos._prod_url) + 1) % len(self.backup_cleos)
                self.cleos = eospyabi.cleos.Cleos(url=self.backup_cleos[next_index])
                raise e
            self.current_block_num += 1
            return True
        return False
    
    def is_x_seconds_behind(self, block, seconds) -> bool:
        return ((datetime.datetime.fromisoformat(block['timestamp']) + datetime.timedelta(seconds=seconds)).isoformat() < datetime.datetime.utcnow().isoformat())
