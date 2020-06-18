import logging
import struct
from enum import Enum
from socket import (
    socket,
    AF_INET,
    SOCK_DGRAM,
    SOCK_STREAM,
    SOL_SOCKET,
    SO_REUSEADDR,
    IPPROTO_UDP,
    IP_MULTICAST_TTL,
    IP_MULTICAST_LOOP,
    IP_ADD_MEMBERSHIP,
    IPPROTO_IP,
    INADDR_ANY,
    inet_aton,
    gethostname,
    gethostbyname,
)

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


def get_host_address():
    hostname = gethostname()
    return gethostbyname(hostname)


def get_multicast_socket():
    socket_mcast = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    try:
        socket_mcast.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    except AttributeError:
        pass
    socket_mcast.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 32)
    socket_mcast.setsockopt(IPPROTO_IP, IP_MULTICAST_LOOP, 1)

    return socket_mcast


def bind_multicast(socket_mcast, MCAST_GRP="224.1.1.1", MCAST_PORT=5007):
    socket_mcast.bind((MCAST_GRP, MCAST_PORT))
    mreq = struct.pack("4sl", inet_aton(MCAST_GRP), INADDR_ANY)
    socket_mcast.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)


def get_unicast_socket():
    socket_ucast = socket(AF_INET, SOCK_DGRAM)
    return socket_ucast


def get_tcp_socket():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    return server_socket


def send_unicast(message, recipient):
    socket_unicast = get_unicast_socket()

    socket_unicast.sendto(message.encode(), recipient, 10001)
    # TODO: make unicast reliable / with ack msg
    """
    socket_unicast.settimeout(1.0)
    try:
        data, server = socket_unicast.recvfrom(1024)
        # Print the ACK the server sent
    except socket.timeout:
        print('Timed out')
    """


def compare_adresses(first_address, second_address):
    """
    comapares which address is the higher identifier and returns True if first is higher, otherwise false
    """
    first = inet_aton(first_address)
    second = inet_aton(second_address)

    if first == second:
        logging.error("First address is same as second")
        return CompareResult.SAME
    elif first > second:
        return CompareResult.LARGER
    else:
        return CompareResult.LOWER


class CompareResult(Enum):
    LARGER = 1
    LOWER = 2
    SAME = 3
