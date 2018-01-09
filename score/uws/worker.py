import score.serve
import threading
from ._hub import Hub


class UwsWorker(score.serve.Worker):
    """
    A :class:`score.serve.Worker` startung a uWebSockets server.
    """

    __hub = None

    def __init__(self, ws_conf):
        self.ws_conf = ws_conf
        self.stop_timeout = ws_conf.stop_timeout

    def prepare(self):
        pass

    def start(self):
        def start():
            barrier.wait()
            self.hub.start()
        barrier = threading.Barrier(2)
        self.hub.listen(self.ws_conf.host, self.ws_conf.port)
        threading.Thread(target=start).start()
        barrier.wait()

    def pause(self):
        self.hub.stop_listening()
        if self.hub.connections and self.ws_conf.stop_timeout != 0:
            def wakeup(*args):
                nonlocal done
                if len(self.hub.connections) <= 1:
                    done = True
                    with condition:
                        condition.notify()
            done = False
            self.hub.add_disconnect_callback(wakeup)
            condition = threading.Condition()
            with condition:
                condition.wait_for(lambda: done,
                                   timeout=self.ws_conf.stop_timeout)
            self.hub.remove_disconnect_callback(wakeup)
        self.hub.stop()

    def stop(self):
        pass

    def cleanup(self, exception):
        pass

    @property
    def hub(self):
        if self.__hub is None:
            self.__hub = Hub()
        return self.__hub

    @hub.setter
    def hub(self, hub):
        self.__hub = hub
