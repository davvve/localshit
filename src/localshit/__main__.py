import logging
import traceback
from localshit.run import LocalsHitManager

def main():
    try:
        logging.info("starting manager...")
        app = LocalsHitManager()
    except Exception as e:
        logging.error("Error while starting app: %s" % e)
        traceback.print_exc()
