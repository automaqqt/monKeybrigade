#### NEW SERIAL

from listener.plugins.brigade import BrigadePlugin
from listener.types.config import ListenerConfig
from typing import Dict
from db import db_session

brigadeconfig = ListenerConfig(
        wanted_traces=['logwork'],
        plugin=BrigadePlugin(db_session),
        fetch_traces=True
    )

leap_listener_config: Dict[str,ListenerConfig] = {
    'workopt': brigadeconfig
}