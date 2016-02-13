import abc
import threading

# TODO: document

class BaseEngine(object):
    __metaclass__  = abc.ABCMeta
    _running = False
    _lock = None

    @abc.abstractmethod
    def timedAction(self):
        '''Timed action.'''

    @abc.abstractmethod
    def exitAction(self):
        '''Exit action.'''

    def start(self):
        _t = threading.Thread(target=self._doRun, args = [ ])
        self._running = True
        self._lock = threading.Condition()
        _t.start()

    def _doRun(self):
        self._lock.acquire()
        while self._running:
            self._lock.wait(2)
            self.timedAction()
        self._lock.release()
        self.exitAction()

    def stop(self):
        self._running = False
        self._lock.acquire()
        self._lock.notify()
        self._lock.release()
