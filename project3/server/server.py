import time
from threading import Thread
from typing import Any, Callable, Dict, List, Optional, Set

import click
import colorama
from colorama import Back, Fore

from .msgs import ResourceLiberation, ServerResp

colorama.init(autoreset=True)


class Server:
    MAX_RESOURCE_TIME_S: int = 30

    def __init__(self, n_resources: int, interactive: bool = True) -> None:
        self.n_resources = n_resources
        self.interactive = interactive

        self.resource_time: Dict[int, Optional[float]] = {
            i: None for i in range(n_resources)
        }
        self.clients: List[int] = []

        # Int is index in self.callbacks
        self.resource_owner: Dict[int, Optional[int]] = {
            i: None for i in range(n_resources)
        }
        self.queue_resources: Dict[int, List[int]] = {i: [] for i in range(n_resources)}
        self.ui = ServerUI(self)

    def start(self):
        t = Thread(target=self.draw_loop, daemon=True)
        t.start()

    def draw_loop(self):
        while(True):
            time.sleep(0.25)
            if(not self.interactive):
                continue
            self.ui.draw()
    
    @property
    def n_clients(self):
        return len(self.callbacks)

    @property
    def resources_time_for_timeout(self) -> Dict[int, Optional[float]]:
        return {i: self.time_for_timeout(i) for i in range(self.n_resources)}

    def time_for_timeout(self, resource: int) -> Optional[float]:
        val = self.resource_time[resource]
        return None if val is None else round(time.time() - val, 2)

class ServerUI:
    def __init__(self, s: Server) -> None:
        self.server = s

    def _draw_state(self):
        serv = self.server
        print(f"{Fore.YELLOW}Number of resources: {serv.n_resources}")
        print(f"{Fore.YELLOW}Number of clients: {serv.n_clients}")
        print()
        print(f"{Fore.YELLOW}Resources owners: {serv.resource_owner}")
        print(f"{Fore.YELLOW}Resources timeout: {serv.resources_time_for_timeout}")
        print(f"{Fore.YELLOW}Resources queues: {serv.queue_resources}")

    def draw(self):
        click.clear()

        print(f"{Fore.YELLOW}------------ SERVER STATE ------------")
        self._draw_state()
        print(f"{Fore.YELLOW}--------------------------------------")
