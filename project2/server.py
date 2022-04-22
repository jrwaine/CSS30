import time
from typing import Any, Dict, List, Optional

import click
import colorama
from colorama import Back, Fore

from .signer import get_key_pair


class Server:
    MAX_RESOURCE_TIME_S: int = 30

    def __init__(self, n_resources: int) -> None:
        self.n_resources = n_resources
        self.n_clients = 0
        self.resource_time = Dict[int, Optional[float]] = {
            i: None for i in range(n_resources)
        }
        self.resource_owner: Dict[int, Optional[int]] = {
            i: None for i in range(n_resources)
        }
        self.queue_resources: Dict[int, List[int]] = {i: [] for i in range(n_resources)}
        self.pub_key, self.priv_key = get_key_pair()

    @property
    def resources_time_for_timeout(self) -> Dict[int, Optional[float]]:
        return {i: self.time_for_timeout(i) for i in range(self.n_resources)}

    @property
    def time_for_timeout(self, resource: int) -> Optional[float]:
        val = self.resource_time[resource]
        return None if val is None else round(time.time() - val, 2)

    def serve(self):
        ...

    def send_token(self, resource: int):
        ...

    def timeout_token(self):
        ...

    def token_liberation(self, pid: int, resource: int):
        ...

    def route_ask_token(self, resource: int) -> Optional[int]:
        ...


class ServerUI:
    def __init__(self, s: Server) -> None:
        self.server = s

    def draw_state(self):
        serv = self.server
        print(f"{Fore.YELLOW}Number of resources: {serv.n_resources}")
        print(f"{Fore.YELLOW}Number of clients: {serv.n_clients}")
        print(f"{Fore.YELLOW}Public key: {serv.pub_key}")
        print(f"{Fore.YELLOW}Private key: {serv.priv_key}")
        print()
        print(f"{Fore.YELLOW}Resources owners: {serv.resource_owner}")
        print(f"{Fore.YELLOW}Resources timeout: {serv.resources_time_for_timeout}")
        print(f"{Fore.YELLOW}Resources queues: {serv.queue_resources}")

    def draw(self):
        click.clear()

        print(f"{Fore.YELLOW}------------ SERVER STATE ------------")
        self.draw_state()
        print(f"{Fore.YELLOW}--------------------------------------")
