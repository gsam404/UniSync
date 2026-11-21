
import logging

from broker.broker_server import BrokerServer


def main():

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    broker = BrokerServer(
        host="127.0.0.1",
        port=5000,
    )

    broker.start()

    try:

        print("UniSync Broker is running.")
        print("Press Ctrl+C to stop.")

        while True:
            input()

    except KeyboardInterrupt:

        print("\nShutting down UniSync...")

    finally:
        broker.stop()


if __name__ == "__main__":
    main()
