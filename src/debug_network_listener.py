import argparse
import asyncio
import logging
import sys
import time

from services.networking_service import NetworkingService


# --- Windows fix for ZeroMQ + asyncio ---
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

async def main(node: int):
    if node == 1:
        NetworkingService.get_instance().configure(
            port=5555,
            peer_addresses=["localhost:5556"],
        )
    else:
        NetworkingService.get_instance().configure(
            port=5556,
            peer_addresses=["localhost:5555"],
        )

    networking_service = NetworkingService.get_instance()
    networking_service.start()

    networking_service.register_handler(NetworkingService.BLOCK_SYNC_REQUEST_TOPIC, write_to_log_file)
    networking_service.register_handler(NetworkingService.BLOCK_SYNC_RESPONSE_TOPIC, write_to_log_file)
    networking_service.register_handler(NetworkingService.BLOCK_BROADCAST_TOPIC, write_to_log_file)
    networking_service.register_handler(NetworkingService.TX_POOL_REQUEST_TOPIC, write_to_log_file)
    networking_service.register_handler(NetworkingService.TX_POOL_RESPONSE_TOPIC, write_to_log_file)
    networking_service.register_handler(NetworkingService.TX_BROADCAST_TOPIC, write_to_log_file)

    print(f"Debug node {node} listening...")

    await networking_service.listen()


def write_to_log_file(payload: dict, topic: str) -> None:
    """ Write request to log file using logging. To send it manually for testing. """
    logging.debug(topic)
    logging.debug(payload)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Goodchain debug node")

    parser.add_argument(
        "--node",
        type=int,
        required=True,
        choices=[1, 2],
        help="Node number (e.g. 1 or 2)",
    )

    args = parser.parse_args()

    logging.basicConfig(filename='debug_network.log', level=logging.DEBUG)

    asyncio.run(main(args.node))