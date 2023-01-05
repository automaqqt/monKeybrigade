from typing import List

class ListenerConfig:
    def __init__(
        self,
        wanted_traces: List[str],
        plugin: any,
        fetch_traces: bool = False,
    ):
        self.wanted_traces = wanted_traces
        self.plugin = plugin
        self.fetch_traces = fetch_traces