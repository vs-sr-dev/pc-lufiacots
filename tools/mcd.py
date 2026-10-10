"""Lufia: Curse of the Sinistrals' archive: mcd.dat, its index (mcd_compact.bin) and names (mcd_path.bin).

    python tools/mcd.py build/extract --list               # every member: index, UID, offset, size, wrapper, name
    python tools/mcd.py build/extract --scan               # members by extension and kind, every wrapper undone
    python tools/mcd.py build/extract --extract build/mcd  # every member, unwrapped, under its own name

The directory is the cartridge's extracted root (`ndskit.rom --extract`).

mcd_compact.bin ("NLCM"):

    0x00  "NLCM"
    0x04  u32 0x38, where the sizes start
    0x08  u32 where the offsets start (0x38 + 4 x count)
    0x0C  u32 count (11 386)
    0x10  u32 1, the number of archives (*inferred*)
    0x14  char[0x24] the archive's path on the developers' machine, "..\\..\\rom\\mcd.dat"
    0x38  u32 size[count], u32 offset[count] (offsets into mcd.dat, 32-byte aligned)

mcd_path.bin: u32 count, u32 offset[count] (into this file), then the
names, NUL-terminated, in the same order ("2d/bustup/talk_f_albert_angry.ncer").

file_uid.bin: u16 member[14 810], indexed by a file's UID (*inferred*:
the number the game's data uses for a file): the member's index, 0xFFFF
for a UID with no file. 11 386 UIDs are used, each member once (UID 1 is
model/PC01.nsbmd).

A member of mcd.dat is stored plain (the SDK's G2D and G3D files, Lua
bytecode, tables), or wrapped: "$FAB", then a word whose low byte is a
BIOS compression type and whose top 24 bits are the size (0x00: stored
as is; 0x11 LZ11; 0x28 Huffman of bytes; 0x30 RLE), then the data.
351 members have a size of 0 (the ending's staff pictures among them).
"""
import argparse
import collections
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from ndskit import lz  # noqa: E402


def read_index(root):
    c = open(os.path.join(root, "mcd_compact.bin"), "rb").read()
    p = open(os.path.join(root, "mcd_path.bin"), "rb").read()
    magic, sizes_at, offs_at, n = struct.unpack_from("<4sIII", c, 0)
    if magic != b"NLCM":
        raise SystemExit("mcd_compact.bin: not NLCM")
    sizes = struct.unpack_from("<%dI" % n, c, sizes_at)
    offs = struct.unpack_from("<%dI" % n, c, offs_at)
    pn = struct.unpack_from("<I", p, 0)[0]
    if pn != n:
        raise SystemExit("mcd_path.bin has %d names for %d members" % (pn, n))
    po = struct.unpack_from("<%dI" % n, p, 4)
    names = [p[o:p.index(b"\0", o)].decode("latin1") for o in po]
    return list(zip(names, offs, sizes))


def read_uids(root):
    """{member index: UID} from file_uid.bin."""
    u = open(os.path.join(root, "file_uid.bin"), "rb").read()
    table = struct.unpack("<%dH" % (len(u) // 2), u)
    return {m: uid for uid, m in enumerate(table) if m != 0xFFFF}


def unwrap(raw):
    """(the member's bytes, the wrapper's name); ValueError if a wrapper does not decode to its size."""
    if raw[:4] != b"$FAB":
        return raw, "-"
    w = struct.unpack_from("<I", raw, 4)[0]
    kind, size = w & 0xFF, w >> 8
    body = raw[4:]
    if kind == 0x00:
        if size > len(body) - 4:
            raise ValueError("stored member longer than its record")
        return body[4:4 + size], "stored"
    h = lz.header(body)
    if not h or h[0] != kind or h[1] != size:
        raise ValueError("wrapper type %02X is not a BIOS compression" % kind)
    try:
        data, end = lz.KINDS[kind](body, size, h[2])
    except (IndexError, struct.error):
        raise ValueError("wrapper type %02X runs out of input" % kind)
    if end > len(body):
        raise ValueError("wrapper type %02X ends after its record" % kind)
    return data, lz.NAMES[kind]


def magic(data):
    m = data[:4]
    if all(0x20 <= b < 0x7F for b in m):
        return m.decode()
    if m == b"\x1bLua":
        return "Lua bytecode"
    return "-"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("root", help="the cartridge's extracted files (ndskit.rom --extract)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--extract", metavar="DIR")
    a = ap.parse_args(argv)
    index = read_index(a.root)
    with open(os.path.join(a.root, "mcd.dat"), "rb") as f:
        mcd = f.read()
    if a.list:
        uids = read_uids(a.root)
        print("index    UID  offset       size  wrapper  name")
        for i, (name, off, size) in enumerate(index):
            raw = mcd[off:off + size]
            wrap = "-"
            if raw[:4] == b"$FAB":
                wrap = "$FAB %02X" % raw[4]
            print("%5d  %5d  %08X %8d  %-8s %s" % (i, uids.get(i, -1), off, size, wrap, name))
    if a.scan or a.extract:
        kinds = collections.Counter()
        wraps = collections.Counter()
        bad = 0
        for name, off, size in index:
            ext = os.path.splitext(name)[1].lower()
            if size == 0:
                kinds[(ext, "empty")] += 1
                continue
            try:
                data, wrap = unwrap(mcd[off:off + size])
            except (ValueError, IndexError) as e:
                print("%s: %s" % (name, e))
                bad += 1
                continue
            wraps[wrap] += 1
            kinds[(ext, magic(data))] += 1
            if a.extract:
                path = os.path.join(a.extract, *name.split("/"))
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "wb") as f:
                    f.write(data)
        if a.scan:
            for (ext, m), k in sorted(kinds.items()):
                print("%-12s %-14s %5d" % (ext, m, k))
            print("wrappers:", ", ".join("%s %d" % kv for kv in sorted(wraps.items())))
        print("%d members, %d failed" % (len(index), bad))


if __name__ == "__main__":
    main()
