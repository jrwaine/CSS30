import click
import colorama
from colorama import Back, Fore

from .service import Service, States

colorama.init(autoreset=True)


class ServiceUI:
    def __init__(self, service: Service) -> None:
        self.service = service

    def draw_state(self):
        serv = self.service
        print(f"{Fore.YELLOW}Currently the program state is: {serv.state.name}")

    def draw_options(self):
        serv = self.service
        if serv.state == States.HELD:

            @click.prompt
            @click.confirm("Release token?")
            def prompt(release: bool):
                if release:
                    click.echo(f"{Fore.BLUE}Releasing token...")
                    serv.release_token()
                    click.echo(f"{Fore.GREEN}Released token!")

            prompt()
        elif serv.state == States.WANTED:
            print(f"{Fore.BLUE}Waiting for token...")
        elif serv.state == States.RELEASED:

            @click.prompt
            @click.confirm("Ask token?")
            def prompt(ask: bool):
                if ask:
                    click.echo(f"{Fore.BLUE}Asking for token...")
                    serv.ask_token()
                    click.echo(f"{Fore.GREEN}Asked for token!")

            prompt()

    def draw(self):
        click.clear()

        print(f"{Fore.YELLOW}------------ STATE ------------")
        self.draw_state()
        print(f"{Fore.YELLOW}-------------------------------")
        print()
        print(f"{Fore.YELLOW}----------- OPTIONS -----------")
        self.draw_options()
        print(f"{Fore.YELLOW}-------------------------------")
