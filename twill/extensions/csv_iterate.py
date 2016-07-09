"""
An extension function to iterate over a list of comma-separated values.

Function 'csv_iterate' reads a file containing one or more rows of
comma-separated columns, assigns them to col1...colN, and, for each row,
executes the given twill script.
"""

import csv

from twill import execute_file, log, namespaces

__all__ = ['csv_iterate']


def csv_iterate(filename, scriptname):
    """>> csv_iterate <csv_file> <script>

    For each line in <csv_file>, read in a list of comma-separated values,
    put them in $col1...$colN, and execute <script>.
    """
    global_dict, local_dict = namespaces.get_twill_glocals()

    reader = csv.reader(open(filename, "rb"))
    for i, row in enumerate(reader, 1):
        log.debug('csv_iterate: on row %d of %s', i, filename)
        for j, col in enumerate(row, 1):
            global_dict["col%d" % (j,)] = col

        execute_file(scriptname, no_reset=True)
