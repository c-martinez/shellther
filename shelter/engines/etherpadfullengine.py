from baseengine import BaseEngine

from etherpad_lite import EtherpadLiteClient

class EtherpadFullEngine(BaseEngine):
    def __init__(self, apikey, base_url, padID):
        self._con = EtherpadLiteClient(base_params={'apikey': apikey}, base_url=base_url)
        self._padID = padID

    def exitAction(self):
        print '''Do exit action at the end.'''

    def timedAction(self):
        newText = 'New Text'
        self._con.setText(padID=self._padID, text=newText)
