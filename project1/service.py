import enum
import time
from typing import Callable, List

from .connection import Connection
from .requests import TokenRequest, TokenRequestAnswer, load_json


class States(enum.Enum):
    HELD = 1
    WANTED = 2
    RELEASED = 3


class Service:
    BASE_PORT = 5000

    def __init__(self, process_id: int, n_procs: int) -> None:
        self.port = self.BASE_PORT + process_id
        self.n_procs = n_procs
        self.queue_requests: List[TokenRequest] = []
        self.state: States = States.RELEASED

        self.t_multicast = Connection.listen_multicast(
            5000 + self.port, self.callback_multicast
        )
        self.t_unicast = Connection.listen_unicast(self.port, self.callback_unicast)
        self.n_answers = 0
        self.last_request = None
        self.callback_state_change: Callable[[], None] = lambda: ...

    def set_callback_state_change(self, f: Callable[[], None]):
        self.callback_state_change = f

    def callback_multicast(self, b: bytes):
        msg = b.decode("utf-8")
        self.state_machine_msg(msg)

    def callback_unicast(self, b: bytes):
        msg = b.decode("utf-8")
        self.state_machine_msg(msg)

    def state_machine_msg(self, msg: str):
        req = load_json(msg)
        data, data_type = req["data"], req["data_type"]
        # Message from itself
        if data["port"] == self.port:
            return
        if self.state == States.WANTED:
            if data_type == TokenRequest.__name__:
                req = TokenRequest(**data)
                if (req.total_time, req.port) < (
                    self.last_request.total_time,
                    self.port,
                ):
                    self.answer_token_request(req)
                else:
                    self.queue_requests.append(req)
            elif data_type == TokenRequestAnswer.__name__:
                answer = TokenRequestAnswer(**data)
                if answer.port_to == self.port:
                    self.n_answers += 1

            if self.n_answers == (self.n_procs - 1):
                self.state = States.HELD
                self.callback_state_change()
        elif self.state == States.HELD:
            if data_type == TokenRequest.__name__:
                token_request = TokenRequest(**data)
                self.last_request = token_request
                self.queue_requests.append(token_request)
        elif self.state == States.RELEASED:
            if data_type == TokenRequest.__name__:
                req = TokenRequest(**data)
                self.answer_token_request(req)

    def release_token(self):
        if not self.state == States.HELD:
            raise Exception(f"I cannot release, my state is {self.state.name}")
        self.answer_all_token_requests()
        self.last_request = None
        self.n_answers = 0
        self.state = States.RELEASED
        self.callback_state_change()

    def ask_token(self):
        self.state = States.WANTED
        token_req = TokenRequest(port=self.port, total_time=time.time())
        self.last_request = token_req
        Connection.publish_multicast(token_req.to_json())
        self.callback_state_change()

    def answer_all_token_requests(self):
        for msg_req in self.queue_requests:
            self.answer_token_request(msg_req)
        self.queue_requests = []

    def answer_token_request(self, msg_req: TokenRequest):
        answer = TokenRequestAnswer(port=self.port, port_to=msg_req.port)
        Connection.send_unicast(answer.to_json(), msg_req.port)
