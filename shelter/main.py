import os
import sys

from engines import EtherpadFullEngine, EtherpadSectionEngine

def runCommand(cmd):
    '''Run given command interactively. Return command exit code.'''
    cmd = cmd.split()
    code = os.spawnvpe(os.P_WAIT, cmd[0], cmd, os.environ)
    if code == 127:
        sys.stderr.write('{0}: command not found\n'.format(cmd[0]))
    return code

def recordConsole(engine, logfile):
    engine.start()
    runCommand('script -f ' + logfile)
    engine.stop()

def doMain(apikey, padID, marker, baseurl, logfile, doSection):
    if doSection:
        engine = EtherpadSectionEngine(apikey, padID, targetFile=logfile, marker=marker, base_url=baseurl)
    else:
        engine = EtherpadFullEngine(apikey, padID, targetFile=logfile, base_url=baseurl)
    recordConsole(engine, logfile)
