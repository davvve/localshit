import threading

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def setup(self):
        """Can be overwritten."""
        pass

    def clean_up(self):
        """Can be overwritten."""
        pass

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.isSet()

    def run(self):
        self.setup()
        while not self.stopped():
            self.worker()
        self.clean_up()

    def worker(self):
        raise NotImplementedError
