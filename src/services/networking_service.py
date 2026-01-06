import asyncio
import json
import logging
from typing import Any, Callable
import zmq
import zmq.asyncio

from base import AbstractSingleton
from base.subscribable import Subscribable


class NetworkingService(Subscribable, AbstractSingleton):
    # Block related topics
    BLOCK_SYNC_REQUEST_TOPIC = "blocks.sync.request"
    BLOCK_SYNC_RESPONSE_TOPIC = "blocks.sync.response"
    BLOCK_BROADCAST_TOPIC = "blocks.broadcast"

    # Block validation related topics
    VALIDATION_BROADCAST_TOPIC = "validations.broadcast"

    # Transaction pool related topics
    TX_POOL_REQUEST_TOPIC = "transactions.pool.request"
    TX_POOL_RESPONSE_TOPIC = "transactions.pool.response"
    TX_BROADCAST_TOPIC = "transactions.broadcast"

    def __init__(self):
        super().__init__()
        self.port = None
        self.peer_addresses = []

        self.context = zmq.asyncio.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.subscriber = self.context.socket(zmq.SUB)
        self.running = False
        self._handlers: dict[str, Callable[[dict[str, Any], str], None]] = {}
        logging.debug("NetworkingService initialized")

    def configure(self, port: int, peer_addresses: list[str]) -> None:
        if self.port is not None or self.peer_addresses:
            raise Exception("NetworkingService is already configured.")
        logging.debug(f"Configuring NetworkingService on port {port} with peers {peer_addresses}")
        self.port = port
        self.peer_addresses = peer_addresses

    def start(self):
        self.publisher.bind(f"tcp://*:{self.port}")
        logging.debug(f"Publisher bound to tcp://*:{self.port}")
        for peer_address in self.peer_addresses:
            self.subscriber.connect(f"tcp://{peer_address}")
            logging.debug(f"Subscriber connected to tcp://{peer_address}")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        logging.debug("Subscriber subscribed to all topics (empty string)")

    def subscribe_to_topic(self, topic: str):
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)
        logging.debug(f"Subscribing to topic: '{topic}'")

    def register_handler(self, topic: str, callback: Callable[[dict[str, Any], str], None]) -> None:
        """Register a callback for a specific topic; payload already parsed as JSON."""
        self._handlers[topic] = callback
        self.subscribe_to_topic(topic)
        logging.debug(f"Registered handler for topic '{topic}': {callback}")

    def unregister_handler(self, topic: str) -> None:
        self._handlers.pop(topic, None)
        logging.debug(f"Unregistered handler for topic '{topic}'")

    def stop(self):
        self.running = False
        logging.debug("Stopping NetworkingService: closing sockets and terminating context")
        self.publisher.close()
        self.subscriber.close()
        self.context.term()
        logging.debug("NetworkingService stopped")

    def broadcast(self, message: str, topic: str = ""):
        # Truncate long messages in logs to keep output readable
        logging.debug(f"Broadcasting on topic '{topic}': {message}")
        if topic:
            self.publisher.send_string(f"{topic} {message}")
        else:
            self.publisher.send_string(message)

    def _broadcast_json(self, topic: str, payload: dict[str, Any]) -> None:
        logging.debug("Broadcasting JSON payload on topic '%s': %s", topic, json.dumps(payload))
        self.broadcast(json.dumps(payload), topic=topic)

    # -------- Block sync helpers (messaging only) --------
    def request_next_block(self, after_number: int) -> None:
        logging.debug(f"Requesting next block after {after_number}")
        self._broadcast_json(self.BLOCK_SYNC_REQUEST_TOPIC, {"after_number": after_number, "max": 1})

    def send_block_chunk(self, block_number: int, block_payload: dict[str, Any]) -> None:
        logging.debug(f"Sending block chunk for block_number={block_number}")
        self._broadcast_json(self.BLOCK_SYNC_RESPONSE_TOPIC, {
            "block_number": block_number,
            "block_data": block_payload,
        })

    def broadcast_new_block(self, block_number: int, block_payload: dict[str, Any]) -> None:
        logging.debug(f"Broadcasting new block {block_number}")
        self._broadcast_json(self.BLOCK_BROADCAST_TOPIC, {
            "block_number": block_number,
            "block_data": block_payload,
        })

    def broadcast_new_validation(self, validation_payload: dict[str, Any], block_hash: str) -> None:
        logging.debug("Broadcasting new validation")
        self._broadcast_json(self.VALIDATION_BROADCAST_TOPIC, {
            "validation_data": validation_payload,
            "block_hash": block_hash,
        })

    # -------- Transaction pool helpers (messaging only) --------
    def request_pool_snapshot(self) -> None:
        logging.debug("Requesting transaction pool snapshot")
        self.broadcast("{}", topic=self.TX_POOL_REQUEST_TOPIC)

    def send_pool_snapshot(self, transactions: list[dict[str, Any]]) -> None:
        logging.debug(f"Sending pool snapshot with {len(transactions)} transactions")
        self._broadcast_json(self.TX_POOL_RESPONSE_TOPIC, {"transactions": transactions})

    def broadcast_new_transaction(self, transaction_payload: dict[str, Any]) -> None:
        logging.debug("Broadcasting new transaction")
        self._broadcast_json(self.TX_BROADCAST_TOPIC, {"transaction": transaction_payload})

    async def listen(self):
        logging.debug("Starting NetworkingService listen loop")
        self.running = True
        while self.running:
            try:
                message = await self.subscriber.recv_string()
                logging.debug(f"Received raw message: {message}")
                topic, payload = self._split_message(message)
                logging.debug(f"Parsed message. topic='{topic}', payload_keys={list(payload.keys())}")
                self._dispatch_message(topic, payload)
                # notify any subscribable subscribers
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
        logging.debug(f"_split_message result -> topic: '{topic}', payload size: {len(payload) if isinstance(payload, dict) else 'N/A'}")
        return topic, payload

    def _dispatch_message(self, topic: str, payload: dict[str, Any]) -> None:
        handler = self._handlers.get(topic)
        if handler is not None:
            logging.debug(f"Dispatching to handler for topic '{topic}'")
            try:
                handler(payload, topic)
            except Exception:
                logging.exception(f"Exception while handling message for topic '{topic}'")
        else:
            logging.debug(f"No handler registered for topic '{topic}'")
