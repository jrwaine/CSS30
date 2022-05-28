import time
import unittest
from threading import Thread

from fastapi.testclient import TestClient

from .app import app
from .resource_hdlr import ResourceHandler, get_resources_hdlr, setup_resources_hdlr


class TestProject3(unittest.TestCase):
    def setUp(self) -> None:
        self.n_resources = 2
        setup_resources_hdlr(self.n_resources, interactive=False)
        self.res_hdlr = get_resources_hdlr()
        self.res_hdlr.start()
        self.res_hdlr.MAX_RESOURCE_TIME_S = 15
        self.client = TestClient(app)

    def ask_resource(self, client_id: int, resource: int):
        def func():
            print("asking client", client_id, "resource", resource)
            req = self.client.get(
                f"/resource/{resource}/ask", params={"client_id": client_id}
            )
            if req.status_code != 200:
                raise BaseException(f"wrong status {(req.status_code, req.text)}")
            return req

        t = Thread(target=func, args=(), daemon=True)
        t.start()
        return t

    def release_resource(self, client_id: int, resource: int):
        print("releasing client", client_id, "resource", resource)
        req = self.client.get(
            f"/resource/{resource}/release", params={"client_id": client_id}
        )
        if req.status_code != 200:
            raise BaseException(f"wrong status {(req.status_code, req.text)}")
        return req

    def test_functional_project(self):
        # There may be some timing issues, but overall the test passes

        t = self.ask_resource(0, 0)
        time.sleep(1)
        self.assertEqual(self.res_hdlr.owner(0), 0)

        t = self.ask_resource(1, 0)
        time.sleep(1)
        self.assertIn(1, self.res_hdlr.queue_resources[0])

        req = self.release_resource(0, 0)
        time.sleep(1)
        self.assertEqual(self.res_hdlr.owner(0), 1)

        req = self.release_resource(1, 0)

        t = self.ask_resource(2, 0)
        t = self.ask_resource(2, 1)

        time.sleep(2)
        self.assertEqual(self.res_hdlr.owner(0), 2)
        self.assertEqual(self.res_hdlr.owner(1), 2)

        t = self.ask_resource(3, 0)
        t = self.ask_resource(3, 1)
        t = self.ask_resource(0, 0)
        t = self.ask_resource(0, 1)
        time.sleep(4)
        self.assertIn(3, self.res_hdlr.queue_resources[0])
        self.assertIn(3, self.res_hdlr.queue_resources[1])
        self.assertIn(0, self.res_hdlr.queue_resources[0])
        self.assertIn(0, self.res_hdlr.queue_resources[1])

        req = self.release_resource(2, 0)
        time.sleep(2)
        self.assertEqual(self.res_hdlr.owner(0), 3)
        self.assertIn(3, self.res_hdlr.queue_resources[1])
        self.assertIn(0, self.res_hdlr.queue_resources[0])
        self.assertIn(0, self.res_hdlr.queue_resources[1])

        req = self.release_resource(3, 0)
        time.sleep(1)
        self.assertNotIn(3, self.res_hdlr.queue_resources[0])
        self.assertIn(3, self.res_hdlr.queue_resources[1])
        self.assertEqual(self.res_hdlr.owner(0), 0)
        self.assertIn(0, self.res_hdlr.queue_resources[1])

        req = self.release_resource(0, 0)
        time.sleep(1)

        # Timeout resource 1 in client 2
        time.sleep(self.res_hdlr.MAX_RESOURCE_TIME_S + 2)
        self.assertEqual(self.res_hdlr.owner(1), 3)
        self.assertIn(0, self.res_hdlr.queue_resources[1])

        # Timeout resource 1 in client 3
        time.sleep(self.res_hdlr.MAX_RESOURCE_TIME_S + 2)
        self.assertEqual(self.res_hdlr.owner(1), 0)


if __name__ == "__main__":
    unittest.main()
