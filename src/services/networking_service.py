import asyncio
import json
from typing import Any, Callable
import zmq
import zmq.asyncio

from base.subscribable import Subscribable


class NetworkingService(Subscribable):
    # Block related topics
    BLOCK_SYNC_REQUEST_TOPIC = "blocks.sync.request"
    BLOCK_SYNC_RESPONSE_TOPIC = "blocks.sync.response"
    BLOCK_BROADCAST_TOPIC = "blocks.broadcast"

    # Transaction pool related topics
    TX_POOL_REQUEST_TOPIC = "transactions.pool.request"
    TX_POOL_RESPONSE_TOPIC = "transactions.pool.response"
    TX_BROADCAST_TOPIC = "transactions.broadcast"

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
        self._handlers: dict[str, Callable[[dict[str, Any], str], None]] = {}

    def start(self):
        self.publisher.bind(f"tcp://*:{self.port}")
        for peer_address in self.peer_addresses:
            self.subscriber.connect(f"tcp://{peer_address}")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

    def subscribe_to_topic(self, topic: str):
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)

    def register_handler(self, topic: str, callback: Callable[[dict[str, Any], str], None]) -> None:
        """Register a callback for a specific topic; payload already parsed as JSON."""
        self._handlers[topic] = callback
        self.subscribe_to_topic(topic)

    def unregister_handler(self, topic: str) -> None:
        self._handlers.pop(topic, None)

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

    def _broadcast_json(self, topic: str, payload: dict[str, Any]) -> None:
        self.broadcast(json.dumps(payload), topic=topic)

    # -------- Block sync helpers (messaging only) --------
    def request_next_block(self, after_number: int) -> None:
        self._broadcast_json(self.BLOCK_SYNC_REQUEST_TOPIC, {"after_number": after_number, "max": 1})

    def send_block_chunk(self, block_number: int, block_payload: dict[str, Any]) -> None:
        self._broadcast_json(self.BLOCK_SYNC_RESPONSE_TOPIC, {
            "block_number": block_number,
            "block_data": block_payload,
        })

    def broadcast_new_block(self, block_number: int, block_payload: dict[str, Any]) -> None:
        self._broadcast_json(self.BLOCK_BROADCAST_TOPIC, {
            "block_number": block_number,
            "block_data": block_payload,
        })

    # -------- Transaction pool helpers (messaging only) --------
    def request_pool_snapshot(self) -> None:
        self.broadcast("{}", topic=self.TX_POOL_REQUEST_TOPIC)

    def send_pool_snapshot(self, transactions: list[dict[str, Any]]) -> None:
        self._broadcast_json(self.TX_POOL_RESPONSE_TOPIC, {"transactions": transactions})

    def broadcast_new_transaction(self, transaction_payload: dict[str, Any]) -> None:
        self._broadcast_json(self.TX_BROADCAST_TOPIC, {"transaction": transaction_payload})

    async def listen(self):
        self.running = True
        while self.running:
            try:
                message = await self.subscriber.recv_string()
                topic, payload = self._split_message(message)
                self._dispatch_message(topic, payload)
                self._call_subscribers((topic, payload))
            except zmq.ZMQError:
                break
            except asyncio.CancelledError:
                break

    def _split_message(self, message: str) -> tuple[str, dict[str, Any]]:
        message = message.strip()
        if not message:
            return "", {}

        if message.startswith("{"):
            topic = ""
            payload_raw = message
        else:
            parts = message.split(" ", 1)
            if len(parts) == 2 and parts[1].lstrip().startswith("{"):
                topic, payload_raw = parts[0], parts[1].lstrip()
            elif len(parts) == 2:
                topic, payload_raw = parts[0], parts[1]
            else:
                topic, payload_raw = parts[0], "{}"

        payload = json.loads(payload_raw or "{}")
        return topic, payload

    def _dispatch_message(self, topic: str, payload: dict[str, Any]) -> None:
        handler = self._handlers.get(topic)
        if handler is not None:
            handler(payload, topic)
