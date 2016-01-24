"""Shelter. Log your terminal and sync it with Etherpad (or other repository).

Usage:
  main.py <logfile> <padID> [--full | --section [--marker=<m>]]

Options:
  -h --help     Show this screen.
  --marker=<m>  Marker used as separator. If None, random marker is generated [default: None].
"""
# logfile = 'logfile.txt'
# padID = 'test'

# marker = None
# doSection = False

# apikey = '2dd4c81386f54847e329fcfd6705314c410804cd1605d03d09d100f291f51acb'
# base_url = 'http://localhost:9001/api'

#  naval_fate.py ship <name> move <x> <y> [--speed=<kn>]
#  naval_fate.py ship shoot <x> <y>
#  naval_fate.py mine (set|remove) <x> <y> [--moored | --drifting]
#  naval_fate.py (-h | --help)
#  naval_fate.py --version









import os
import sys
from docopt import docopt

from engines import EtherpadFullEngine, EtherpadSectionEngine

# TODO: Add docopt documentation

def runCommand(cmd):
    '''Run given command interactively. Return command exit code.'''
    cmd = cmd.split()
    code = os.spawnvpe(os.P_WAIT, cmd[0], cmd, os.environ)
    if code == 127:
        sys.stderr.write('{0}: command not found\n'.format(cmd[0]))
    return code

def recordConsole(engine, logfile):
    engine.start()
    # TODO: post-process logfile to remove back lines and etc.
    # runCommand('bash dostuff.sh')
    runCommand('script -f ' + logfile)
    engine.stop()

def doMain(apikey, padID, marker, base_url, logfile, doSection):
    if doSection:
        engine = EtherpadSectionEngine(apikey, padID, targetFile=logfile, marker=marker, base_url=base_url)
    else:
        engine = EtherpadFullEngine(apikey, padID, targetFile=logfile, base_url=base_url)
    recordConsole(engine, logfile)

# TODO: Read these parameters from config file or docopt
# apikey = '2dd4c81386f54847e329fcfd6705314c410804cd1605d03d09d100f291f51acb'
# base_url = 'http://localhost:9001/api'
# padID = 'test'
# marker = None
# logfile = 'logfile.txt'
# doSection = False

arguments = docopt(__doc__, version='Shelter v0.1')
print arguments
# print (apikey, padID, marker, base_url, logfile, doSection)
# doMain(apikey, padID, marker, base_url, logfile, doSection)
