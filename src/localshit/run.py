"""
Main class for starting a server instance.

"""
import socket

class LocalsHitManager:
    def __init__(self):
        self.print_welcome()

    def print_welcome(self):
        print("manager started!")
    



if __name__ == "__main__":
    try:
        print("starting manager...")
        app = LocalsHitManager()
    except Exception as e:
        print("Error while starting app: %s" % e)