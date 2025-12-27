import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Goodchain node")

    parser.add_argument(
        "--node",
        type=int,
        required=True,
        help="Node number (e.g. 1, 2, 3)"
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    from services import InitializationService, NodeFileSystemService

    NodeFileSystemService.set_node_data_directory_by_number(args.node)
    InitializationService.initialize_application()

    from ui import GoodchainApp
    app = GoodchainApp()
    app.run()