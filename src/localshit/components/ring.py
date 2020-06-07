import socket
import logging

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)



class Ring:
    members = []
    sorted_ring = []

    def __init__(self):
        logging.info("Ring initialized")

    def _form_ring(self, members):
        sorted_binary_ring = sorted([socket.inet_aton(member) for member in members])
        sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring]
        return sorted_ip_ring

    def add_host(self, host, own_ip):


        if host not in self.members:
            self.members.append(host)
            self.sorted_ring = self._form_ring(self.members)
            logging.info("Discovered hosts: %s" % self.members)
            left_member = self.get_neighbour(own_ip)
            logging.info("Own IP: %s | left Neighbour: %s" % (own_ip, left_member))

            right_member = self.get_neighbour(own_ip, direction='right')
            logging.info("Own IP: %s | right Neighbour: %s" % (own_ip, right_member))
        else:
            logging.info("Host %s was already discovered" % host)

    def get_hosts(self):
        return self.members


    def get_neighbour(self, current_member_ip, direction='left'):
        current_member_index = self.sorted_ring.index(current_member_ip) if current_member_ip in self.sorted_ring else -1
        if current_member_index != -1:
            if direction == 'left':
                if current_member_index + 1 == len(self.sorted_ring):
                    return self.sorted_ring[0]
                else:
                    return self.sorted_ring[current_member_index + 1]
            else:
                # TODO: rechts rum funktioniert hier nicht
                if current_member_index - 1 == 0:
                    return self.sorted_ring[len(self.sorted_ring) - 1]
                else:
                    return self.sorted_ring[current_member_index - 1]
        else:
            return None
