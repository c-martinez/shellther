import os
import sys

from engines import EtherpadFullEngine, EtherpadSectionEngine

# TODO: Add docopt documentation

def runCommand(cmd):
    '''Run given command interactively. Return command exit code.
    '''
    cmd = cmd.split()
    code = os.spawnvpe(os.P_WAIT, cmd[0], cmd, os.environ)
    if code == 127:
        sys.stderr.write('{0}: command not found\n'.format(cmd[0]))
    return code

def recordConsole(engine, logfile):
    engine.start()
    # TODO: post-process logfile to remove back lines and etc.
    runCommand('script -f ' + logfile)
    engine.stop()

# TODO: Read these parameters from config file or docopt
apikey = 'e792c32e44952f8d24c2cabe35bf36a12003d04726d3579c36f5a1d00569c81c'
base_url = 'http://localhost:9001/api'
padID = 'test'
marker = None
logfile = 'logfile.txt'
doSection = True

if doSection:
    engine = EtherpadSectionEngine(apikey, padID, targetFile=logfile, marker=marker, base_url=base_url)
else:
    engine = EtherpadFullEngine(apikey, padID, targetFile=logfile, base_url=base_url)

recordConsole(engine, logfile)
