import logicsponge.core as ls
import numpy as np
import zmq
from logicsponge.core import dashboard, stats


class Car(ls.FunctionTerm):
    def __init__(self, *args, port=5555, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://localhost:{port}")

    def enter(self):
        self.socket.send_json({"command": "reset"})
        # Receive initial observation
        response = self.socket.recv_json()

        if not isinstance(response, dict):
            msg = "Expected response to be a dictionary"
            raise TypeError(msg)

        observation = np.array(response["observation"])
        self.output(
            ls.DataItem(
                {
                    "observation": observation,
                    "reward": 0.0,
                    "done": False,
                    "truncated": False,
                }
            )
        )

    def f(self, item: ls.DataItem) -> ls.DataItem:
        action = item["action"]
        self.socket.send_json({"command": "step", "action": action})

        # Receive new observation from server
        response = self.socket.recv_json()

        if not isinstance(response, dict):
            msg = "Expected response to be a dictionary"
            raise TypeError(msg)

        observation = np.array(response["observation"])
        reward = response["reward"]
        done = response["done"]
        truncated = response["truncated"]

        # Output the new state (i.e., send it to policy)
        return ls.DataItem(
            {
                "observation": observation,
                "reward": reward,
                "done": done,
                "truncated": truncated,
            }
        )


class Policy(ls.FunctionTerm):
    def f(self, item: ls.DataItem) -> ls.DataItem:
        """Plug-in your own controller policy (e.g., a DQN)"""
        _ = item
        return ls.DataItem({"action": 3})


car = Car()
policy = Policy()
total_reward = (
    stats.Sum(key="reward") * ls.AddIndex(key="index") * dashboard.Plot("cumulated reward", x="index", y=["sum"])
)

circuit = car * (policy * car | total_reward)
# equivalently :
# circuit = car * policy * car * total_reward
circuit.start()
dashboard.show_stats(circuit)
dashboard.run()
