import logging
import traceback
import argparse
from localshit.run import LocalsHitManager


def main():
    frontend = "192.168.0.179"
    parser = argparse.ArgumentParser(prog="my_megazord_program")
    parser.add_argument(
        "-f", nargs="?", help='start with localshit -f "172.17.0.2" to add frontend'
    )
    args = parser.parse_args()
    if args.f:
        frontend = args.f

    logging.info("Frontend server is set to %s" % frontend)

    try:
        logging.info("starting manager...")
        _ = LocalsHitManager(frontend=frontend)
    except Exception as e:
        logging.error("Error while starting app: %s" % e)
        traceback.print_exc()
