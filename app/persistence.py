import struct
from enum import Enum
from pathlib import Path

from app.util.decoder import read_length_encoding, read_string
from app.util.encoder import encode_string

dir = ""
dbfilename = ""
enabled = False


class OP_CODE:
    EOF = 0xFF
    SELECTDB = 0xFE
    EXPIRETIME = 0xFD
    EXPIRETIMEMS = 0xFC
    RESIZEDB = 0xFB
    AUX = 0xFA


class VALUE_TYPE(int, Enum):
    STRING = 0
    LIST = 1
    SET = 2
    ZSET = 3
    HASH = 4
    ZSET_2 = 5
    MODULE = 6
    MODULE_2 = 7
    HASH_ZIPMAP = 9
    LIST_ZIPLIST = 10
    SET_INTSET = 11
    ZSET_ZIPLIST = 12
    HASH_ZIPLIST = 13
    LIST_QUICKLIST = 14
    STREAM_LISTPACKS = 15


def save_file(storage):
    if dir == "" or dbfilename == "":
        raise Exception("Initialize dir and filename first")

    with open(dbfilename) as file:
        # First line magic string REDIS
        file.write(b"REDIS")

        # Second line RDB version (v 0003)
        file.write(b"0011")

        # Auxilary field
        file.write(OP_CODE.AUX)

        # Database selector 00
        file.write(OP_CODE.SELECTDB + " 00")

        file.write(OP_CODE.RESIZEDB)
        # resize DB size
        file.write(len(storage))

        for key, value in storage.items():
            # Supporting only string values for now
            file.write(OP_CODE.STRING_ENCODING)
            file.write(encode_string(key))
            file.write(encode_string(value))

        file.write(OP_CODE.EOF)

        # TODO add checksum
        # file.write(checksum)


def read_file():
    databases = {}
    db_file = Path(dir + "/" + dbfilename)
    if not db_file.is_file():
        return None

    try:
        with open(db_file, "rb") as file:
            assert file.read(5) == b"REDIS"
            version = file.read(4)

            current_db = ""

            while True:
                op = read_unsigned_char(file)
                match op:
                    case OP_CODE.AUX:
                        key = read_string(file)
                        val = read_string(file)
                    case OP_CODE.SELECTDB:
                        current_db = read_unsigned_char(file)
                        databases[current_db] = {}
                    case OP_CODE.RESIZEDB:
                        hash_table_len = read_unsigned_char(file)
                        expire_table_len = read_unsigned_char(file)
                    case OP_CODE.EXPIRETIME:
                        raise NotImplementedError()
                    case OP_CODE.EXPIRETIMEMS:
                        raise NotImplementedError()
                    case OP_CODE.EOF:
                        # cheksum
                        checksum = read_unsigned_long(file)
                        break
                    case value_type:
                        key, value = read_key_value(value_type, file)
                        databases[current_db][key] = value

        print(f"loaded DBs from {dbfilename}")
        print(databases)
        return databases
    except FileNotFoundError as e:
        raise e


def read_unsigned_char(file):
    return struct.unpack("B", file.read(1))[0]


def read_unsigned_long(file):
    return struct.unpack("Q", file.read(8))[0]


def read_length(file):
    return read_length_encoding(file)[0]


def read_key_value(value_type, file):
    key = read_string(file)
    match value_type:
        case VALUE_TYPE.STRING:
            value = read_string(file)
        case _:
            raise NotImplementedError("Only string values suported for now")
    return key, value
