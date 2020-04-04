"""twill multiprocess execution system."""

# This file is part of the twill source distribution.
#
# twill is a extensible scriptlet language for testing Web apps,
# available at http://twill.idyll.org/.
#
# Contact author: C. Titus Brown, titus@idyll.org.
#
# This program and all associated source code files are Copyright (C)
# 2005-2007 by C. Titus Brown.  It is released under the MIT license;
# please see the included LICENSE.txt file for more information, or
# go to http://www.opensource.org/licenses/mit-license.php.

from __future__ import print_function

import sys
import os
import time

from optparse import OptionParser

from . import execute_file, set_loglevel

try:
    from cPickle import load, dump
except ImportError:  # Python 3
    from pickle import load, dump

# make sure that the current working directory is in the path
if '' not in sys.path:
    sys.path.append('')


def main():

    try:
        fork = os.fork
    except AttributeError:
        sys.exit('Error: Must use Unix to be able to fork processes.')

    parser = OptionParser()
    add = parser.add_option
    add('-u', '--url', nargs=1, action="store", dest="url",
        help="start at the given URL before each script")
    add('-n', '--number', nargs=1, action="store", dest="number",
        default=1, type="int",
        help="number of times to run the given script(s)")
    add('-p', '--processes', nargs=1, action="store",
        dest="processes", default=1, type="int",
        help="number of processes to execute in parallel")

    options, args = parser.parse_args()

    if not args:
        sys.exit('Error: Must specify one or more scripts to execute.')

    average_number = options.number // options.processes
    last_number = average_number + options.number % options.processes
    child_pids = []
    is_parent = True

    # start a bunch of child processes and record their pids in the parent
    for i in range(options.processes):
        pid = fork()
        if pid:
            child_pids.append(pid)
        else:
            repeat = average_number if i else last_number
            is_parent = False
            break

    # set the children up to run and record their stats
    failed = False

    if is_parent:

        time.sleep(1)

        total_time = total_exec = 0

        # iterate over all the child pids, wait until they finish,
        # and then sum statistics
        for child_pid in child_pids[:]:
            child_pid, status = os.waitpid(child_pid, 0)
            if status:  # failure
                print('[twill-fork parent: process %d FAILED: exit status %d]'
                      % (child_pid, status,))
                print('[twill-fork parent:'
                      ' (not counting stats for this process)]')
                failed = True
            else:  # record statistics, otherwise
                filename = '.status.%d' % (child_pid,)
                with open(filename) as fp:
                    this_time, n_executed = load(fp)
                os.unlink(filename)
                total_time += this_time
                total_exec += n_executed

        # summarize
        print('\n----\n')
        print('number of processes:', options.processes)
        print('total executed:', total_exec)
        print('total time to execute: %.2f s' % (total_time,))
        if total_exec:
            print('average time: %.2f ms' % (1000 * total_time / total_exec,))
        else:
            print('(nothing completed, no average!)')
        print()

    else:

        print('[twill-fork: pid %d : executing %d times]'
              % (os.getpid(), repeat))

        start_time = time.time()

        set_loglevel('warning')
        for i in range(repeat):
            for filename in args:
                execute_file(filename, initial_url=options.url)

        end_time = time.time()
        this_time = end_time - start_time

        # write statistics
        filename = '.status.%d' % (os.getpid(),)
        with open(filename, 'w') as fp:
            info = (this_time, repeat)
            dump(info, fp)

    sys.exit(-1 if failed else 0)


if __name__ == '__main__':
    main()
