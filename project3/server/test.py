import time
import unittest
from threading import Thread

from ._client import Client, States
from .server import Server


class TestProject3(unittest.TestCase):
    def test_functional_project(self):
        n_resources = 2
        n_clients = 4
        server = Server(n_resources, interactive=False)
        # start server
        server.start()
        time.sleep(1)
        # Lower max resource time
        server.MAX_RESOURCE_TIME_S = 10
        


if __name__ == "__main__":
    unittest.main()
