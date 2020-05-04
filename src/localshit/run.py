"""
Main class for starting a server instance.

"""
import socket
import os
import sys
import logging
import time
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
from service_discovery import ServiceDiscovery
from service_announcement import ServiceAnnouncement




class LocalsHitManager:
    def __init__(self):
        self.print_welcome()
        self.running = True
        discovery_thread = ServiceDiscovery(10001)


        try:
            discovery_thread.start()
            print("discovery_thread started")


            while self.running:
                if not discovery_thread.is_alive():
                    print("process died")
                    self.running = False
                    break

                time.sleep(0.2)

        except KeyboardInterrupt:
            print("Process terminated by user")
        except Exception as e:
            print(e)
        finally:
            print("stop discovery_thread...")
            discovery_thread.stop()
            discovery_thread.join()
        # announcement_thread_1 = ServiceAnnouncement(10001)
        # announcement_thread_1.start()

    def print_welcome(self):
        print("manager started!")


if __name__ == "__main__":
    try:
        print("starting manager...")
        app = LocalsHitManager()
    except Exception as e:
        print("Error while starting app: %s" % e)
