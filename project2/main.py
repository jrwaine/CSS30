import argparse
import time
from dataclasses import dataclass
from typing import Literal

from .client import Client
from .server import Server


@dataclass
class ArgsCLI:
    proc_type: Literal["server", "client"]
    n_resources: int


def parse_args(*args) -> ArgsCLI:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--proc-type",
        help="Process type",
        required=True,
        type=str,
        choices=["server", "client"],
    )
    ap.add_argument(
        "--n-resources", help="Number of resources", required=True, type=int
    )
    parsed = ap.parse_args(args)
    return ArgsCLI(proc_type=parsed.proc_type, n_resources=parsed.n_resources)


def main(*args):
    cli_args = parse_args(*args)

    if cli_args.proc_type == "server":
        serv = Server(cli_args.n_resources)
        serv()
    elif cli_args.proc_type == "client":
        client = Client(cli_args.n_resources)
        client()

    while True:
        time.sleep(0.5)
