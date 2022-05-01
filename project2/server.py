import time
from threading import Thread
from typing import Any, Callable, Dict, List, Optional, Set

import click
import colorama
import Pyro5.api
import Pyro5.core
from colorama import Back, Fore

from .msgs import ResourceLiberation, ServerResp
from .signer import get_key_pair, sign_message

colorama.init(autoreset=True)


class Server:
    MAX_RESOURCE_TIME_S: int = 30

    def __init__(self, n_resources: int) -> None:
        self.n_resources = n_resources
        self.pub_key, self.priv_key = get_key_pair()

        self.resource_time: Dict[int, Optional[float]] = {
            i: None for i in range(n_resources)
        }

        self.callbacks: List[Callable] = []

        # Int is index in self.callbacks
        self.resource_owner: Dict[int, Optional[int]] = {
            i: None for i in range(n_resources)
        }
        self.clients_sent_pub_key: Set[int] = set()
        self.queue_resources: Dict[int, List[int]] = {i: [] for i in range(n_resources)}
        self.ui = ServerUI(self)

    def _activate_server(self):
        self.daemon = Pyro5.api.Daemon()
        uri = self.daemon.register(self)
        # print(uri)
        ns = Pyro5.core.locate_ns()
        ns.register("MyApp", uri)
        uri = self.daemon.register(self, force=True)
        # daemon.requestLoop()
        self.daemon.requestLoop()

    def __call__(self) -> Any:
        t = Thread(target=self.serve_loop, daemon=True)
        t.start()
        print(f"{Fore.GREEN}Server is active")

    @property
    def n_clients(self):
        return len(self.callbacks)

    @property
    def resources_time_for_timeout(self) -> Dict[int, Optional[float]]:
        return {i: self.time_for_timeout(i) for i in range(self.n_resources)}

    def time_for_timeout(self, resource: int) -> Optional[float]:
        val = self.resource_time[resource]
        return None if val is None else round(time.time() - val, 2)

    def _check_resource_timeouts(self):
        timed_out = []
        for resource, time_passed in self.resources_time_for_timeout.items():
            if time_passed is None:
                continue
            if time_passed >= self.MAX_RESOURCE_TIME_S:
                timed_out.append(resource)

        for resource in timed_out:
            self._timeout_resource(resource)

    def _send_queue_resources(self):
        for resource, pids in self.queue_resources.items():
            if len(pids) == 0:
                continue
            owner = self.resource_owner[resource]
            if owner is not None:
                continue
            first_pid = pids[0]
            # Send token for first pid in list
            self._send_resource(first_pid, resource)
            self.resource_owner[resource] = first_pid
            # Remove pid from list
            pids.pop(0)

    def draw_loop(self):
        loop_count = 0
        while True:
            loop_count += 1
            print("here", loop_count)
            time.sleep(0.5)
            self._check_resource_timeouts()
            self._send_queue_resources()
            self.ui.draw()

    def serve_loop(self):
        t = Thread(target=self.draw_loop)
        t.start()
        self._activate_server()

    def _get_resource_liberation(
        self, pid: int, resource: int, is_liberated: bool
    ) -> ResourceLiberation:
        msg = ResourceLiberation(
            is_liberated=is_liberated,
            resource=resource,
        )
        return msg

    def _get_resp_send(self, pid: int, resource: int, is_liberated: bool) -> ServerResp:
        res_liber = self._get_resource_liberation(pid, resource, is_liberated)
        send_pub_key = True if (pid not in self.clients_sent_pub_key) else False
        msg_res_liber = res_liber.to_json()
        msg = ServerResp(
            msg=sign_message(msg_res_liber, self.priv_key),
            pub_key=self.pub_key if send_pub_key else None,
        )
        self.clients_sent_pub_key.add(pid)
        return msg

    def _send_resource(self, pid: int, resource: int):
        msg = self._get_resp_send(pid, resource, True)
        callback = self.callbacks[pid]
        msg_enc = sign_message(msg.to_json(), self.priv_key)
        # cli._pyroClaimOwnership()
        callback._pyroClaimOwnership()
        callback.route_receive_resource(msg_enc)

    def _timeout_resource(self, resource: int):
        self.resource_owner[resource] = None

    @Pyro5.api.expose
    def route_resource_liberation(self, pid: int, resource: int) -> bool:
        owner = self.resource_owner[resource]
        # Check if process really owns resource
        if pid != owner:
            # Check if pid is in queue
            if pid not in self.queue_resources[resource]:
                return False
            else:
                self.queue_resources[resource].remove(pid)
        # Remove owner
        self.resource_owner[resource] = None
        return True

    @Pyro5.api.expose
    def route_ask_resource(self, pid: int, resource: int) -> str:
        owner = self.resource_owner[resource]
        # self._send_resource(pid, resource)
        is_liberated = True
        if owner is not None:
            is_liberated = False
            queue_res = self.queue_resources[resource]
            # If asking not already owns and is not in queue
            if owner != pid and pid not in queue_res:
                queue_res.append(pid)
        msg = self._get_resp_send(pid, resource, is_liberated)
        if is_liberated:
            self.resource_owner[resource] = pid
        msg_enc = sign_message(msg.to_json(), self.priv_key)
        return msg_enc

    @Pyro5.api.expose
    def route_get_pid(self, callback: Callable) -> int:
        self.callbacks.append(callback)
        return len(self.callbacks) - 1


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
