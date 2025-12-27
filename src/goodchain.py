import argparse
import logging

def parse_args():
    parser = argparse.ArgumentParser(description="Goodchain node")

    parser.add_argument(
        "--node",
        type=int,
        required=True,
        help="Node number configures data directory and networking",
        choices=[1, 2],
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    logging.basicConfig(
        filename=f"goodchain_node_{args.node}.log",
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    from services import InitializationService, NodeFileSystemService

    logging.info(f"Starting Goodchain node {args.node}...")

    NodeFileSystemService.set_node_data_directory_by_number(args.node)
    InitializationService.initialize_application(args.node)

    from ui import GoodchainApp
    app = GoodchainApp()
    app.run()