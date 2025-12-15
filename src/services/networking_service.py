import asyncio
import zmq
import zmq.asyncio

from src.base.subscribable import Subscribable


class NetworkingService(Subscribable):
    def __init__(self, port: int = 5555, peer_addresses: list[str] = None):
        super().__init__()
        if peer_addresses is None:
            peer_addresses = []

        self.port = port
        self.peer_addresses = peer_addresses

        self.context = zmq.asyncio.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.subscriber = self.context.socket(zmq.SUB)
        self.running = False

    def start(self):
        self.publisher.bind(f"tcp://*:{self.port}")
        for peer_address in self.peer_addresses:
            self.subscriber.connect(f"tcp://{peer_address}")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

    def subscribe_to_topic(self, topic: str):
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)

    def stop(self):
        self.running = False
        self.publisher.close()
        self.subscriber.close()
        self.context.term()

    def broadcast(self, message: str, topic: str = ""):
        if topic:
            self.publisher.send_string(f"{topic} {message}")
        else:
            self.publisher.send_string(message)

    async def listen(self):
        self.running = True
        while self.running:
            try:
                message = await self.subscriber.recv_string()
                self._call_subscribers(message)
            except zmq.ZMQError:
                break
            except asyncio.CancelledError:
                break
