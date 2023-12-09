import struct
from enum import Enum, auto


class ALT_STRING_ENCODING(str, Enum):
    LENGTH_PREFIXED = auto()
    INT_8 = auto()
    INT_16 = auto()
    INT_32 = auto()
    LZF_COMPRESSED = auto()


def decode_string_from_file(file):
    length = unsigned_char(file)
    return file.read(length)


def unsigned_char(file):
    return struct.unpack("B", file.read(1))[0]


def unsigned_int(f):
    return struct.unpack("I", f.read(4))[0]


def unsigned_short(f) -> int:
    return struct.unpack("H", f.read(2))[0]


"""
dark voodoo
https://rdb.fnordig.de/file_format.html#length-encoding
"""


def read_length_encoding(file) -> tuple[len, ALT_STRING_ENCODING]:
    first_byte = unsigned_char(file)
    match first_byte:
        case x if x >> 6 == 0b00:
            # String. Last 6 bits are length
            return (first_byte & 0b00111111, ALT_STRING_ENCODING.LENGTH_PREFIXED)
        case x if x >> 6 == 0b01:
            # String, The last 6 bits + next 8 bits combined are the value
            next_byte = unsigned_char(file)
            rest = first_byte & 0b00111111
            return (rest << 8 | next_byte, ALT_STRING_ENCODING.LENGTH_PREFIXED)
        case x if x >> 6 == 0b10:
            # String. Discard the last 6 bits. Next 4 bytes are value
            return (unsigned_int(file), ALT_STRING_ENCODING.LENGTH_PREFIXED)
        case 0b11000000:
            return (1, ALT_STRING_ENCODING.INT_8)
        case 0b11000001:
            return (2, ALT_STRING_ENCODING.INT_16)
        case 0b11000010:
            return (4, ALT_STRING_ENCODING.INT_32)
        case 0b11000011:
            raise NotImplementedError("LZF compression not implemented")
        case _:
            raise ValueError(f"Unknown string encoding: {bin(first_byte)}")


def read_string(file) -> str | int:
    length, str_fmt = read_length_encoding(file)
    match str_fmt:
        case ALT_STRING_ENCODING.INT_8:
            return unsigned_char(file)
        case ALT_STRING_ENCODING.INT_16:
            return unsigned_short(file)
        case ALT_STRING_ENCODING.INT_32:
            return unsigned_int(file)
        case ALT_STRING_ENCODING.LZF_COMPRESSED:
            raise NotImplementedError("LZF compression not implemented")
        case _:
            return file.read(length).decode("ascii")
