#!/usr/bin/env python
"""
tz_utils.py

TODO: Add some example usage cases.
"""
from datetime import date
from datetime import datetime
from datetime import tzinfo
from datetime import timedelta


class Zone(tzinfo):
    """
    Simple class to help with converting timezones for datefields.

    Attribution:
        Source: http://stackoverflow.com/questions/4770297/python-convert-utc-datetime-string-to-local-datetime
    """
    def __init__(self,offset,isdst,name):
        self.offset = float(offset)
        self.isdst = isdst
        self.name = name

    def utcoffset(self, dt):
        return timedelta(hours=self.offset) + self.dst(dt)

    def dst(self, dt):
        return timedelta(hours=1) if self.isdst else timedelta(0)

    def tzname(self,dt):
        return self.name


