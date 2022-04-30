import enum
import time
from threading import Thread
from typing import Any, Dict, List, Literal, Optional

import click
import colorama
import Pyro5.api
from colorama import Back, Fore

from .msgs import ResourceLiberation, ServerResp, load_json
from .server import Server
from .signer import validate_message

colorama.init(autoreset=True)


class States(enum.Enum):
    HELD = 1
    WANTED = 2
    RELEASED = 3


class Client:
    def __init__(self, n_resources: int) -> None:
        self.n_resources = n_resources
        self.curr_resources: Dict[int, States] = {
            i: States.RELEASED for i in range(n_resources)
        }
        self.pub_key = None

        ns = Pyro5.core.locate_ns()
        uri = ns.lookup("MyApp")
        self.res_server = Pyro5.api.Proxy(uri)
        self.ui = ClientUI(self)

    def __call__(self) -> Any:
        t = Thread(target=self.serve_loop, daemon=True)
        t.start()
        print(f"{Fore.GREEN}Server is active")

    def serve_loop(self):
        while True:
            self.ui.draw()

    def take_action(self, action: Literal["ASK", "RELEASE"], resource: int):
        resource_state = self.curr_resources[resource]

        if action.upper() == "ASK" and resource_state in (States.HELD, States.WANTED):
            click.echo(f"Already holding resource {resource}")
            return
        elif action.upper() == "RELEASE" and resource_state == States.RELEASED:
            click.echo(f"Already released resource {resource}")
            return

        func = (
            self._release_resource
            if action.upper() == "RELEASE"
            else self._ask_resource
        )
        func(resource)

    def _release_resource(self, resource: int):
        server = self.res_server
        msg = self.res_server.route_resource_liberation(self.pid, resource)
        if not msg:
            print(f"{Fore.RED}Unable to release resource {resource}")
        else:
            self.curr_resources[resource] = States.RELEASED

    def _ask_resource(self, resource: int):
        server = self.res_server
        msg = server.route_ask_resource(self.pid)
        server_resp = ServerResp(**load_json(msg))
        if self.pub_key is None:
            self.pub_key = server_resp

        try:
            res_msg = validate_message(server_resp.msg, self.pub_key)
            res_liber = ResourceLiberation(**load_json(res_msg))
        except Exception as e:
            print(f"{Fore.RED}Unable to decode message with key {self.pub_key}")
        else:
            if res_liber.is_liberated:
                self.curr_resources[resource] = States.HELD
            else:
                self.curr_resources[resource] = States.WANTED

    @Pyro5.api.expose
    def route_receive_resource(self, msg: str):
        server_resp = ServerResp(**load_json(msg))
        if self.pub_key is None:
            self.pub_key = server_resp.pub_key

        try:
            res_msg = validate_message(server_resp.msg, self.pub_key)
            res_liber = ResourceLiberation(**load_json(res_msg))
        except Exception as e:
            print(f"{Fore.RED}Unable to decode route message with key {self.pub_key}")
        else:
            resource = res_liber.resource
            if res_liber.is_liberated:
                self.curr_resources[resource] = States.HELD


class ClientUI:
    def __init__(self, c: Client) -> None:
        self.client = c

    def draw_state(self):
        client = self.client
        print(f"{Fore.YELLOW}Number of resources: {client.n_resources}")
        print(f"{Fore.YELLOW}Pub server key: {client.pub_key}")
        print()
        print(
            f"{Fore.YELLOW}Current states: "
            + {k: v.name for k, v in client.curr_resources.items()}
        )

    def draw_options(self):
        client = self.client

        action = click.prompt(
            "What action you want to take?",
            type=click.Choice(["ASK", "RELEASE", "NONE"], case_sensitive=False),
        )
        if action.upper() == "NONE":
            return
        if action.upper() == "ASK":
            if all(
                v in (States.HELD, States.WANTED)
                for v in client.curr_resources.values()
            ):
                click.echo(
                    "Holding/Asked all resources already. Unable to ask for more"
                )
                return
        elif action.upper() == "RELEASE":
            if all(v in (States.RELEASED) for v in client.curr_resources.values()):
                click.echo("Released all resources already. Unable to release more")
                return

        resource = click.prompt(
            "What resource you want to act on?",
            type=click.Choice([str(i) for i in range(client.n_resources)]),
        )
        resource = int(resource)
        client.take_action(action.upper(), resource)

    def draw(self):
        click.clear()

        print(f"{Fore.YELLOW}------------ CLIENT STATE ------------")
        self.draw_state()
        print(f"{Fore.YELLOW}--------------------------------------")

        print(f"{Fore.YELLOW}------------ CLIENT OPTIONS ------------")
        self.draw_options()
        print(f"{Fore.YELLOW}----------------------------------------")
