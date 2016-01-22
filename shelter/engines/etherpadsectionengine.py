from baseengine import BaseEngine

from etherpad_lite import EtherpadLiteClient

class EtherpadSectionEngine(BaseEngine):
    def __init__(self, apikey, base_url, padID, marker=None):
        self._con = EtherpadLiteClient(base_params={'apikey': apikey}, base_url=base_url)
        self._padID = padID
        if marker==None:
            # TODO: Random generate string
            marker = 'XXXXXXXXXXXX'
        self._lineMarker = '===== ' + marker + ' ============='

        # Insert line markers at the end of pad
        pad = self._con.getText(padID=self._padID)
        newText = pad['text'] + self._lineMarker + '\n' + self._lineMarker
        self._con.setText(padID=self._padID, text=newText)

    def exitAction(self):
        print '''Do exit action at the end.'''

    def timedAction(self):
        newText = 'New text'
        pad = self._con.getText(padID=self._padID)
        text = pad['text']
        parts = text.split(self._lineMarker)
        newText = parts[0] +
                  self._lineMarker + '\n' +
                  newText + '\n' +
                  self._lineMarker +
                  parts[2]
        self._con.setText(padID=self._padID, text=newText)
