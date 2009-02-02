import sys, subprocess

try:
    import pkg_resources
except ImportError:
    raise Exception("you must have setuptools installed to run the tests")

pkg_resources.require('quixote>=2.3')

from quixote.server.simple_server import run
from cStringIO import StringIO
import os
import socket
import urllib

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

def execute_twill_script(filename, inp=None, initial_url=None):
    global testdir

    if inp:
        inp_fp = StringIO(inp)
        old, sys.stdin = sys.stdin, inp_fp

    scriptfile = os.path.join(testdir, filename)
    try:
        twill.execute_file(filename, initial_url=initial_url)
    finally:
        if inp:
            sys.stdin = old

def execute_twill_shell(filename, inp=None, initial_url=None,
                        fail_on_unknown=False):
    # use filename as the stdin *for the shell object only*
    scriptfile = os.path.join(testdir, filename)
    
    cmd_inp = open(scriptfile).read()
    cmd_inp += '\nquit\n'
    cmd_inp = StringIO(cmd_inp)

    # use inp as the std input for the actual script commands.
    if inp:
        inp_fp = StringIO(inp)
        old, sys.stdin = sys.stdin, inp_fp

    try:
        try:
            s = twill.shell.TwillCommandLoop(initial_url=initial_url,
                                             stdin=cmd_inp,
                                             fail_on_unknown=fail_on_unknown)
            s.cmdloop()
        except SystemExit:
            pass
    finally:
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
