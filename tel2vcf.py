import os
import struct
import quopri

src_file = "dump.tel"
out_file = "dump.vcf"


def read_int(fp):
    return struct.unpack("i", fp.read(4))[0]


def read_string(buffer):
    chars = []
    for byte in buffer:
        if byte == 0x0:
            return "".join(chars)
        chars.append(chr(byte))
    return "".join(chars)


def start(src, dst):
    header = b'\xff\xff\xff\xff'

    cwd = os.getcwd()
    src = open(cwd + "/" + src, "rb")
    dst = open(cwd + "/" + dst, "w")

    buf = src.read(len(header))
    if buf != header:
        print("Invalid header")
        exit(0)
    count = struct.unpack("i", src.read(4))[0]
    if count < 1:
        print("Nothing to read")
        exit(0)

    total = 0
    while total < count:
        total += 1
        length = read_int(src)  # 0x18 - ???
        src.read(length - 4)
        length = read_int(src)  # 0x04 - ???
        if length == 4:
            src.read(length)
            length = read_int(src)  # 0x10 - contact name
            name = src.read(length).decode('cp1251')
            read_int(src)  # 0x00 - ???
            length = read_int(src)  # 0x0C - phone number
            phone = read_string(src.read(length))

            print(f"{total:3}: {name:22} {phone}")

            charset = ""
            if not all(ord(c) < 128 for c in name):
                charset = ";CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE"
                name = quopri.encodestring(name.encode("utf-8"), True).decode()

            dst.write("BEGIN:VCARD\n")
            dst.write("VERSION:2.1\n")
            dst.write(f"N{charset}:;{name};;;\n")
            dst.write(f"FN{charset}:{name}\n")
            dst.write(f"TEL;CELL:{phone}\n")
            dst.write("END:VCARD\n")

    src.close()
    dst.close()


if __name__ == '__main__':
    start(src_file, out_file)
