import abc
import threading
import time
import os

def runCommand(cmd):
    '''Run given command interactively. Return command exit code.
    '''
    cmd = cmd.split()
    code = os.spawnvpe(os.P_WAIT, cmd[0], cmd, os.environ)
    if code == 127:
        sys.stderr.write('{0}: command not found\n'.format(cmd[0]))
    return code

#print 'TODO: '
#print ' - Start listener'
#print ' - Start script command'
#print ' - Push output of script command'
# runCommand('/bin/bash')

class AbstractEngine(object):
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
            print 'Every X time run timed action...'
            engine.timedAction()
            # time.sleep(1)
        self._lock.release()
        print 'On exit run end action'
        engine.exitAction()

    def stop(self):
        self._running = False
        self._lock.acquire()
        self._lock.notify()
        self._lock.release()


class DummyEngine(AbstractEngine):
    def setup(self):
        print '''Do setup.'''

    def exitAction(self):
        print '''Exit action.'''

    def timedAction(self):
        print '''Timed action.'''

def doStuff(engine):
    engine.start()
    runCommand('/bin/bash')
    engine.stop()

engine = DummyEngine()
doStuff(engine)

print 'Finished main script'
