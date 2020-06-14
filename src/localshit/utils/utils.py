import logging
import struct
from socket import (
    socket,
    AF_INET,
    SOCK_DGRAM,
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
    gethostbyname
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
