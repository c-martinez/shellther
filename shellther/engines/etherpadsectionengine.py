from .baseengine import BaseEngine

from etherpad_lite import EtherpadLiteClient
from .shellloggerExtract import sanitize

import string
import random

# TODO: document

class EtherpadSectionEngine(BaseEngine):
    def __init__(self, apikey, padID, targetFile, base_url='http://localhost:9001/api', marker=None):
        self._con = EtherpadLiteClient(base_params={'apikey': apikey}, base_url=base_url)
        self._padID = padID
        self._file = targetFile
        if marker==None:
            marker = id_generator(10)
        self._lineMarker = '===== ' + marker + ' ============='

        # Insert line markers at the end of pad
        pad = self._con.getText(padID=self._padID)
        newText = pad['text'] + self._lineMarker + '\n' + self._lineMarker
        self._con.setText(padID=self._padID, text=newText)

    def timedAction(self):
        with open(self._file, 'r') as fin:
            fileText = fin.read()
        fileText = sanitize(fileText)
        pad = self._con.getText(padID=self._padID)
        text = pad['text']
        parts = text.split(self._lineMarker)
        newText = parts[0] + \
                  self._lineMarker + '\n' + \
                  fileText + '\n' + \
                  self._lineMarker + \
                  parts[2]
        self._con.setText(padID=self._padID, text=newText)

    def exitAction(self):
        pass

# from https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
