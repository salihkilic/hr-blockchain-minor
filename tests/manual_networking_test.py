import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from services.networking_service import NetworkingService

async def main():
    # Create two nodes
    node1 = NetworkingService(port=5555, peer_addresses=["localhost:5556"])
    node2 = NetworkingService(port=5556, peer_addresses=["localhost:5555"])

    node1.start()
    node2.start()

    # Subscribe to topics
    node1.subscribe_to_topic("BLOCKS")
    node2.subscribe_to_topic("BLOCKS")

    # Define a callback (Note: Subscribable is class-based, so this is tricky in one process)
    # But let's just see if they run and send/receive without crashing.

    received_messages = []
    def callback(msg):
        print(f"Callback received: {msg}")
        received_messages.append(msg)

    NetworkingService.subscribe(callback)

    # Run listeners in background
    t1 = asyncio.create_task(node1.listen())
    t2 = asyncio.create_task(node2.listen())

    await asyncio.sleep(1) # Wait for connection

    print("Broadcasting...")
    node1.broadcast("Requesting new blocks after block #56", topic="BLOCKS")
    await asyncio.sleep(1) # Wait for transmission
    node2.broadcast("Responding with block #57", topic="BLOCKS")
    await asyncio.sleep(1) # Wait for transmission

    node1.stop()
    node2.stop()
    t1.cancel()
    t2.cancel()

    print(f"Total messages received: {len(received_messages)}")

if __name__ == "__main__":
    asyncio.run(main())

