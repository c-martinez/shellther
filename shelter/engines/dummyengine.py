from baseengine import BaseEngine

class DummyEngine(BaseEngine):
    def exitAction(self):
        print '''Do exit action at the end.'''

    def timedAction(self):
        print '''Do timed action every X time.'''
