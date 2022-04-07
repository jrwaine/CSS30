import argparse
import sys
from dataclasses import dataclass

from .service import Service
from .ui import ServiceUI


@dataclass
class ArgsCLI:
    id_process: int
    n_processes: int


def parse_args(*args):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pid", help="Process ID", required=True, type=int)
    ap.add_argument("--n-procs", help="Number of processes", required=True, type=int)
    parsed = ap.parse_args(args)
    return ArgsCLI(id_process=parsed.pid, n_processes=parsed.n_procs)


def main(*args):
    args_cli = parse_args(*args)
    service = Service(process_id=args_cli.id_process, n_procs=args_cli.n_processes)
    service_ui = ServiceUI(service)

    service.set_callback_state_change(service_ui.draw)
    service_ui.draw()

    print("created")
