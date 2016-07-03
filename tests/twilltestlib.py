import os
import sys
import getpass
import subprocess
import urllib

from cStringIO import StringIO


_server_url = None

def get_url():
    if _server_url is None:
        raise Exception("server has not yet been started")
    return _server_url

testdir = os.path.dirname(__file__)
print 'testdir is:', testdir
sys.path.insert(0, os.path.abspath(os.path.join(testdir, '..')))

import twill

def cd_testdir():
    global cwd
    cwd = os.getcwd()
    os.chdir(testdir)

def pop_testdir():
    global cwd
    os.chdir(cwd)

def execute_script(filename, inp=None, initial_url=None):
    global testdir

    if inp:
        def new_getpass(*args):
            return ""
        
        inp_fp = StringIO(inp)
        old, sys.stdin = sys.stdin, inp_fp
        old_getpass, getpass.getpass = getpass.getpass, new_getpass

    if filename != '-':
        filename = os.path.join(testdir, filename)
    try:
        twill.execute_file(filename, initial_url=initial_url)
    finally:
        if inp:
            sys.stdin = old
            getpass.getpass = old_getpass

def execute_shell(filename, inp=None, initial_url=None,
                        fail_on_unknown=False):
    # use filename as the stdin *for the shell object only*
    scriptfile = os.path.join(testdir, filename)

    cmd_inp = open(scriptfile).read()
    cmd_inp += '\nquit\n'
    cmd_inp = StringIO(cmd_inp)

    command_loop = twill.shell.TwillCommandLoop

    # use inp as the std input for the actual script commands.
    if inp:
        inp_fp = StringIO(inp)
        old, sys.stdin = sys.stdin, inp_fp
    try:
        s = command_loop(initial_url=initial_url, stdin=cmd_inp,
                         fail_on_unknown=fail_on_unknown)
        s.cmdloop()
    except SystemExit:
        pass
    finally:
        command_loop.reset()  # do not keep as singleton
        if inp:
            sys.stdin = old
    

def run_server(create_fn, PORT=None):
    """
    Run a Quixote simple_server on localhost:PORT with subprocess.
    All output is captured & thrown away.

    The parent process returns the URL on which the server is running.
    """
    import time, tempfile
    global _server_url

    if PORT is None:
        PORT = int(os.environ.get('TWILL_TEST_PORT', '8080'))

    outfd = tempfile.mkstemp('twilltst')[0]
	
    print 'STARTING:', sys.executable, 'tests/twilltestserver.py', os.getcwd()
    process = subprocess.Popen([sys.executable, '-u', 'twilltestserver.py'],
                               stderr=subprocess.STDOUT,
                               stdout=outfd)
   
    time.sleep(1)

    _server_url = 'http://localhost:%d/' % (PORT,)
	
def kill_server():
    """
    Kill the previously started Quixote server.
    """
    global _server_url
    if _server_url != None:
       try:
          fp = urllib.urlopen('%sexit' % (_server_url,))
       except:
          pass

    _server_url = None
