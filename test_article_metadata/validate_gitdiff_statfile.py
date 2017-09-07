#!/usr/bin/env python
"""
The purpose of this file is to generate a list of package enables that
when used with forward packages turned on will result in the right set of
tests being run to test a pull request. The current implementation is neither
maintainable or precise. It is a proof-of-concept at this point.

file with list of changed files - generated currently with
git diff origin/$TRILINOS_TARGET_BRANCH --numstat > ../gitchanges.txt
assumed to be in the directory where this script is executed from
"""
import os
import os.path
import re
import sys
from optparse import OptionParser

from csv_tools import *
from utilities import *

from metadata_validation_core import *



def process_program_options():
    parser = OptionParser()
    parser.add_option("-f", "--filename", dest="param_ifilename",    default=None,              help="[REQUIRED] Input gitdiff file.")
    parser.add_option("-s", "--specfile", dest="param_specfilename", default=None,              help="[REQUIRED] Constraints Specification Filename")
    parser.add_option("-p", "--package-list", dest="param_pkglistfile",  default=None,              help="[REQUIRED] Package list spec file (CSV)")
    parser.add_option("-d", "--dry-run",  action="store_true",       dest="param_dry_run",      default=False, help="[OPTIONAL] Dry Run. If      enabled then don't modify any files. Default: %default")
    parser.add_option("-D", "--debug",    action="store_true",       dest="param_log_debug",    default=False, help="[OPTIONAL] Debug mode.      Default: %default")
    parser.add_option("-V", "--verbose",  action="store_true",       dest="param_log_verbose",  default=False, help="[OPTIONAL] Verbose mode.    Default: %default")
    parser.add_option(      "--color",    dest="param_color_stdout", default=None,              choices=["tty"],
                            help="[OPTIONAL] Colorize the output. Use --color=tty for ansi color.  Default: %default")
    (options, arguments) = parser.parse_args()

    # print out help if no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if options.param_ifilename is None or    \
       options.param_specfilename is None or \
       options.param_pkglistfile is None:
        parser.print_help()
        sys.exit(1)

    if options.param_specfilename is None:
        parser.print_help()
        sys.exit(1)

    # debug implies verbose mode.
    if options.param_log_debug:
        options.param_log_verbose = True

    if options.param_log_debug:
        print_debug("Program Options:", options)
        for k,v in options.__dict__.items():
            print_debug("    %-20s: %s"%(k,v), options)
        print_debug("    %-20s: %s"%("working directory", os.path.dirname(os.path.realpath(__file__))), options)
        print_debug("",options)

    return options



class package(object):
    """
    Properties:
        - package_name
        - package_path

    Accessors:
        - name()
        - path()

    Methods:
        - is_in_package(path)
    """
    def __init__(self, package_name, package_path):
        self.package_name = package_name
        self.package_path = package_path

    def name(self):
        return self.package_name

    def path(self):
        return self.package_path

    def contains_path_fragment(self, path):
        """
        True if the given path is part of the "package path"
        """
        pattern = r"%s"%(self.package_path)
        return re.search(pattern, path) is not None
        # return path in self.package_path

    def __str__(self):
        return "%s\t%s"%(self.name(), self.path())



class package_collection(object):
    """
    Properties:
        - packages (dict)  { package_name: <package object> }
    """

    def __init__(self):
        self.packages = {}

    def add(self, package_name, package_path):
        self.packages[package_name] = package(package_name,package_path)

    def iteritems(self):
        for key in self.packages:
            yield key, self.packages[key]
        raise StopIteration

    def get_package(self, package_name):
        return self.packages[package_name]

    def find_package(self, path):
        """
        Return the first package with a path containing the path parameter string.
        If no matches, return None.
        """
        output = None
        for pkg_name,pkg in self.packages.iteritems():

            if pkg.contains_path_fragment(path):
                output = pkg
                break

        return output

    def prettyString(self, indent=0):
        """
        Generate a string containing the contents in a nicely formatted look.
        """
        s = ""
        for key in self.packages:
            s += "%s%-20s %s\n"%(" "*indent, self.packages[key].name(), self.packages[key].path())
        return s

    def prettyPrint(self, indent=0):
        """
        Print contents in a visually nice way.
        """
        print self.prettyString(indent=indent)
        return True



def gen_bssio_packages(packagelist_filename=None):
    """
    """
    packages = package_collection()
    if packagelist_filename is None:
        packages.add("default", ".*")
    else:
        data = csv_data(delimiter=",", first_row_is_header=True, ignore_empty_lines=True, comment_char="#")
        data.load_csv(packagelist_filename)
        for entry in data.iterrows_dict():
            packages.add(entry["Package_Name"], entry["Package_Path"])

    return packages



class git_diff_entry(object):
    """
    Generic class for git diff entries.

    Stores a list of files from git diff output that have been changed.
    """
    def __init__(self, line):
        """
        c'tor.
        """
        self.initialize(line)

    def initialize(self, line):
        # Initializer should be customized to the specific type of git diff output
        # we need.  such as --numstat, --summary, --name-only, etc.
        raise NotImplemented, "this is an abstract class"

    def check_param_str(self, param):
        """
        generic checker to make sure paramter is a file like string.
        """
        if not isinstance(param, str):
            raise TypeError, "invalid parameter, string expected."
        return True

    @property
    def filepath(self):
        try:
            return self._filepath
        except:
            self._filepath = None
        return self._filepath

    @filepath.setter
    def filepath(self, value):
        self.check_param_str(value)
        self._filepath = self.add_trailing_sep_to_path(value)
        self._absfilepath = self.add_trailing_sep_to_path(os.path.abspath(value))

    @property
    def absfilepath(self):
        try:
            return self._absfilepath
        except:
            self._absfilepath = None
        return self._absfilepath

    @absfilepath.setter
    def absfilepath(self, value):
        self.check_param_str(value)
        self._absfilepath = self.add_trailing_sep_to_path(value)
        self._filepath = self.add_trailing_sep_to_path(os.path.relpath(value))

    def add_trailing_sep_to_path(self, path):
        """ Add trailing path separator to paths if they don't already have one. """
        self.check_param_str(path)
        if len(path) > 0 and path[-1] != os.path.sep:
            path += os.path.sep
        return path

    @property
    def filename(self):
        try:
            return self._filename
        except:
            self._filename = None
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value

    @property
    def fileext(self):
        try:
            return self._fileext
        except:
            self._fileext = None
        return self._fileext

    @fileext.setter
    def fileext(self, value):
        self._fileext = value

    def gen_filename(self):
        return self.filename + self.fileext

    def gen_file_with_path(self):
        """
        return the filename assembled with path + filename + ext.
        """
        return os.path.join(self.filepath, self.gen_filename() )

    def gen_file_with_abspath(self):
        """
        return string of the filename + absolute path.
        """
        return os.path.join(self.absfilepath, self.gen_filename() )

    def gen_file_with_relpath(self):
        """
        return string of the filename's relative path to cwd.
        """
        return os.path.relpath(self.gen_file_with_path(), start='.' )

    def to_dict(self):
        """
        Return a dictionary based representation of the data.

        Required keys:  { "filepath", "filename", "fileext" }
        """
        return { "filepath": self.filepath,
                 "filename": self.filename,
                 "fileext" : self.fileext
               }

    def init_filename(self, filename):
        """
        Initialize data structure from a filename.

        Arguments:
          filename (str): a filename of the form 'path/to/filename.ext'

        Returns:
          bool: True if successful.
        """
        _filepath, _filename = os.path.split(filename)
        _filename, _fileext  = os.path.splitext(_filename)

        self.absfilepath = os.path.abspath(_filepath)

        self.filepath = _filepath
        self.filename = _filename
        self.fileext  = _fileext

        return True



# TODO: Create git_diff_entry subclasses for --name-status and --numstat variations (if necessary)
class git_diff_entry_nameonly(git_diff_entry):
    def initialize(self, line):
        """
        Initializer for name-only version.
        - there will be one entry per line in the form path/to/filename.ext

        Arguments:
          line (str): For this mode, there is one entry per line, and is formatted as "path/to/filename.ext"

        Returns:
          bool: True if successful.
        """
        self.init_filename(line)
        return True



def prepare_git_diff_lines(file_lines):
    """
    input  : list of lines from git --name-only data file
    output : list of git_numstat_entry
    """
    output = []
    for line in file_lines:
        output.append( git_diff_entry_nameonly(line) )
    return output



def main():
    """
    """
    program_options = process_program_options()

    print_verbose("-"*80, program_options)
    print_verbose("Prepare BSSIO test package information.", program_options)
    print_verbose("-"*80, program_options)
    print_verbose("Load package data from file: %s"%(program_options.param_pkglistfile), program_options)
    packages = gen_bssio_packages(program_options.param_pkglistfile)
    # packages.prettyPrint(indent=2)
    print_verbose("Packages:\n%s"%(packages.prettyString(indent=6).rstrip()), program_options)

    # Load specfile data
    print_message("-"*80, program_options)
    print_message("Load metadata specfile information", program_options)
    print_message("-"*80, program_options)
    specfile_data = load_metadata_specfile(program_options.param_specfilename, program_options)

    # load file into lines.
    print_message("-"*80, program_options)
    print_message("Load git diff file", program_options)
    print_message("-"*80, program_options)
    file_lines = load_textfile_to_stringlist(program_options.param_ifilename, program_options)
    gitdiff_entry_list = prepare_git_diff_lines(file_lines)

    print_message("-"*80, program_options)
    print_message("Inspect files", program_options)
    print_message("-"*80, program_options)

    all_tests_passed = True

    summary_num_tested  = 0
    summary_num_passed  = 0
    summary_num_failed  = 0
    summary_list_failed = []

    for entry in gitdiff_entry_list:
        summary_num_tested += 1

        print_message("-", program_options)
        print_message("Inspect File: [%s] %s"%(entry.gen_filename(), entry.gen_file_with_relpath()), program_options)
        print_debug  ("    abs file: %s"%(entry.gen_file_with_abspath()), program_options)
        print_message("-", program_options)

        pkg = packages.find_package(entry.filepath)

        # so, if pkg is not None, then it means it's in the set of packages that we care about checking
        # and this file should be tested.

        # if the file 'fails' the check then we should print out the message and keep going but set
        # the overall pass/fail status to FAIL.
        if pkg is None:
            print_message("Skipping: file is not in a designated package area.", program_options)
            continue

        print_message("Checking metadata ...", program_options)

        passed,failmsg = check_metadata_in_file(entry.gen_file_with_relpath(), specfile_data, program_options)

        if passed is True:
            print_message("Metadata verification PASSED", program_options)
            summary_num_passed += 1
        else:
            summary_num_failed += 1
            failmsg = str(failmsg).rstrip()
            print_message("Metadata verification FAILED", program_options)
            print_verbose("Message:\n=== Begin Failure Message ===\n%s\n=== End Failure Message ==="%(failmsg), program_options)
            summary_list_failed.append(entry.gen_file_with_relpath())
            all_tests_passed = False

        print_message("-"*40, program_options)

    print_message("Summary:", program_options)
    print_message("  Num Tested: %d"%(summary_num_tested), program_options)
    print_message("  Num Passed: %d"%(summary_num_passed), program_options)
    print_message("  Num Failed: %d"%(summary_num_failed), program_options)
    print_message("  Files failed:", program_options)
    for e in summary_list_failed:
        print_message("  - %s"%(e), program_options)

    if all_tests_passed is True:
        print_message("Finished: All testsed files PASSED", program_options)
    else:
        print_message("Finished: Something FAILED", program_options)

    return all_tests_passed


if __name__ == "__main__":
    status = main()

    if status is False:
        exit (1)

