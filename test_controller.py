from network.controller import Controller
from network.common.network import Network


def main():
    network = Network()
    controller = Controller(
        "localhost",
        8888,
        network
    )
    controller.start()


if __name__ == "__main__":
    main()
