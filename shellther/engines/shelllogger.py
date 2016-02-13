"""
DISCLAIMER:
This code is not part of shellther. It is found here:
    http://pydoc.net/Python/shelllogger/1.0.1/sl.shelllogger/
However, it does not seem to have any way of installing as a package, so it has
been repackaged here.

ShellLogger: Unix shell command invocation logger

Usage: shelllogger [-s, --sanitize outfilename] <logfilename>

Upon invocation, it will spawn a new shell (either tcsh or bash, depending upon
SHELL variable).

Directory can be specified by setting (and exporting) the SHELLLOGGERDIR
environment variable to a directory which will contain the XML logfiles.

If no logfilename is specified, commands are logged to
 .shelllogger/log.<tstamp>.xml

The script will automatically change the prompt upon startup to one of the following:

bash prompt: PS1='[SL \w]$ '
tcsh prompt: set prompt='[SL %~]$ '

If called with the -s option, it will parse <logfilename> as if it was a raw file and
remove all escape characters, printing to standard out.

Much of the terminal-related logic comes from example code posted
to comp.lang.python by Donn Cave. Used here with his permission.
For the original post, see:
http://groups.google.com/group/comp.lang.python/msg/de40b36c6f0c53cc
"""


import fcntl
import sys
import os
import pty
import re
import select
import signal
import socket
import struct
import termios
import time
import errno
import codecs
import datetime

isFirst = True

# Fix for older versions of Python
try:
    True
except NameError:
    True,False = 1,0

# These are applications that use the terminal in such a way that
# it is better to not capture their output
TERMINAL_APPS = ['vi','vim','emacs','pico','nano','joe']

BASH_PROMPT = "PS1='[SL \w]$ ' \n"
TCSH_PROMPT = "set prompt='[SL %~]$ ' \n"
SHELL_PROMPTS = {'bash':BASH_PROMPT,'tcsh':TCSH_PROMPT}


def is_printable(c):
    """
    Returns true if c is a printable character.

    We do this by checking for ord value above 32 (space),
    as well as CR (\r), LF (\n) and tab (\t)

    """
    return ord(c)>=32 or c in ['\r','\n', '\t']

def sanitize(buf,
             backspaces=['\x08\x1b[K', '\x08 \x08'],
             escape_regex=re.compile(r'\x1b(\[|\]|\(|\))[;?0-9]*[0-9A-Za-z](.*\x07)?')):
    """Filter control characters out of the string buf, given a list of control codes
    that represent backspaces, and a regex of escape sequences.

    backspaces are characters emitted when the user hits backspace.
    This will probably vary from terminal to terminal, and
    this list should grow as new terminals are encountered.

    escape_regex is a Regex filter to capture all escape sequences.
    Modified from: http://wiki.tcl.tk/9673
    """
    # Filter out control characters

    # First, handle the backspaces.
    for backspace in backspaces:
        try:
            while True:
                ind = buf.index(backspace)
                buf = ''.join((buf[0:ind-1],buf[ind+len(backspace):]))
        except:
            pass

    strip_escapes = escape_regex.sub('',buf)

    # strip non-printable ASCII characters

    clean = ''.join([x for x in strip_escapes if is_printable(x)])
    return clean


class TTY:
    def __init__(self):
        self.iflag, self.oflag, self.cflag, self.lflag, \
            self.ispeed, self.ospeed, self.cc = termios.tcgetattr(0)
    def raw(self):
        # ISIG - passes Ctl-C, Ctl-Z, etc. to the child rather than generating signals
        raw_lflag = self.lflag & ~(termios.ICANON|termios.ECHO|termios.ISIG)
        raw_iflag = self.iflag & ~(termios.ICRNL|termios.IXON)
        raw_cc = self.cc[:]
        raw_cc[termios.VMIN] = 1
        raw_cc[termios.VTIME] = 0
        termios.tcsetattr(0, termios.TCSANOW, [raw_iflag, self.oflag,
                                               self.cflag, raw_lflag,
                                               self.ispeed, self.ospeed,
                                               raw_cc])
    def restore(self):
        termios.tcsetattr(0, termios.TCSANOW, [self.iflag, self.oflag,
                                               self.cflag, self.lflag,
                                               self.ispeed, self.ospeed,
                                               self.cc])

class ChildWindowResizer:
    """Informs the child process that the window has been resized."""

    def __init__(self,child_fd):
        self.child_fd = child_fd
        signal.signal(signal.SIGWINCH,self.signal_handler)

    def signal_handler(self,sig,data):
        """Signal handler that gets installed"""
        self.resize_child_window()

    def resize_child_window(self):
        """Tells the child process to resize its window"""
        s = struct.pack('HHHH', 0, 0, 0, 0)
        x = fcntl.ioctl(0,termios.TIOCGWINSZ,s)
        fcntl.ioctl(self.child_fd,termios.TIOCSWINSZ,x)


def get_shell():
  return os.path.basename(os.environ['SHELL'])

def run_shell():
    """Launch the appropriate shell as a login shell

    It will be either bash or tcsh depending on what the user is currently running.
    It checks the SHELL variable to figure it out.
    """
    shell = get_shell()
    if shell not in ['bash','tcsh']:
        raise ValueError, "Unsupported shell (only works with bash and tcsh)"
    os.execvp(shell,(shell,"-l"))

def get_log_dir():
    """Retrieve the name of the directory that will store the logfiles.

    If the SHELLLOGGERDIR environment variable is set, use that.
    Otherwise, default to ~/.shelllogger"""
    env_var = "SHELLLOGGERDIR"
    if os.environ.has_key(env_var):
        return os.environ[env_var]
    else:
        return os.path.expanduser('~/.shelllogger')

def start_recording(logfilename, debug):

    # Check for recursive call
    env_var = 'ShellLogger'
    if os.environ.has_key(env_var):
        # Recursive call, just exit
        return

    os.environ[env_var]='1'
    print "ShellLogger enabled"

    if logfilename is None:
        dirname = get_log_dir()
        try:
            os.mkdir(dirname)
            print "Creating %s directory for storing logfile" % dirname
        except OSError, e:
            # If it's anything but "File exists",then we're in trouble.
            # We'll just re-raise the exception for now
            if e.errno != errno.EEXIST:
                raise e

        logfilename = os.path.join(dirname,'log.%d.raw' % time.time())
        if debug:
            debugfilename = os.path.join(dirname,'log.%d.debug' % time.time())
        else:
            debugfilename = None

    pid, fd = pty.fork()

    # Python won't return -1, rather will raise exception.
    if pid == 0:    # child process
        try:
            run_shell()
        except:
            # must not return to caller.
            os._exit(0)

    # parent process
    input = TTY()

    input.raw()

    resizer = ChildWindowResizer(fd)
    resizer.resize_child_window()

    bufsize = 1024

    try:
        logger = Logger(logfilename, debugfilename)

        if debugfilename is not None:
            print "Warning, shelllogger running in debug mode. All keystrokes will be logged to a plaintext file. Do not type in any passwords during this session!"

        # Set the shell prompt properly
        os.write(fd,SHELL_PROMPTS[get_shell()])

        while True:
            delay = 1
            exit = 0
            try:
                r, w, e = select.select([0, fd], [], [], delay)
            except select.error, se:
                # When the user resizes the window, it will generate a signal
                # that will be handled, which will cause select to be
                # interrupted.
                if se.args[0]==errno.EINTR:
                    continue
                else:
                    raise
            for File in r:
                if File == 0:
                    first_user_input = 1
                    from_user = os.read(0, bufsize)
                    os.write(fd, from_user)
                    logger.input_from_user(from_user)

                elif File == fd:
                    try:
                        from_shell = os.read(fd, bufsize)
                        os.write(1, from_shell)
                        logger.input_from_shell(from_shell)
                        if from_shell=='':
                            exit = 1
                    except OSError:
                    # On Linux, os.read throws an OSError
                    # when data is done
                        from_shell = ''
                        os.write(1, from_shell)
                        logger.input_from_shell(from_shell)
                        exit = 1

            if exit==1:
                break

        xmlfilename = logger.done()

    except:
        input.restore()
        raise
    input.restore()
    print "ShellLogger data stored in " + xmlfilename

class Logger:
    def __init__(self,logfilename, debugfilename):
        self.logfilename = logfilename
        self.logfile = open(logfilename,'w')
        self.logfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.logfile.write('<cli-logger machine="%s">\n\n' % socket.gethostname())
        self.buffer = ''
        self.cwd = os.getcwd()
        self.state = BeginState(self)
        self.debugfilename = debugfilename
        self.isLinux = False
        if self.debugfilename is not None:
            self.debugfile = open(debugfilename, 'w')
            self.debugfile.write("<cli-debug>\n")
        else:
            self.debugfile = None

    def done(self):
        """Call when session is complete.

        Returns the name of the XML file

        """
        self.logfile.write("]]></result>\n</cli-logger-entry>\n</cli-logger>\n")
        self.logfile.close()
        if self.debugfilename is not None:
            self.debugfile.write("</cli-debug>")
        return self.raw_to_xml()

    def raw_to_xml(self):
        """Convert the .raw file, with illegal characters and escape keys, to a proper XML version.

        Returns the name of the XML file
        """
        xmlfilename = self.logfilename.replace('.raw','.xml')
        fout = codecs.open(xmlfilename, encoding="utf-8", mode="w")
        for line in codecs.open(self.logfilename,encoding="utf-8"):
            fout.write(sanitize(line))

        fout.close()
        return xmlfilename

    def input_from_shell(self,buf):
        if self.debugfile:
            self.debug_log(buf,True)
        self.state.input_from_shell(buf)
        self.state = self.state.next_state()

    def input_from_user(self,buf):
        if self.debugfile:
            self.debug_log(buf,False)
        self.state.input_from_user(buf)
        self.state = self.state.next_state()

    def write(self,buf):
        self.logfile.write(buf)

    def debug_log(self, buf, shell):
        """Record to the debug log"""

        # Handle Shell output
        if shell == True:
            self.debugfile.write("<shell time=\" " + datetime.datetime.now().strftime("%H:%M:%S ") + "\" >" )
            self.debugfile.write("<![CDATA["+buf+"]]></shell>\n")

        # Handle User Input
        else:
            self.debugfile.write("<user time=\" " + datetime.datetime.now().strftime("%H:%M:%S ") + "\" >" )
            self.debugfile.write("<![CDATA["+buf+"]]></user>\n")

# regex for matching the prompt
# this is used to identify the data directory
re_prompt = re.compile(r'(.*)^\[SL (.*)\]\$ $', re.MULTILINE | re.DOTALL | re.IGNORECASE)
mac_prompt = re.compile(re.compile(r'(?:.*)\[SL (.*)\](.*)(\$)?',re.MULTILINE | re.DOTALL | re.IGNORECASE))
linux_prompt = re.compile(r'(?:.*)\[SL (.*)\]\$',re.MULTILINE | re.DOTALL | re.IGNORECASE)

def is_enter(buf):
    # Check if buffer consists entirely of \n or \r
    for c in buf:
        if c!='\n' and c!='\r':
            return False
    return True


class BeginState:
    def __init__(self,logger):
        self.logger = logger
        self.saw_shell_input = False

    def input_from_shell(self,buf):
        # If it's the prompt, then it's just the very first shell
        m = re_prompt.match(buf)
        if m is not None:
            self.logger.cwd = os.path.expanduser(m.group(2))
            return
        # If the user just hit enter, we don't log it
        if is_enter(buf):
            return
        self.saw_shell_input = True
        # Stick the data in a buffer
        self.logger.buffer = buf

    def input_from_user(self,buf):
        # We don't actually care about input from the user,
        # we just use shell echos
        pass

    def next_state(self):
        if self.saw_shell_input:
            return UserTypingState(self.logger)
        else:
            return self

class UserTypingState:
    def __init__(self,logger):
        self.logger = logger
        self.seen_cr = False
        self.program_invoked = None

    def input_from_shell(self,buf):
        if(buf.startswith('\x0D') or buf.startswith('\r')):
            self.logger.isLinux = True
            self.seen_cr = True
            self.program_invoked = self.logger.buffer.split()[0]
            self.logger.write('''<cli-logger-entry>
<invocation time="%f"
current-directory="%s"><![CDATA[''' % (time.time(),self.logger.cwd))
            self.logger.write(self.logger.buffer)
            self.logger.write(']]></invocation>\n')
            self.logger.buffer = buf;

        elif is_enter(buf) and len(self.logger.buffer)>0 and ( self.logger.buffer[-1]!='\\' or 'logout' in buf ):
            self.seen_cr = True
            self.program_invoked = self.logger.buffer.split()[0]
            self.logger.write('''<cli-logger-entry>
<invocation time="%f"
current-directory="%s"><![CDATA[''' % (time.time(),self.logger.cwd))
            self.logger.write(self.logger.buffer)
            self.logger.write(']]></invocation>\n')
        else:
            self.logger.buffer += buf

    def input_from_user(self,buf):
        # Don't need to take any action
        global isFirst
        if(isFirst):
            isFirst = False
            self.logger.buffer = ''
        pass

    def next_state(self):
        if self.seen_cr:
            if self.program_invoked in TERMINAL_APPS:
                return WaitingForShellNoOutputState(self.logger)
            else:
                return WaitingForShellState(self.logger)

        else:
            return self

class WaitingForShellState:
    def __init__(self,logger):
        self.logger = logger
        self.seen_shell_input = False
        self.seen_prompt = False

    def input_from_shell(self,buf):
        # Check for the case of no input, just a shell prompt
        m = re_prompt.match(buf)
        if m is not None:
            # Empty result
            try:
                self.logger.write('<result time="%f"></result>\n</cli-logger-entry>\n\n' % time.time())
                self.logger.cwd = os.path.expanduser(m.group(2))
                self.seen_prompt = True
                return
            except:
               m = mac_prompt.match(buf)
               if m is not None:
                   self.logger.cwd = os.path.expanduser(m.group(1))
                   self.logger.write('</result>\n</cli-logger-entry>\n\n' % time.time())
                   self.seen_prompt = True
                   return
        else:
            self.seen_shell_input = True
            self.logger.write('<result time="%f"><![CDATA[\n' % time.time())
            self.write_output_to_log(buf)

    def write_output_to_log(self,buf):
        self.logger.write(buf)

    def input_from_user(self,buf):
         if self.logger.isLinux:
            m = linux_prompt.match(self.logger.buffer.strip())
            if m is not None:
                self.logger.cwd = os.path.expanduser(m.group(1))
                self.logger.write('<result time="%f"></result>\n</cli-logger-entry>\n\n' % time.time())
                self.seen_prompt = True

    def shell_output_state(self,logger):
        return ShellOutputState(logger)

    def next_state(self):
        if self.seen_prompt:
            return BeginState(self.logger)
        elif self.seen_shell_input:
            return self.shell_output_state(self.logger)
        else:
            return self


class WaitingForShellNoOutputState(WaitingForShellState):
    """
    In this state, we do not want to capture any output. The typical case
    is when the user has invoked an interactive program such as a
    text editor.
    """


    def write_output_to_log(self,buf):
        pass

    def shell_output_state(self,logger):
        return ShellOutputNoOutputState(logger)



class ShellOutputState:
    def __init__(self,logger):
        self.logger = logger
        self.saw_prompt = False

    def input_from_shell(self,buf):
        # Check if it's the prompt
        m = re_prompt.match(buf)
        mac = mac_prompt.match(buf)
        linux = linux_prompt.match(buf)
        if m is not None:
            # It's the prompt!
            self.saw_prompt = True
            try:
               self.logger.cwd = os.path.expanduser(m.group(2))
               self.write_output_to_log(m.group(1))
               self.logger.write("]]></result>\n</cli-logger-entry>\n\n")
            except:
               m = mac_prompt.match(buf)
               if m is not None:
                   self.logger.cwd = os.path.expanduser(m.group(1))
                   self.logger.write('</result>\n</cli-logger-entry>\n\n' % time.time())
                   self.seen_prompt = True
        elif mac is not None:
               self.logger.cwd = os.path.expanduser(mac.group(1))
               self.logger.write("]]></result>\n</cli-logger-entry>\n\n")
        elif linux is not None:
               self.logger.cwd = os.path.expanduser(linux.group(1))
               self.logger.write("]]></result>\n</cli-logger-entry>\n\n")
        else:
            self.write_output_to_log(buf)

    def write_output_to_log(self,buf):
        self.logger.write(buf)

    def input_from_user(self,buf):
        if(self.logger.isLinux):
            self.logger.isLinux = False
            self.saw_prompt = True

    def next_state(self):
        if self.saw_prompt:
            return BeginState(self.logger)
        else:
            return self

class ShellOutputNoOutputState(ShellOutputState):
    """

    TODO: This is a dead state, which is clearly incorrect.
    """
    def write_output_to_log(self,buf):
        pass

def sanitize_file(infilename, outfilename):
    """Strip all control characters and non-UTF-8 characters from a file.

    Prints the output to standard out"""
    fout = codecs.open(outfilename, encoding="utf-8", mode="w")
    for line in codecs.open(infilename, encoding="utf-8"):
        fout.write(sanitize(line))
