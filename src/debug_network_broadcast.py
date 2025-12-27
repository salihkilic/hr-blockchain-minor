# broadcast_test.py
import sys
import json
import time
import argparse
import asyncio

from services.networking_service import NetworkingService


# --- Windows fix for ZeroMQ + asyncio ---
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )


def main(node: int):
    if node == 1:
        networking_service = NetworkingService(
            port=5555,
            peer_addresses=["localhost:5556"],
        )
    else:
        networking_service = NetworkingService(
            port=5556,
            peer_addresses=["localhost:5555"],
        )

    networking_service.start()

    payload = {
        "message": f"Hello from node {node}!",
        "timestamp": time.time(),
    }
    topic = "test.topic"

    print(f"Broadcasting from node {node}")
    print(f"Topic   : {topic}")
    print(f"Payload : {json.dumps(payload)}")

    # Give SUB sockets a moment to connect (important for PUB/SUB)
    time.sleep(0.5)

    networking_service.broadcast(
        json.dumps(payload),
        topic=topic,
    )

    print("Broadcast sent.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Goodchain broadcast test")

    parser.add_argument(
        "--node",
        type=int,
        required=True,
        choices=[1, 2],
        help="Node number (1 or 2)",
    )

    args = parser.parse_args()

    main(args.node)
