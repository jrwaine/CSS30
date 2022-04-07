import time

import click
import colorama
from colorama import Back, Fore

from .service import Service, States

colorama.init(autoreset=True)


class ServiceUI:
    def __init__(self, service: Service) -> None:
        self.service = service
        self.state_changed = True
        self.__state_changed = True

    def draw_state(self):
        serv = self.service
        print(f"{Fore.YELLOW}Currently the program state is: {serv.state.name}")

    def set_state_changed(self):
        self.__state_changed = True

    def draw_options(self):
        serv = self.service
        if serv.state == States.HELD:

            def prompt():
                if click.confirm("Release token?"):
                    click.echo(f"{Fore.BLUE}Releasing token...")
                    serv.release_token()
                    click.echo(f"{Fore.GREEN}Released token!")

            prompt()
        elif serv.state == States.WANTED:
            print(f"{Fore.BLUE}Waiting for token...")
        elif serv.state == States.RELEASED:

            def prompt():
                if click.confirm("Ask token?"):
                    click.echo(f"{Fore.BLUE}Asking for token...")
                    serv.ask_token()
                    click.echo(f"{Fore.GREEN}Asked for token!")

            prompt()
        # time.sleep(0.1)

    def draw(self):
        if not self.__state_changed:
            return

        click.clear()
        print(f"{Fore.YELLOW}------------ STATE ------------")
        self.draw_state()
        print(f"{Fore.YELLOW}-------------------------------")
        print()
        print(f"{Fore.YELLOW}----------- OPTIONS -----------")
        self.draw_options()
        print(f"{Fore.YELLOW}-------------------------------")
