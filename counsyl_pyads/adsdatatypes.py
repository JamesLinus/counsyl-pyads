"""Collection of utility functions for data types available in Twincat.

A documentation of Twincat data types is available at
http://infosys.beckhoff.com/content/1033/tcplccontrol/html/tcplcctrl_plc_data_types_overview.htm?id=20295  #nopep8
"""
import datetime
import struct


class AdsDatatype(object):
    """Represents a simple data type with a fixed byte count."""
    def __init__(self, byte_count, pack_format):
        self.byte_count = int(byte_count)
        self.pack_format = str(pack_format)

    def pack(self, value):
        """Pack a value using Python's struct.pack()"""
        assert(self.pack_format is not None)
        if(self.pack_format is not None):
            return struct.pack(self.pack_format, value)
        else:
            return value

    def pack_into_buffer(self, byte_buffer, offset, value):
        assert(self.pack_format is not None)
        struct.pack_into(self.pack_format, byte_buffer, offset, value)

    def unpack(self, value):
        """Unpack a value using Python's struct.unpack()"""
        assert(self.pack_format is not None)
        if(self.pack_format is not None):
            return struct.unpack(self.pack_format, value)[0]
        else:
            return value

    def unpack_from_buffer(self, byte_buffer, offset):
        assert(self.pack_format is not None)
        return struct.unpack_from(self.pack_format, byte_buffer, offset)[0]


class AdsStringDatatype(AdsDatatype):
    """Represents Twincat's variable length STRING data type."""
    def __init__(self, str_length=80):
        super(AdsStringDatatype, self).__init__(
            byte_count=str_length, pack_format='%ss' % str_length)

    def unpack(self, value):
        """Unpacks the value into a string of str_length, then strips null
        characters and white space.
        """
        value = super(AdsStringDatatype, self).unpack(value)
        return value.strip(' \t\r\n\0')

    def unpack_from_buffer(self, byte_buffer, offset):
        """c.f. unpack()"""
        value =  super(AdsStringDatatype, self).unpack_from_buffer(
            byte_buffer, offset)
        return value.strip(' \t\r\n\0')


class AdsTimeDatatype(AdsDatatype):
    """Represents Twincat's TIME data type."""
    def __init__(self):
        # DATE, TIME, and DATE_AND_TIME are all handled as WORD by Twincat
        super(AdsTimeDatatype, self).__init__(byte_count=4, pack_format='I')

    def time_to_milliseconds_integer(self, value):
        """Converts a Python datetime.time object to an integer.

        The output represents the number of milliseconds since
        datetime.time(0). Any time zone information is ignored.
        """
        assert(isinstance(value, datetime.time))
        return (
            ((value.hours * 60 + value.minutes) * 60 + value.seconds) * 1000 +
            int(value.microseconds / 1000))

    def milliseconds_integer_to_time(self, value):
        """Converts an integer into a Python datetime.time object.

        The input is assumed to represent the number of milliseconds since
        datetime.time(0). Any time zone information is ignored.
        """
        assert(isinstance(value, int))
        # pretend this is a timestamp in millisecond resolution and get the
        # datetime ignoring timezones, then discard the date component
        dt = datetime.datetime.utcfromtimestamp(value/1000.0)
        return dt.time()

    def pack(self, value):
        value = self.time_to_milliseconds_integer(value)
        return super(AdsTimeDatatype, self).pack(value)

    def pack_into_buffer(self, byte_buffer, offset, value):
        value = self.time_to_milliseconds_integer(value)
        super(AdsTimeDatatype, self).pack_into_buffer(
            byte_buffer, offset, value)

    def unpack(self, value):
        value = super(AdsTimeDatatype, self).unpack(value)
        return self.milliseconds_integer_to_time(value)

    def unpack_from_buffer(self, byte_buffer, offset):
        value =  super(AdsTimeDatatype, self).unpack_from_buffer(
            byte_buffer, offset)
        return self.milliseconds_integer_to_time(value)


class AdsDateDatatype(AdsDatatype):
    def __init__(self):
        # DATE, TIME, and DATE_AND_TIME are all handled as WORD by Twincat
        super(AdsDateDatatype, self).__init__(byte_count=4, pack_format='I')

    # contrary to what the docs say the resolution of the DATE datatype is
    # one day, not one second
    def time_to_days_integer(self, value):
        assert(isinstance(value, datetime.date))
        dt1970 = datetime.date(1970, 1, 1)
        tdelta = value - dt1970
        return tdelta.days

    def days_integer_to_time(self, value):
        assert(isinstance(value, int))
        dt1970 = datetime.date(1970, 1, 1)
        return dt1970 + datetime.date(days=value)

    def pack(self, value):
        value = self.time_to_days_integer(value)
        return super(AdsTimeDatatype, self).pack(value)

    def pack_into_buffer(self, byte_buffer, offset, value):
        value = self.time_to_days_integer(value)
        super(AdsTimeDatatype, self).pack_into_buffer(
            byte_buffer, offset, value)

    def unpack(self, value):
        value = super(AdsTimeDatatype, self).unpack(value)
        return self.days_integer_to_time(value)

    def unpack_from_buffer(self, byte_buffer, offset):
        value =  super(AdsTimeDatatype, self).unpack_from_buffer(
            byte_buffer, offset)
        return self.days_integer_to_time(value)


# TODO
class AdsDateAndTimeDatatype(AdsDatatype):
    def __init__(self):
        # DATE, TIME, and DATE_AND_TIME are all handled as WORD by Twincat
        super(AdsDateAndTimeDatatype, self).__init__(byte_count=4, pack_format='I')

    def pack(self, value):
        pass

    def pack_into_buffer(self, byte_buffer, offset, value):
        pass

    def unpack(self, value):
        pass

    def unpack_from_buffer(self, byte_buffer, offset):
        pass


BOOL = AdsDatatype(byte_count=1, pack_format='?')  # Bool
BYTE = AdsDatatype(byte_count=1, pack_format='b')  # Int8
WORD = AdsDatatype(byte_count=2, pack_format='H')  # UInt16
DWORD = AdsDatatype(byte_count=4, pack_format='I')  # UInt32
SINT = AdsDatatype(byte_count=1, pack_format='b')  # Int8 (Char)
USINT = AdsDatatype(byte_count=1, pack_format='B')  # UInt8
INT = AdsDatatype(byte_count=2, pack_format='h')  # Int16
UINT = AdsDatatype(byte_count=2, pack_format='H')  # UInt16
DINT = AdsDatatype(byte_count=4, pack_format='i')  # Int32
UDINT = AdsDatatype(byte_count=4, pack_format='I')  # UInt32
# LINT (64 Bit Integer, wird aktuell von TwinCAT nicht unterstuetzt)
# ULINT (Unsigned 64 Bit Integer, wird aktuell von TwinCAT nicht unterstuetzt)
REAL = AdsDatatype(byte_count=4, pack_format='f')  # float
LREAL = AdsDatatype(byte_count=8, pack_format='d')  # double
STRING = lambda str_length: AdsStringDatatype(str_length)
# Duration time. The most siginificant digit is one millisecond. The data type
# is handled internally like DWORD.
TIME = AdsTimeDatatype()
TIME_OF_DAY = TIME  # only semantically different from TIME
TOD = TIME_OF_DAY  # alias
DATE = AdsDateDatatype()
DATE_AND_TIME = AdsDateAndTimeDatatype()
DT = DATE_AND_TIME  #alias
