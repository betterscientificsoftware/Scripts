#!/usr/bin/env python
"""
Core validation functions
"""
from debug import print_debug
from debug import print_verbose



def load_textfile_to_stringlist(filename, program_options=None):
    """
    Load a text file and return it as a list of strings and strip
    traling whitespce.

    @param filename: [required] The input filename
    @param program_optons: [optional] program options (from OptionParser).
    """
    output = []

    print_verbose("Load input file: %s"%(filename), program_options)

    with open(filename, "r") as ifp:
        for line in ifp:
            output.append( line.rstrip() )

    if program_options.param_log_debug is True:
        print_debug("file contents:", program_options)
        for line in output:
            print_debug(line, program_options)

    print_verbose("Load input file: Loaded %d lines"%(len(output)), program_options)
    print_verbose("Load input file: Complete", program_options)

    return output


