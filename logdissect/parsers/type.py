# MIT License
# 
# Copyright (c) 2017 Dan Persons <dpersonsdev@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import re
from datetime import datetime
import time
import gzip
from logdissect.data import LogEntry
from logdissect.data import LogData
import logdissect.parsers.utils

class ParseModule:
    def __init__(self, options=[]):
        """Initialize a log parsing module"""
        self.name = ''
        self.desc = ''
        self.date_format = None
        self.fields = []
        self.backup_date_format = None
        self.backup_fields = []
        self.tzone = None
        # Options to convert datestamp: standard, iso
        # Set to None to skip conversion
        self.datestamp_type = 'standard'


    def parse_file(self, sourcepath):
        """Parse a file into a LogData object"""
        # Get regex objects:
        self.date_regex = re.compile(
                r'{}'.format(self.date_format))
        if self.backup_date_format:
            self.backup_date_regex = re.compile(
                    r'{}'.format(self.backup_date_format))
        data = LogData()
        data.parser = self.name
        current_entry = LogEntry()
        data.source_path = sourcepath
        data.source_file = data.source_path.split('/')[-1]

        # Set our start year:
        data.source_file_mtime = \
                os.path.getmtime(data.source_path)
        timestamp = datetime.fromtimestamp(data.source_file_mtime)
        data.source_file_year = timestamp.year
        entryyear = timestamp.year
        currentmonth = '99'

        # Set our timezone
        if not self.tzone:
            self.tzone = util.get_tzone()

        # Parsing works in reverse. This helps with multi-line entries,
        # and logs that span multiple years (December to January shift).

        # Get our lines:
        fparts = sourcepath.split('.')
        if fparts[-1] == 'gz':
            with gzip.open(str(sourcepath), 'r') as logfile:
                loglines = reversed(logfile.readlines())
        else:
            with open(str(data.source_path), 'r') as logfile:
                loglines = reversed(logfile.readlines())

        # Parse our lines:
        for line in loglines:
            ourline = line.rstrip()

            # Send the line to self.parse_line
            entry = self.parse_line(ourline)

            if entry:
                current_entry = LogEntry()

                # Check for Dec-Jan jump and set the year:
                if int(entry['month']) > int(currentmonth):
                    entryyear = entryyear - 1
                    currentmonth = entry['month']

                # Set our attributes:
                current_entry.parser = entry['parser']
                current_entry.raw_text = ourline
                current_entry.date_stamp = entry['date_stamp']
                current_entry.numeric_date_stamp = str(entryyear) \
                        + entry['month'] + entry['day'] + entry['tstamp']
                current_entry.year = str(entryyear)
                current_entry.month = entry['month']
                current_entry.day = entry['day']
                current_entry.tstamp = entry['tstamp']
                current_entry.tzone = entry['tzone']
                current_entry._utc_date()
                current_entry.raw_stamp = entry['raw_stamp']
                current_entry.message = entry['message']
                current_entry.source_host = entry['source_host']
                current_entry.source_process = entry['source_process']
                current_entry.source_pid = entry['source_pid']
                current_entry.source_path = \
                        data.source_path
            
            
                # Append and reset current_entry
                data.entries.append(current_entry)

            else:
                continue

        # Write the entries to the log object
        data.entries.reverse()
        return data


    def parse_line(self, line):
        """Parse a line into a dictionary"""
        match = re.findall(self.date_regex, line)
        if match:
            fields = self.fields
        elif self.backup_date_regex and not match:
            match = re.findall(self.backup_date_regex, line)
            fields = self.backup_fields

        if match:
            entry = logdissect.parsers.utils.get_blank_entry()

            matchlist = list(zip(fields, match[0]))
            for f, v in matchlist:
                entry[f] = v

            if entry['date_stamp']:
                if self.datestamp_type == 'standard':
                    entry = logdissect.parsers.utils.convert_standard_datestamp(entry)
                elif self.datestamp_type == 'iso':
                    entry = logdissect.parsers.utils.convert_iso_datestamp(entry)
            
            return entry

        else:
            return None
