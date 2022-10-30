"""twill multiprocess execution system."""

import sys
import os
import time

from optparse import OptionParser

from . import execute_file, set_log_level

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
    repeat = 0

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
                print(f'[twill-fork parent: process {child_pid} FAILED:'
                      f' exit status {status}]')
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
        print(f'number of processes: {options.processes}')
        print(f'total executed: {total_exec}')
        print(f'total time to execute: {total_time:.2f} s')
        if total_exec:
            avg_time = 1000 * total_time / total_exec
            print(f'average time: {avg_time:.2f} ms')
        else:
            print('(nothing completed, no average!)')
        print()

    else:

        pid = os.getpid()
        print(f'[twill-fork: pid {pid} : executing {repeat} times]')

        start_time = time.time()

        set_log_level('warning')
        for i in range(repeat):
            for filename in args:
                execute_file(filename, initial_url=options.url)

        end_time = time.time()
        this_time = end_time - start_time

        # write statistics
        filename = f'.status.{pid}'
        with open(filename, 'w') as fp:
            info = (this_time, repeat)
            dump(info, fp)

    sys.exit(-1 if failed else 0)


if __name__ == '__main__':
    main()
