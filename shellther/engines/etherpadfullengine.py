from .baseengine import BaseEngine

from etherpad_lite import EtherpadLiteClient
from .shellloggerExtract import sanitize

# TODO: document

class EtherpadFullEngine(BaseEngine):
    def __init__(self, apikey, padID, targetFile, base_url='http://localhost:9001/api'):
        self._con = EtherpadLiteClient(base_params={'apikey': apikey}, base_url=base_url)
        self._padID = padID
        self._file = targetFile

    def timedAction(self):
        with open(self._file, 'r') as fin:
            newText = fin.read()
        newText = sanitize(newText)
        self._con.setText(padID=self._padID, text=newText)

    def exitAction(self):
        pass
