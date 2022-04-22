import enum
import time
from typing import Any, Dict, List, Literal, Optional

import click
import colorama
from colorama import Back, Fore


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

    def serve(self):
        ...

    def take_action(self, action: Literal["ASK", "RELEASE"], resource: int):
        resource_state = self.curr_resources[resource]

        if action.upper() == "ASK" and resource_state in (States.HELD, States.WANTED):
            click.echo(f"Already holding resource {resource}")
            return
        elif action.upper() == "RELEASE" and resource_state == States.RELEASED:
            click.echo(f"Already released resource {resource}")
            return

    def release_token(self, resource: int):
        ...

    def ask_token(self, resource: int):
        ...

    def route_receive_token(self, resource: int):
        ...


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
