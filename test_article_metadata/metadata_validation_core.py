#!/usr/bin/env python
"""
Core validation functions
"""
import re

from utilities import *
from checked_dictionary import checked_multivalue_dictionary


class markdown_file(object):
    """
    A markdown file handler
    """
    def __init__(self, filename, program_options=None):
        self.program_options = program_options
        self.filename_md     = filename
        self.load_textfile()


    def load_textfile(self):
        """
        Load the text file into a local stringlist
        """
        self.file_lines = []

        print_verbose("Load input file: %s"%(self.filename_md), self.program_options)

        with open(self.filename_md, "r") as ifp:
            for line in ifp:
                self.file_lines.append( line.rstrip() )

        print_verbose("Load Complete", self.program_options)

        # if self.program_options.param_log_debug is True:
            # print_debug("file contents:", self.program_options)
            # for line in self.file_lines:
                # print_debug(line, self.program_options)

        return True


    def get_stringlist(self):
        return self.file_lines


    def get_comment_sections(self):
        """
        Generator to find the comment sections.
        Note: This only works for comments that start and end with the <!--- and ---> as the ONLY thing on their lines.
        """

        comment_start_token = "<!---"
        comment_stop_token  = "--->"
        comment_file_lines  = []
        in_comment          = False
        for line_idx in xrange(len(self.file_lines)):
            line = self.file_lines[line_idx]
            line = line.strip()
            if not in_comment and line == comment_start_token:
                in_comment = True
                comment_file_lines = []
                continue
            if in_comment and line == comment_stop_token:
                in_comment = False
                yield comment_file_lines
            if in_comment:
                comment_file_lines.append(line)

        # Flag error if we've hit the end of the file and we didn't get a comment close token
        if in_comment:
            msg = "Metadata section not found. Missing comment section end token: '--->'."
            raise EOFError, msg



def get_metadata_section(md_file):
    """
    Return the metadata section (if it exists), otherwise return None
    """
    for comment in md_file.get_comment_sections():
        for line in comment:
            if re.match(r"^Publish:", line) is not None:
                return comment
    return None



def is_metadata_section(line_list, program_options):
    """
    param lines (list): A list of strings where each entry is a single line with
                        trailing and leading whitespace removed.
    Returns TRUE if the given section contains the metadata section.
    - This will specifically look for a line that starts with "Publish: "
    """
    output = False

    for line in line_list:
        if re.match(r"^Publish:", line) is not None:
            output = True
    return output



def tokenize_metadata(metadata_file_lines, program_options):
    """
    Tokenize the metadata in the file into key/value pairs.
    """
    metadata_token_list = []
    for line in metadata_file_lines:
        line=line.strip()
        # Skip empty lines because there won't be any key / value pairs on them.
        if len(line) == 0:
            continue
        try:
            key,value_list = re.split(":", line, maxsplit=1)
        except:
            print "Error: Failed to splt the metadata line: '%s'"%(line)
            print "       Most likely this is because the line is not properly"
            print "       formed as a 'key:value(,value)*' style line."
            print "       Please check that the separator is a ':' character."
            raise ValueError("Failed to split the metadata line: '%s'"%(line) )

        key = key.strip()
        for v in value_list.split(","):
            v = v.strip()
            if v is not None and v != "":
                metadata_token_list.append( (key,v) )

    return metadata_token_list



def check_metadata_tokens(metadata_tokens, mv_dict, program_options):
    """
    mv_dict is a checked_multivalue_dictionary with appropriate rules set up.
    """
    do_validate = False

    # First pass: Loop through tokens and look for key="Publish" and value="yes"
    #             If we find that, then do the full check.  Otherwise, the detailed
    #             test isn't performed.
    for key,value in metadata_tokens:
        if key == "Publish" and value == "yes":
            do_validate = True

    # Second pass: Check the values of the metadata to make sure they're correct.
    if do_validate is True:
        for key,value in metadata_tokens:
            print key,value
            mv_dict.append_property_value(key,value)
    else:
        print_message("Skipping metadata check because Publish=yes is not set.", program_options)

    return None



def check_metadata_stringlist(metadata_stringlist, specfile_data, program_options):
    """
    Check the content of the metadata (a list of strings, one for each line)
    and return True or False if the metadata content passed.

    Returns (tuple):
        bool: True if the metadata passed
              False otherwise.
        str : "" if test passed
              reasons for failure if the test failed.
    """
    output_passed = True
    output_info   = ""

    # Set up the constraints in the checked dictionary
    mv_dict = setup_mv_dict_from_specification(specfile_data, program_options)

    metadata_tokens = tokenize_metadata(metadata_stringlist, program_options)

    try:
        check_metadata_tokens(metadata_tokens, mv_dict, program_options)
    except ValueError, msg:
        output_passed = False
        output_info   = msg

    return output_passed, output_info



def check_metadata_in_file_lines(md_file, specfile_data, program_options):
    """
    """
    output_passed  = True
    output_failmsg = ""
    metadata_lines = None
    try:
        for comment in md_file.get_comment_sections():
            if is_metadata_section(comment, program_options):
                output_passed,output_failmsg = check_metadata_stringlist(comment, specfile_data, program_options)
                metadata_lines = comment
                break

    except EOFError, msg:
        output_passed  = False
        output_failmsg = msg
        print_verbose("WARNING:", program_options)
        print_verbose(msg, program_options)
        # return output_passed, output_failmsg

    # If there's no metadata section...
    # - PASS the check since we are only testing for bad metadata sections, not existence of metadata.
    if metadata_lines is None:
        print_debug("No metadata found", program_options)
        output_failmsg = "No metadata section was found"
        output_passed  = True

    # If the metadata section exists...
    else:
        print_debug("===== metadata begin =====", program_options)
        for line in metadata_lines:
            print_debug(line, program_options)
        print_debug("===== metadata end =====", program_options)

    return output_passed,output_failmsg



def check_metadata_in_file(filename, specfile_data, program_options):
    """
    Entry Point...
    """
    print_debug("Check metadata for '%s': "%(filename), program_options)
    output_passed  = True
    output_failmsg = ""
    md_file = markdown_file(filename, program_options)
    output_passed,output_failmsg = check_metadata_in_file_lines(md_file, specfile_data, program_options)
    return output_passed,output_failmsg



def setup_mv_dict_from_specification(specfile_data, program_options=None):
    """
    Set up the rules for the checked dictionary from specfile data.
    See load_metadata_specfile() for information on the required data structure.
    """
    print_debug("Configuring Restrictions", program_options)

    mv_dict = checked_multivalue_dictionary()

    if not isinstance(specfile_data, list):
        raise TypeError, "expected a list"

    for entry in specfile_data:

        if 'R' == entry['type']:
            print_debug("ADD RESTRICTION     : '%s' CAN HAVE '%s'"%(entry['property_name'], entry['allowable_value']), program_options)
            mv_dict.add_restriction(entry['property_name'], restrictions=entry['allowable_value'])

        if 'D' == entry['type']:
            print_debug("ADD RESTRICTION DEP : '%s' CAN HAVE '%s' IF '%s' HAS '%s'"%(entry['property_name'],
                                                  entry['allowable_value'],
                                                  entry['dependency_name'],
                                                  entry['dependency_value']), program_options)

            mv_dict.add_restriction_dependency(property_name=entry['property_name'],
                                               dependency_name = entry['dependency_name'],
                                               dependency_value = entry['dependency_value'],
                                               restrictions=entry['allowable_value'])

        if 'N' == entry['type']:
            print_debug("ADD RESTRICTION NONE: '%s'"%(entry['property_name']), program_options)
            mv_dict.add_restriction(property_name=entry['property_name'], restrictions=None)

        if 'DO' == entry['type']:
            # todo: handle Date-Optional fields here.
            print_debug("ADD RESTRICTION DATE-OPTIONAL: '%s'"%(entry['property_name']), program_options)
            mv_dict.add_restriction_date(property_name=entry['property_name'])

    print_debug("%s"%(mv_dict), program_options)

    return mv_dict



def load_metadata_specfile(filename, program_options=None):
    """
    Load the metadata spec file.

    Returns: A list of dicts:
    [
      {'type': 'R', 'property_name': <string>,   'allowable_value':  <string>
      }
      {'type': 'D', 'property_name': <string>,   'allowable_value':  <string>
                    'dependency_name': <string>, 'dependency_value': <string>
      }
      {'type': 'N', 'property_name': <string>
      }
      {'type': 'DO', 'property_name': <string>
      }
    ]

    Type R entries are simple restrictions in which keys with property_name may only have values
    in the allowable_value list.

    Type D entries have restrictions based on a dependency to another property.  dependency_name
    contains the property_name this property has a dependency on.  Dependency_value is the value
    of the other property that we're applying a restriction to for allowable_value.

    Type DO entries are a Date-Optional field.  Date formats are YYYY-MM-DD.

    For example:
        property_name: FOO
        dependency_name: BAR
        dependency_value: baz
        allowable_value: biff

        Says that the property FOO can contain the value 'biff' if the value of BAR is 'baz'

    """
    print_verbose("Load metadata spec file: %s"%(filename), program_options)

    specfile_data = []

    ifp = open(filename, "r")

    for line in ifp:
        line = line.strip()

        if len(line)==0:
            continue

        if line[0] == "#":
            continue

        # Get the field type.
        line_type, line_str = line.split(" ", 1)
        line_type = line_type.upper()

        # Prune whitespaces
        line_type = line_type.strip()

        if line_type not in ['R', 'D', 'N', 'DO']:
            raise ValueError, "Bad value in column 0.  Allowable values are 'R', 'D', 'N', 'DO' but I got a '%s'"%(line[0])

        line_contents = [x.strip() for x in line_str.strip().split(',')]

        print_debug("%s: %s"%(line_type, line_contents), program_options)

        entry = { 'type': line_type }
        if line_type == 'R':
            entry['property_name']   = line_contents[0]
            entry['allowable_value'] = line_contents[1]
        elif line_type == 'D':
            entry['property_name']    = line_contents[0]
            entry['dependency_name']  = line_contents[1]
            entry['dependency_value'] = line_contents[2]
            entry['allowable_value']  = line_contents[3]
        elif line_type == 'N':
            entry['property_name'] = line_contents[0]
        elif line_type == 'DO':
            entry['property_name'] = line_contents[0]
        else:
            raise ValueError, "Unknown line_type in spec file."

        specfile_data.append(entry)

    ifp.close()

    print_verbose("Load metadata spec file: Complete", program_options)

    return specfile_data


