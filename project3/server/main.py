import argparse
from dataclasses import dataclass

import uvicorn

from .app import app
from .resource_hdlr import setup_resources_hdlr


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

    setup_resources_hdlr(cli_args.n_resources, interactive=True)

    uvicorn.run(app, host="0.0.0.0", port=8000)
