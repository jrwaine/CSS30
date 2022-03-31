import enum
import time
from typing import List

from .connection import Connection
from .requests import TokenRequest, TokenRequestAnswer, load_json


class States(enum.Enum):
    HELD = 1
    WANTED = 2
    RELEASED = 3


class Service:
    all_ports = [5000, 5001, 5002]
    token_val = "esse token eh assim"

    def __init__(self, process_id: int) -> None:
        self.port = self.all_ports[process_id]
        self.queue_requests: List[TokenRequest] = []
        self.state: States = States.RELEASED

        self.t_multicast = Connection.listen_multicast(...)
        self.t_unicast = Connection.listen_unicast(...)
        self.n_answers = 0
        self.last_request = None

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

            if self.n_answers == (len(self.all_ports) - 1):
                self.exchange_token()
                self.use_token()
        elif self.state == States.HELD:
            if data_type == TokenRequest.__name__:
                token_request = TokenRequest(**data)
                self.last_request = token_request
                self.queue_requests.append(token_request)
        elif self.state == States.RELEASED:
            if data_type == TokenRequest.__name__:
                req = TokenRequest(**data)
                Connection.publish_multicast(req)

    def exchange_token(self):
        ...

    def use_token(self):
        self.state = States.HELD
        time.sleep(1)
        self.answer_all_token_requests()
        self.last_request = None
        self.n_answers = 0
        self.state = States.RELEASED

    def ask_token(self):
        self.state = States.WANTED
        token_req = TokenRequest(port=self.port, total_time=time.time())
        Connection.publish_multicast(token_req.to_json())

    def answer_all_token_requests(self):
        for msg_req in self.queue_requests:
            self.answer_token_request(msg_req)
        self.queue_requests = []

    def answer_token_request(self, msg_req: TokenRequest):
        answer = TokenRequestAnswer(port=self.port, port_to=msg_req.port)
        Connection.publish_multicast(answer.to_json())

    def ask_public_key(self, peer_port: str):
        ...
