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
import datetime
from logdissect.parsers.type import ParseModule as OurModule
from logdissect.data.data import LogEntry
from logdissect.data.data import LogData

class ParseModule(OurModule):
    def __init__(self, options):
        self.name = 'syslog'
        self.desc = 'Syslog parsing module'
        self.data = LogData()
        self.date_format = re.compile(r"^([A-Z][a-z]{2} \d{1,2} \d{2} \d{2}:\d{2}:\d{2})")

    def run_parse(self):
	current_entry = LogEntry()
        self.data.source_file_mtime = \
                os.path.getmtime(self.data.source_full_path)
        time_list = datetime.datetime.fromtimestamp(self.data.source_file_mtime)
        # self.data.source_file_time = str(time_list[0]) + \
        #         str(time_list[1]).zfill(2) + str(time_list[2]).zfill(2) + \
        #         str(time_list[3]) + str(time_list[4]) + str(time_list[5])
        self.data.source_file_year = time_list[0]
        #To Do: strip year out of mtime
        entry_year = self.data.source_file_year
        recent_date_stamp = None
        
        # To Do: add some detection to fill in LogData class vars
        
        self.data.source_file_mtime = os.path.getmtime(source_full_path)
        self.data.source_file = self.source_full_path.split('/')[-1]
	with open(str(self.data.source_full_path), 'r') as logfile:
            self.data.lines = logfile.readlines()
            loglines = reversed(self.data.lines)
            for line in loglines:
                line = line.rstrip()
                current_entry.raw_text = line + '\n' + current_entry.raw_text
                match = re.match(self.date_format, line)
                if match:
                    date_list = str(match.split(' '))
                    months = {'Jan':'01', 'Feb':'02', 'Mar':'03', \
                            'Apr':'04', 'May':'05', 'Jun':'06', \
                            'Jul':'07', 'Aug':'08', 'Sep':'09', \
                            'Oce':'10', 'Nov':'11', 'Dec':'12'}
                    if date in months:
                        int_month = months[date]
                    date = str(date).zfill(2)
                    time_list = str(date_list[2].split(':'))
                    date_stamp = str(int_month) + str(date) + \
                            str(time_list[0]) + str(time_list[1]) + \
                            str(time_list[2])
                    # Check for Dec-Jan
                    if int(date_stamp) > recent_date_stamp:
                        entry_year = entry_year - 1
                    recent_date_stamp = int(date_stamp)
                    # Date_stamp should be called as an integer
                    current_entry.date_stamp = int(date_stamp)
                    current_entry.date_stamp_year = int(str(entry_year) \
                            + str(current_entry.date_stamp))
                    self.data.entries.append(current_entry)
        
        # Write the entries to the log object
        self.data.entries = reversed(self.data.entries)
        # Set the date range properties for the log
        self.data.first_date_stamp = self.data.entries[0].date_stamp
        self.data.first_date_stamp_year = self.data.entries[0].date_stamp_year
        self.data.last_date_stamp = self.data.entries[0].date_stamp
        self.data.last_date_stamp_year = self.data.entries[0].date_stamp_year
        return self.data
