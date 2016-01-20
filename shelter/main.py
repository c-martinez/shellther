import os

from engines import DummyEngine

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

def doStuff(engine):
    engine.start()
    # runCommand('/bin/bash')
    runCommand('pwd')
    engine.stop()

engine = DummyEngine()
doStuff(engine)

print 'Finished main script'
