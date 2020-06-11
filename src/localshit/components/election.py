import logging

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)

class Election:

    def __init__(self):

        # first, mark member as non-participant
        self.participant = False
        logging.info("Election Class initialized")

        # second, send election msg with ip to neighbour
    
    def start_election(self):
            logging.info("starting election")
            self.participant = True


    