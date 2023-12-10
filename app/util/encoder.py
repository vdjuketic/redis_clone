import struct


def encode_string(str):
    length = struct.pack(">H", len(str))
    return length + str.encode()


def encode_list(list):
    encoded = f"{len(list)}\r\n"
    for string in list:
        encoded += f"${len(string)}\r\n{string}\r\n"

    return encoded
