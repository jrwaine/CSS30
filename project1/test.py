import time
import unittest

from .service import Service, States


class TestProject1(unittest.TestCase):
    def test_functional_project(self):
        servs = [Service(i, 3) for i in range(3)]

        servs[0].ask_token()
        time.sleep(0.1)
        self.assertEqual(
            [servs[i].state for i in range(3)],
            [States.HELD, States.RELEASED, States.RELEASED],
        )
        servs[1].ask_token()
        time.sleep(0.1)
        self.assertEqual(
            [servs[i].state for i in range(3)],
            [States.HELD, States.WANTED, States.RELEASED],
        )

        servs[0].release_token()
        time.sleep(0.1)
        self.assertEqual(
            [servs[i].state for i in range(3)],
            [States.RELEASED, States.HELD, States.RELEASED],
        )

        servs[2].ask_token()
        time.sleep(0.1)
        self.assertEqual(
            [servs[i].state for i in range(3)],
            [States.RELEASED, States.HELD, States.WANTED],
        )
        servs[0].ask_token()
        time.sleep(0.1)
        self.assertEqual(
            [servs[i].state for i in range(3)],
            [States.WANTED, States.HELD, States.WANTED],
        )

        # 2 gets first
        servs[1].release_token()
        time.sleep(0.1)
        self.assertEqual(
            [servs[i].state for i in range(3)],
            [States.WANTED, States.RELEASED, States.HELD],
        )


if __name__ == "__main__":
    unittest.main()
