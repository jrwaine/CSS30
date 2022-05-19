import argparse
import time
from dataclasses import dataclass
from typing import Literal

from ._client import Client
from .server import Server


@dataclass
class ArgsCLI:
    n_resources: int


def parse_args(*args) -> ArgsCLI:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--n-resources", help="Number of resources", required=True, type=int
    )
    parsed = ap.parse_args(args)
    return ArgsCLI(proc_type=parsed.proc_type, n_resources=parsed.n_resources)


def main(*args):
    cli_args = parse_args(*args)

    serv = Server(cli_args.n_resources)
    serv.start()

    while True:
        time.sleep(0.5)
