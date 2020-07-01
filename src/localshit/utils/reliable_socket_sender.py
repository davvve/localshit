"""
Class for handle reliable multicast and unicast.

Inspired by https://github.com/daeyun/reliable-multicast-chat
"""
from queue import PriorityQueue
import socket
import struct
import threading
import time
import logging
import json

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class ReliableSocketWorker:
    def __init__(self, running, hosts, port=10033):
        self.port = port
        self.hosts = hosts
        self.running = running

        self.my_id = self.hosts.current_member_ip
        self.message_max_size = 4096
        self.message_id_counter = 0
        self.threads = []

        self.has_received = {}
        self.has_acknowledged = {}  # saves acknowledged messages
        self.unack_messages = []  # messages with pending acknowledgement
        self.holdback_queue = []

        self.holdback_queue_markers = []
        self.holdback_sequence_counter = 0
        self.sequence_counter = 0
        self.SEQUENCER_ID = 0

        self.queue = PriorityQueue()
        self.mutex = threading.Lock()
        size = len(self.hosts.members)
        self.my_timestamp = {"192.168.0.10": 0}  # [self.ip2int("192.168.0.10")] # size

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.bind(("", port))
        self.sock.settimeout(0.01)

    def unicast_send(
        self,
        destination,
        message,
        msg_id=None,
        is_ack=False,
        is_order_marker=False,
        timestamp=None,
    ):
        """ Push an outgoing message to the message queue. """
        if timestamp is None:
            timestamp = self.my_timestamp

        is_msg_id_specified = msg_id is not None
        if msg_id is None:
            msg_id = self.message_id_counter

        # pack message with utils, make vector timestamp
        message = self.pack_message(
            [
                self.my_id,
                msg_id,
                is_ack,
                is_order_marker,
                json.dumps(timestamp),
                message,
            ]
        )

        # append every new message excluding ack msg or without id to unack_messages. they will be removed as soon as message was acknowledged
        if not is_ack and not is_msg_id_specified:
            with self.mutex:
                self.unack_messages.append((destination, message))

        dest_ip = destination
        dest_port = self.port
        send_time = time.time()
        # put to queue, which sends the messages out
        self.queue.put((send_time, message, dest_ip, dest_port))

    def unicast_receive(self):
        """ Receive UDP messages from other chat processes and store them in the holdback queue.
            Returns True if new message was received. """

        data, _ = self.sock.recvfrom(self.message_max_size)
        [
            sender,
            message_id,
            is_ack,
            is_order_marker,
            message_timestamp,
            message,
        ] = self.unpack_message(data)

        # check if ack message type
        if is_ack:
            # save that ack was send
            self.has_acknowledged[(sender, message_id)] = True
        else:
            # if normal message, send acknowledgement to the sender
            self.unicast_send(sender, "", message_id, True)
            # check if message was send more than once
            if (sender, message_id) not in self.has_received:
                self.has_received[(sender, message_id)] = True
                self.holdback_queue.append((sender, message_timestamp, message))
                self.update_holdback_queue_casual()
                return True
        return False

    def update_holdback_queue_casual(self):
        """ Compare message timestamps to ensure casual ordering. """
        while True:
            new_holdback_queue = []
            removed_messages = []
            # check with vector timestamp, if ordering is correct or some messages are missing
            for sender, v, message in self.holdback_queue:
                should_remove = True
                for i in range(len(v)):
                    if i == sender:
                        if list(v)[i] != list(self.my_timestamp)[i] + 1:
                            should_remove = False
                    else:
                        if list(v)[i] > list(self.my_timestamp)[i]:
                            should_remove = False
                if not should_remove:
                    new_holdback_queue.append((sender, v, message))
                else:
                    removed_messages.append((sender, v, message))

            # deliver the messages which are removed from holdback queue in this update cycle
            for sender, v, message in removed_messages:
                self.my_timestamp[sender] += 1  # update own vector_clock timestamp
                self.deliver(sender, message)

            self.holdback_queue = new_holdback_queue

            if not removed_messages:
                break

    def multicast(self, message, is_order_marker=False):
        """ Unicast the message to all known clients. """
        # immitate multicast as for loop with unicasts. only on this way we get reliable multicast
        for destination in self.hosts.members:
            self.unicast_send(destination, message, is_order_marker=is_order_marker)
        self.message_id_counter += 1

    def pack_message(self, message_list):
        return (",".join([str(x) for x in message_list])).encode("utf-8")

    def unpack_message(self, message):
        message = message.decode("utf-8")
        (
            sender,
            message_id,
            is_ack,
            is_order_marker,
            vector_str,
            message,
        ) = message.split(",", 5)

        # sender = self.ip2int(sender)
        message_id = int(message_id)
        timestamp = json.loads(vector_str)
        is_ack = is_ack in ["True", "true", "1"]
        is_order_marker = is_order_marker in ["True", "true", "1"]

        return [sender, message_id, is_ack, is_order_marker, timestamp, message]

    def ip2int(self, addr):
        return struct.unpack("!I", socket.inet_aton(addr))[0]

    def int2ip(self, addr):
        return socket.inet_ntoa(struct.pack("!I", addr))

    def deliver(self, sender, message):
        """ Do something with the received message. """
        # TODO: save message to database
        logging.info("%s says: %s" % (sender, message))

    def message_queue_handler(self, running):
        """ Thread that actually sends out messages when send time <= current_time. """
        # TODO: if we have removed randomness in sending messages, can we simplify this?
        while running:
            (send_time, message, ip, port) = self.queue.get(block=True)
            if send_time <= time.time():
                self.sock.sendto(message, (ip, port))
            else:
                self.queue.put((send_time, message, ip, port))
                time.sleep(0.01)

    def ack_handler(self, running):
        """ Thread that re-sends all unacknowledged messages. """
        while running:
            time.sleep(0.2)

            with self.mutex:
                new_unack_messages = []
                for dest_id, packed_message in self.unack_messages:
                    [
                        _,
                        message_id,
                        is_ack,
                        is_order_marker,
                        message_timestamp,
                        message,
                    ] = self.unpack_message(packed_message)
                    if (dest_id, message_id) not in self.has_acknowledged:
                        new_unack_messages.append((dest_id, packed_message))
                        self.unicast_send(
                            dest_id,
                            message,
                            msg_id=message_id,
                            is_ack=is_ack,
                            is_order_marker=is_order_marker,
                            timestamp=message_timestamp,
                        )
                self.unack_messages = new_unack_messages

    def incoming_message_handler(self, running):
        """ Thread that listens for incoming UDP messages """
        while running:
            try:
                self.unicast_receive()
            except (socket.timeout, BlockingIOError):
                pass

    def run(self):
        """ Initialize and start all threads. """
        thread_routines = [
            self.ack_handler,
            self.message_queue_handler,
            self.incoming_message_handler,
        ]

        count = 1
        for thread_routine in thread_routines:
            thread = threading.Thread(
                target=thread_routine,
                args=(self.running,),
                name="ReliableSocketWorker-%s" % count,
            )
            thread.daemon = True
            thread.start()
            logging.info("Thread %s started." % thread.name)
            self.threads.append(thread)
            count += 1