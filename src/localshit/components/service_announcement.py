"""
Service Announcement

Adapted from https://stackoverflow.com/questions/21089268/python-service-discovery-advertise-a-service-across-a-local-network
"""

from time import sleep
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname
import uuid


class ServiceAnnouncement():
    def __init__(self, port):
        s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
        s.bind(('', 0))
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) #this is a broadcast socket
        server_id = str(uuid.uuid4())

        while True:
            data = server_id
            s.sendto(data.encode(), ('<broadcast>', port))
            print("sent service announcement")
            sleep(5)



if __name__ == "__main__":
    print("service announcement...")
    app = ServiceAnnouncement(5000)