#!/usr/bin/env python
"""
Todo:
    - Add method documentation.
"""
import copy
import csv
import os
import os.path
import sys
import shutil

from datetime import datetime
from datetime import tzinfo
from datetime import timedelta

from tz_utils import Zone




class csv_data(object):
    """
    CSV Data Class
    """

    def __init__(self, delimiter=",", first_row_is_header=True, ignore_empty_lines=True, comment_char="#"):
        """
        Default constructor.

        Args:
            delimiter (str): The character (or string) delimiter for each column.  Default=","
            first_row_is_header (bool): If True then the first row is interpreted as the header row,
                                        If False then we interpret the first row as data and number
                                        rows from 1 .. N.  Default=True
            ignore_empty_lines (bool): Ignore empty (blank) lines from the input file and treat them as
                                       comments. Default=True
            comment_char (str): Lines starting with this character in column 0 are treated as comments.
                                Default="#"

        Todo:
            - Change comment_char to comment_prefix and make it a regex expressoin that's matched at the start
              of a line.
        """
        self.column_headers      = None
        self.column_data         = {}
        self.first_row_is_header = first_row_is_header
        self.ignore_empty_lines  = ignore_empty_lines
        self.comment_char        = comment_char
        self.delimiter           = delimiter
        self.num_rows            = 0
        self.filename            = None

        if (self.comment_char is not None) and ((not isinstance(self.comment_char,str)) or (len(comment_char) > 1)):
            raise StandardError, "comment_char can be None or a string of length 1."

        if not isinstance(self.delimiter, str):
            raise StandardError, "delimiter must be a string."

        return None


    def get_num_rows(self):
        """
        Returns:
            int: number of rows in the CSV file that have been loaded.
        """
        return self.num_rows


    def load_csv(self, filename):
        """
        Load the CSV file.

        [column_name_1, column_name_2, ... column_name_n]
        {"column_name_1": [data_row_1, data_row_2, ... data_row_m]
        """

        self.filename = filename

        if self.first_row_is_header is False:
            raise NotImplementedError, "First row must be a header."

        # dictreader does not give me the actual line, so we need to scan through the file
        # and pick out the lines to skip (i.e., commented lines)
        lines_to_skip = []
        with open(filename, 'rb') as csvfile:
            row_num = 1
            for row in csvfile:
                if row[0] == self.comment_char:
                    lines_to_skip.append(row_num)
                row_num += 1

        # read the file in via the dictreader
        with open(filename, 'rb') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=None, restkey=None, restval=None, dialect='excel')
            self.column_headers = copy.deepcopy(reader.fieldnames)
            num_rows = 0
            for row in reader:
                if not reader.line_num in lines_to_skip:
                    num_rows += 1
                    for k,v in row.iteritems():
                        if not self.column_data.has_key(k):
                            if num_rows > 1:
                                raise IOError, "new keys should only show up on row 1"
                            self.column_data[k] = []
                        self.column_data[k].append(v)

            self.num_rows = num_rows

        return None


    def get_filename(self):
        """
        Return the filename of the CSV file.

        Returns:
            str: The filename of the CSV file.
        """
        return self.filename


    def write_csv(self, filename):
        """
        Write out the data into a delimited file, using the delimiter specified in the c'tor.

        Args:
            filename (str): The filename of the file to write to.

        Returns:
            int: number of rows written

        Todo:
            - Add (no)overwrite option and checking to make sure path exists and is writable, etc.
              with appropriate errors if fails.
        """
        rows_written = 0
        ofp = open(filename, "w")

        if self.first_row_is_header is True:
            ofp.write(self.delimiter.join(self.column_headers) + "\n")
            rows_written += 1

        for row in self.iterrows():
            ofp.write(self.delimiter.join(row) + "\n")
            rows_written += 1

        ofp.close()

        return rows_written


    def append_csvfile(self, filename):
        """
        Append another CSV file with identical column headers into this CSV data.
        Column labels must be identical and in the same ordering.

        Args:
            filename (str): The filename of the file to append content to.

        Returns:
            bool: True if success.  False if not successful.

        Todo:
            - Add file / permissions checking and raise appropriate errors if fails.
            - Make 'debuggable'
        """
        if not os.path.isfile(filename):
            msg = "ERROR: input file not found: %s"%(filename)
            raise IOError, msg

        data_csv = csv_data(delimiter=self.delimiter,
                            first_row_is_header=self.first_row_is_header,
                            ignore_empty_lines=self.ignore_empty_lines,
                            comment_char=self.comment_char)
        data_csv.load_csv(filename)

        #print "CSV"
        #self.PrettyPrintHorizontal(delimiter="\t", max_rows_to_print=30, indent=4)
        #print ""

        #print "CSV-NEW"
        #data_csv.PrettyPrintHorizontal(delimiter="\t", max_rows_to_print=30, indent=4)
        #print ""

        # Check columns
        csv1_headers = self.get_column_headers()
        csv2_headers = data_csv.get_column_headers()

        if len(csv1_headers) != len(csv2_headers):
            print "ERROR: Append failed due to different # of columns."
            return False

        for colidx in xrange(len(csv1_headers)):
            if csv1_headers[colidx] != csv2_headers[colidx]:
                print "ERROR: Column label mismatch: %s:%s <> %s:%s"%(self.filename, csv1_headers[colidx], filename, csv2_headers[colidx])
                return False

        # If we've made it here, then the two files have
        #    (a) same # of columns
        #    (b) columns are named the same.
        # So, we can append the files now.
        for csv2_row_data in data_csv.iterrows_dict():
            self.append_row(csv2_row_data)

        return True


    def get_column_headers(self):
        """
        Todo:
            - Add method documentation.
        """
        return self.column_headers


    def get_num_columns(self):
        """
        Returns:
            int: Number of columns in the dataset.
        """
        return len(self.column_headers)


    def iterrows(self):
        """
        Iterator over rows.
        Yields: [ col1_data, col2_data, ... , colN_data ]
        Column order matches that in column_headers.
        """
        for rowidx in range(self.num_rows):
            yield self.get_row(rowidx)
        raise StopIteration()


    def iterrows_dict(self):
        """
        Iterator over rows.
        Yields: { column_name1: value, column_name2: value, ..., column_nameN: value }
        """
        for rowidx in range(self.num_rows):
            yield self.get_row_dict(rowidx)
        raise StopIteration()


    def get_row(self, rowidx):
        """
        returns row as a list.
        rowidx is 0..N-1.
        order matches the order of column_headers.
        """
        if (self.num_rows < 1) or (rowidx > self.num_rows-1):
            raise IndexError, "Invalid row index (%d), valid size range is [0,%d]"%(rowidx, self.num_rows-1)

        row = []
        for colhdr in self.column_headers:
            row.append( self.column_data[colhdr][rowidx])

        return row


    def get_row_dict(self, rowidx):
        """
        return row as a dict.
        """
        if (self.num_rows < 1) or (rowidx > self.num_rows-1):
            raise IndexError, "Invalid row index (%d), valid size range is [0, %d]"%(rowidx, self.num_rows-1)
        row = {}
        for colhdr in self.column_headers:
            row[colhdr] = self.column_data[colhdr][rowidx]
        return row


    def convert_column_timezone(self, column_src_lbl, column_dst_lbl, old_tz_offset, new_tz_offset, delete_old_column=False):
        """
        Todo:
            - Add full description of method.
        """

        new_column_data = []

        old_tz_offset = float(old_tz_offset)
        new_tz_offset = float(new_tz_offset)

        tz_src = Zone(old_tz_offset, False, 'OldTZ')
        tz_dst = Zone(new_tz_offset, False, 'NewTZ')

        for old_date in self.column_data[column_src_lbl]:

            old_date_tz = None
            try:
                old_date_tz = datetime.strptime(old_date, "%Y-%m-%dT%H:%M:%S")
            except ValueError, msg:
                _msg =  "Unable to convert datetime field '%s' using expected format: 'yyyy-mm-ddThh:mm:ss'\n"%(old_date)
                _msg += msg
                raise ValueError, _msg
            old_date_tz = old_date_tz.replace(tzinfo=tz_src)

            new_date_tz = old_date_tz.astimezone(tz_dst)

            new_date_str = new_date_tz.__format__("%Y-%m-%dT%H:%M:%S")
            new_column_data.append(new_date_str)

        self.column_headers.insert(self.column_headers.index(column_src_lbl)+1, column_dst_lbl)
        self.column_data[column_dst_lbl] = new_column_data

        if delete_old_column is True:
            self.delete_column(column_src_lbl)

        return None


    def append_const_column(self, column_lbl, column_data):
        """
        Append a new const column.
        """

        # if data has no defined header, use N (note, column numbers in header are 1..N)
        if self.first_row_is_header is not True:
            column_lbl = self.get_num_columns()+1
            while column_lbl in self.column_headers():
                column_lbl += 1

        self.column_headers.append(column_lbl)
        self.column_data[column_lbl] = [column_data for x in range(self.num_rows)]

        return None


    def append_column(self, column_data, column_lbl=None):
        """
        Append data in a new column.

        column_lbl : Label
        column_data: [row1, row2, row3, ... rowN]
        """

        # if data has no defined header, use N (note, column numbers in header are 1..N)
        if self.first_row_is_header is not True:
            column_lbl = self.get_num_columns()+1
        elif column_lbl is None:
            column_lbl = self.get_num_columns()
            while column_lbl in self.column_headers():
                column_lbl += 1

        # if there is data already, we sould make sure the length is ok
        if len(self.column_data)>0:
            if len(column_data) != len(self.num_rows):
                raise IndexError, "new column rows != existing data rows."

        # otherwise, there is no data, so we should set the number of rows.
        else:
            self.num_rows = len(column_data)

        self.column_headers.append(column_lbl)
        self.column_data[column_lbl] = copy.deepcopy(column_data)

        return None


    def append_row(self, row_data):
        """
        Add a new row to the data set.

        row_data:  {column_name1: value, column_name2: value, ..., column_nameN: value }
        """

        # 1) if there's no data, then we're setting the column names, etc.
        if self.column_headers is None:
            self.column_headers = []

        if len(self.column_headers)==0:
            for k,v in row_data.iteritems():
                self.column_headers.append(k)
                self.column_data[k] = [ str(v) ]

        # 2) if there is data, we should add a range check.
        else:
            if len(self.column_headers) != len(row_data):
                raise IndexError, "Wrong number of columns on append_row.\n" + \
                      "Expected %d but got %d."%(len(self.column_headers), len(row_data))
            for k,v in row_data.iteritems():
                self.column_data[k].append(str(v))

        self.num_rows += 1

        return None


    def has_column(self, column_lbl):
        """
        Todo:
            - Add method documentation.
        """
        return column_lbl in self.column_headers


    def rename_column_if_exists(self, column_src_lbl, column_dst_lbl):
        """
        Todo:
            - Add method documentation.
        """
        if not self.has_column(column_src_lbl):
            return False

        self.column_data[column_dst_lbl] = self.column_data.pop(column_src_lbl)
        hdridx = self.get_column_index(column_src_lbl)
        self.column_headers[hdridx] = column_dst_lbl
        return True


    def replace_str_in_headers(self, old_str, new_str):
        """
        Todo:
            - Add method documentation.
        """
        if self.first_row_is_header is not True:
            return None

        for idx in range(len(self.column_headers)):

            old_header = self.column_headers[idx]
            new_header = old_header.replace(old_str, new_str)

            if old_header != new_header:
                self.column_headers[idx] = new_header
                self.column_data[new_header] = self.column_data.pop(old_header)

        return True


    def replace_str_in_data(self, old_str, new_str, column=None, column_idx=None):
        """
        Todo:
            - Add method documentation.
        """
        for key in self.column_data.keys():
            for idx in range(len(self.column_data[key])):
                old = self.column_data[key][idx]
                new = old.replace(old_str,new_str)
                if old != new:
                    self.column_data[key][idx] = new

        return True


    def get_column_index(self, column_lbl):
        """
        Return the index of a column given a label.
        """
        if not self.has_column(column_lbl):
            print "%s was not found in the list of column headers."%(column_lbl)
            print "Acceptable Values:"
            for h in self.column_headers:
                print "\t'%s'"%(h)
            raise IndexError
        return self.column_headers.index(column_lbl)


    def delete_column(self, column_lbl):
        """
        Todo:
            - Add method documentation.
        """
        #idx = self.column_headers.index(column_lbl)
        idx = self.get_column_index(column_lbl)
        del self.column_headers[idx]
        del self.column_data[column_lbl]

        return None


    def PrettyPrint(self, delimiter="\t", max_rows_to_print=None, indent=0):
        """
        Todo:
            - Add method documentation.
        """
        row_idx = 0

        if self.column_headers is None:
            return None

        if self.first_row_is_header is True:
            print " "*indent + delimiter.join(self.column_headers)

        for row in self.iterrows():
            if max_rows_to_print is not None and row_idx >= max_rows_to_print:
                print " "*indent + "<more>"
                break

            row_idx += 1
            print " "*indent + delimiter.join(row)

        return None


    def PrettyPrintHorizontal(self, delimiter="\t", max_rows_to_print=1, indent=0):
        """
        Todo:
            - Add method documentation.
        """
        if not isinstance(max_rows_to_print, int):
            max_rows_to_print = 1
        if max_rows_to_print < 0:
            max_rows_to_print = 0

        try:
            delimiter = str(delimiter)
        except:
            raise TypeError, "Delimiter must be a string, or convertible to a string."

        max_hdr_len = 0
        for hdr in self.column_headers:
            max_hdr_len = max(max_hdr_len, len(hdr))

        for hdr in self.column_headers:
            data = self.column_data[hdr]
            print " "*indent + "%s:\t"%(hdr.ljust(max_hdr_len)),
            print delimiter.join(data[:max_rows_to_print])

        return None



