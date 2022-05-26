import time
from threading import Thread
from typing import Dict, List, Optional

import click
import colorama
from colorama import Fore

colorama.init(autoreset=True)


class ResourceHandler:
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
        self.ui = ResourceHandlerUI(self)

    def start(self):
        self.t = Thread(target=self.serve_loop, daemon=True)
        self.t.start()

    def serve_loop(self):
        def check_resources_time():
            for resource, res_time in self.resource_time.items():
                if res_time is None:
                    continue
                diff_time = time.time() - res_time
                # Liberate a fter some time
                if diff_time > self.MAX_RESOURCE_TIME_S:
                    self.release_resource(self.resource_owner[resource], resource)

        def check_resources_queue():
            for resource, clients in self.queue_resources.items():
                owner = self.resource_owner[resource]
                if owner is not None:
                    continue
                if len(clients) == 0:
                    continue
                client_next = clients.pop(0)
                self.get_resource(client_next, resource)

        while True:
            time.sleep(0.1)
            check_resources_time()
            check_resources_queue()
            if not self.interactive:
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

    def owner(self, resource: int) -> Optional[int]:
        return self.resource_owner[resource]

    def add_client(self) -> int:
        client_id = len(self.clients)
        self.clients.append(client_id)
        return client_id

    def get_resource(self, client_id: int, resource: int) -> bool:
        if self.resource_owner[resource] is not None:
            queue_res = self.queue_resources[resource]
            if client_id not in queue_res:
                queue_res.append(client_id)
            return False
        self.resource_owner[resource] = client_id
        self.resource_time[resource] = time.time()
        return True

    def release_resource(self, client_id: int, resource: int) -> bool:
        if self.resource_owner[resource] != client_id:
            return False
        self.resource_owner[resource] = None
        self.resource_time[resource] = None
        return True


class ResourceHandlerUI:
    def __init__(self, res_hdlr: ResourceHandler) -> None:
        self.res_hdlr = res_hdlr

    def _draw_state(self):
        res_hdlr = self.res_hdlr
        print(f"{Fore.YELLOW}Number of resources: {res_hdlr.n_resources}")
        print(f"{Fore.YELLOW}Number of clients: {res_hdlr.n_clients}")
        print()
        print(f"{Fore.YELLOW}Resources owners: {res_hdlr.resource_owner}")
        print(f"{Fore.YELLOW}Resources timeout: {res_hdlr.resources_time_for_timeout}")
        print(f"{Fore.YELLOW}Resources queues: {res_hdlr.queue_resources}")

    def draw(self):
        click.clear()

        print(f"{Fore.YELLOW}------------ RESOURCES STATE ------------")
        self._draw_state()
        print(f"{Fore.YELLOW}-----------------------------------------")


_res_hdlr = None


def setup_resources_hdlr(n_resources: int, interactive: bool = True):
    global _res_hdlr
    _res_hdlr = ResourceHandler(n_resources, interactive)
    _res_hdlr.start()


def get_resources_hdlr():
    global _res_hdlr
    if _res_hdlr is None:
        raise BaseException("Server is None")
    return _res_hdlr
