from collections.abc import Iterator

import logicsponge.core as ls
import zmq
from logicsponge.core import dashboard


class ZeroMQSource(ls.SourceTerm):
    port: int
    socket_type: int

    def __init__(self, *args, port: int = 5555, socket_type: int = zmq.PULL, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        print(f"Initializing ZeroMQ with port {port}")
        self.context = zmq.Context()
        self.socket = self.context.socket(socket_type)
        self.socket.bind(f"tcp://localhost:{port}")

    def receive(self) -> ls.DataItem:
        # Wait for the next message
        message = self.socket.recv_json()

        if not isinstance(message, dict):
            msg = f"Expected message to be a dictionary, got {type(message).__name__} instead"
            raise TypeError(msg)

        return ls.DataItem(message)

    def generate(self) -> Iterator[ls.DataItem]:
        while True:
            message = self.receive()
            yield message


# the circuit
source = ZeroMQSource(socket_type=zmq.PULL)
circuit = (
    source
    * ls.Print()
    * (dashboard.Plot("Loss", x="epoch", y=["loss"]) | dashboard.Plot("Accuracy", x="epoch", y=["accuracy"]))
)

# dashboard
dashboard.show_stats(circuit)
dashboard.run()

# start
circuit.start()
