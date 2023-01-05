import time, datetime, eospy.cleos
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
        self.cleos = eospy.cleos.Cleos(url=leap_rpc)
        self.time_to_run_behind = time_to_run_behind
        self.current_block_num = self.cleos.get_info()["head_block_num"]
        if start_block_num != 0:
            self.current_block_num = start_block_num
        self.current_block = self.cleos.get_block(self.current_block_num)
        self.config = config
        self.plugins = {}
        self.load_all_plugins()
        self.wanted_actions = [key for key in self.config]

    def load_all_plugins(self):
        for key in self.config: 
            for t in self.config[key].wanted_traces:
                self.plugins[t] = self.config[key].plugin

    async def process_blocks(self):
        while True:
            start = time.time()

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
                print(f"ERROR | {datetime.datetime.now().isoformat()}: {e}\nContext: \ncurrent_block_num: {self.current_block_num} ")
            
            rtime = time.time()-start
            if rtime < 0.4 and rtime > 0:
                time.sleep(0.4 - rtime)

            print([self.current_block_num, self.current_block['timestamp']])

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
                fetching=False
            except Exception as e:
                print(e)
                time.sleep(1)

        for trace in full_tx['traces']:
            if trace['act']['name'] in self.config[act].wanted_traces:
                return trace['act']

        return None

    async def next_block(self) -> bool:
        if (datetime.datetime.fromisoformat(self.current_block['timestamp']) + datetime.timedelta(seconds=self.time_to_run_behind)).isoformat() < datetime.datetime.utcnow().isoformat():
            self.current_block = self.cleos.get_block(self.current_block_num)
            self.current_block_num += 1
            return True
        return False
