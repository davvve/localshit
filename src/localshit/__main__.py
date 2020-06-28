import logging
import traceback
import argparse
from localshit.run import LocalsHitManager


def main():
    proxy = "192.168.0.179"
    parser = argparse.ArgumentParser(prog="my_megazord_program")
    parser.add_argument(
        "-p", nargs="?", help='start with localshit -p "172.17.0.2" to add proxy'
    )
    args = parser.parse_args()
    if args.p:
        proxy = args.p

    logging.info("Proxy is set to %s" % proxy)

    try:
        logging.info("starting manager...")
        app = LocalsHitManager(proxy=proxy)
    except Exception as e:
        logging.error("Error while starting app: %s" % e)
        traceback.print_exc()
