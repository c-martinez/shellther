import os
import sys

from .engines import EtherpadFullEngine, EtherpadSectionEngine
from tempfile import NamedTemporaryFile
try:
    from ConfigParser import SafeConfigParser
except:
    from six.moves.configparser import SafeConfigParser


def runCommand(cmd):
    '''Run given command interactively. Return command exit code.'''
    cmd = cmd.split()
    code = os.spawnvpe(os.P_WAIT, cmd[0], cmd, os.environ)
    if code == 127:
        sys.stderr.write('{0}: command not found\n'.format(cmd[0]))
    return code

def buildCommandLine(logfile):
    platform = sys.platform
    if platform == "linux" or platform == "linux2":
        return 'script -f ' + logfile
    elif platform == "darwin":
        return 'script -t 0 ' + logfile
    elif platform == "win32":
        sys.stderr.write('Windows is not currently supported. Sorry!')
        sys.exit()
    else:
        sys.stderr.write('Unknown platform. Don\'t know what to do. Bye!')
        sys.exit()

def recordConsole(engine, logfile):
    engine.start()
    runCommand(buildCommandLine(logfile))
    engine.stop()

def parseArgs(args):
    padID = args['<padID>']
    doSection = args['--section']
    marker = args['--marker']

    defaultConfig = {
            'apikey' : '',     # Content of etherpad's APIKEY.txt
            'baseurl': ''      # Something like http://localhost:9001/api
        }
    config = SafeConfigParser(defaultConfig)
    config.add_section('shellther')
    if args['--config']:
        config.read(args['--config'])
    apikey = config.get('shellther', 'apikey')
    baseurl = config.get('shellther', 'baseurl')

    # Validate config files
    if apikey=='':
        print('Cannot work without an API key!')
        sys.exit()
    if baseurl=='':
        print('Need a valid URL!')
        sys.exit()

    logfile = NamedTemporaryFile(delete=True).name
    print('Using temp file: ',logfile)
    doMain(apikey, padID, marker, baseurl, logfile, doSection)


def doMain(apikey, padID, marker, baseurl, logfile, doSection):
    if doSection:
        engine = EtherpadSectionEngine(apikey, padID, targetFile=logfile, marker=marker, base_url=baseurl)
    else:
        engine = EtherpadFullEngine(apikey, padID, targetFile=logfile, base_url=baseurl)
    recordConsole(engine, logfile)
