import time
import unittest
from threading import Thread

from .client import Client, States
from .server import Server
from .signer import get_key_pair, sign_message, validate_message


class TestProject2(unittest.TestCase):
    def test_sign(self):
        pub_key, priv_key = get_key_pair()

        msg = "testing"
        signed = sign_message(msg, priv_key)
        self.assertIsInstance(signed, str)
        validate_message("testing", pub_key, signed)

    def test_functional_project(self):
        n_resources = 2
        n_clients = 4
        server = Server(n_resources, interactive=False)
        # start server
        server.start()
        time.sleep(1)
        # Lower max resource time
        server.MAX_RESOURCE_TIME_S = 10
        clients = [Client(n_resources, interactive=False) for _ in range(n_clients)]

        for c in clients:
            t = Thread(target=c.start)
            t.start()

        time.sleep(2)

        clients[0].take_action("ASK", 0)
        time.sleep(0.5)
        self.assertEqual(clients[0].curr_resources[0], States.HELD)

        clients[1].take_action("ASK", 0)
        time.sleep(0.5)
        self.assertEqual(clients[1].curr_resources[0], States.WANTED)

        clients[0].take_action("RELEASE", 0)
        time.sleep(0.5)
        self.assertEqual(clients[1].curr_resources[0], States.HELD)
        clients[1].take_action("RELEASE", 0)

        clients[2].take_action("ASK", 0)
        clients[2].take_action("ASK", 1)
        time.sleep(0.5)
        self.assertEqual(clients[2].curr_resources, {0: States.HELD, 1: States.HELD})

        clients[3].take_action("ASK", 1)
        clients[3].take_action("ASK", 0)
        clients[0].take_action("ASK", 1)
        clients[0].take_action("ASK", 0)
        time.sleep(0.5)
        self.assertEqual(
            clients[3].curr_resources, {0: States.WANTED, 1: States.WANTED}
        )
        self.assertEqual(
            clients[0].curr_resources, {0: States.WANTED, 1: States.WANTED}
        )

        clients[2].take_action("RELEASE", 0)
        time.sleep(0.5)
        self.assertEqual(clients[3].curr_resources, {0: States.HELD, 1: States.WANTED})
        self.assertEqual(
            clients[0].curr_resources, {0: States.WANTED, 1: States.WANTED}
        )

        clients[3].take_action("RELEASE", 0)
        time.sleep(0.5)
        self.assertEqual(
            clients[3].curr_resources, {0: States.RELEASED, 1: States.WANTED}
        )
        self.assertEqual(clients[0].curr_resources, {0: States.HELD, 1: States.WANTED})
        clients[0].take_action("RELEASE", 0)

        # Timeout resource 1 in client 2
        time.sleep(server.MAX_RESOURCE_TIME_S + 1)
        self.assertEqual(
            clients[3].curr_resources, {0: States.RELEASED, 1: States.HELD}
        )
        self.assertEqual(
            clients[0].curr_resources, {0: States.RELEASED, 1: States.WANTED}
        )

        # Timeout resource 1 in client 3
        time.sleep(server.MAX_RESOURCE_TIME_S + 1)
        self.assertEqual(
            clients[0].curr_resources, {0: States.RELEASED, 1: States.HELD}
        )

        for c in clients:
            del c
        del server


if __name__ == "__main__":
    unittest.main()
