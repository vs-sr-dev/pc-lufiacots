# The cartridge

Everything here was read from the cartridge with ndskit (`python -m
ndskit.rom ROM --info`, `--list`, `--extract build/extract --nested`) and
`tools/mcd.py`, or seen running in melonDS, unless marked *inferred*.

## Identity

| Field | Value |
|---|---|
| File | `Lufia - Curse of the Sinistrals (USA).nds`, 64 MiB image, 0x03D8AD40 bytes used; SHA-1 019908480071470b8549885a87a88b17b2330cd5 |
| Title, code, maker | `ESTPOLIS DS`, `BSDE` (USA), `E9` (Natsume) |
| Unit, region, version | 0 (DS), 0, 0 |
| Header CRC, logo CRC | 0x7197, 0xCF56: both correct |
| Secure area | decrypted (the 0xE7FFDEFF marker), its CRC 0xEFC4 |
| SDK | **NitroSDK 5.3** (ModuleParams' relstep 30005); Moon and Nostalgia: 4.2 |
| Banner | version 1; every language: "Lufia: Curse / of the Sinistrals / Natsume Inc." |
| Internal name | "ESTPOLIS DS": the Japanese title (*Estpolis Denki*), in the header |

On screen (melonDS, from a new cartridge): the logos of **Square Enix**
(upper screen) and **Neverland** (lower screen) at about 6 s; then an
opening in 3D with the staff on the lower screen ("Producer Hajime
Kojima", "Main Planner Naoyuki Ukeda", "Main Programmer Yuki Tamura",
"Character Designer Yusuke Naora", "Main Designer Takanobu Tsujihata",
"Music Composer Yasunori Shiono", "Scenario and Directed by Masahide
Miyata"); then the title, whose lower screen reads "© 2010 SQUARE ENIX
CO.,LTD. All Rights Reserved / Original Works : ©TAITO CORP.1993,1995 /
Licensed to and published by Natsume Inc." No Natsume logo is shown at
the boot. The opening cannot be skipped (START, A, B, X, SELECT, L+R and
the touch screen tried, the presses seen in the game's pad state): the
title comes after about 4 minutes 20 seconds (VBlank 15 700).

## The two programs

| | ARM9 | ARM7 |
|---|---|---|
| Stored at | 0x4000, 0xD3D90 bytes | 0x12AE00, 0x26BEC bytes |
| Runs at | 0x02000000, entry 0x02000800 | 0x02380000, entry 0x02380000 |
| Compressed | **yes**: the SDK's backward LZ up to 0x020D3D90 (ModuleParams at 0x02000B88); plain, 0x15BDF8 bytes (to the end of the autoload list) | no |
| crc32 | 0x12E197C1 stored, 0x6FF424D4 plain | **0x3F0CD426** (Moon's 0x1B16DBE2, Nostalgia's 0x3DFBBAA1) |
| Static BSS | 0x02154860-0x02174140 | |
| Autoloads | ITCM 0x01FF8000 (0x7480 bytes), DTCM 0x027E0000 (0x100, BSS 0x320) | main RAM 0x027E0000 (0xBC), shared WRAM 0x037F8000 (0xE6D8, BSS 0x3FF8), **VRAM 0x06000000 (0x18150, BSS 0x1590)** |

The ARM9 decompresses itself: its crt0 passes ModuleParams' compressed
end to `MIi_UncompressBackward` (0x02000950) before the autoloads are
copied (`03-executables.md`). melonDS's direct boot and ndskit's leave it
compressed in memory, as the SDK expects.

The ARM7 is the SDK's component of a newer SDK: of its 1 058 functions,
460 are as Moon's or Nostalgia's (the same bytes elsewhere, or the same
but for branch offsets and literals; none at the same address) and 972
as those of a 2010 cartridge built with SDK 5.4 (`03-executables.md`).

**The ARM7's autoload to VRAM** (`03-executables.md`, read): its third
autoload, 0x18150 bytes linked to run at 0x06000000 (VRAM banks C/D given
to the ARM7), is the wireless driver (its code loads the addresses of the
wireless registers, 0x0480xxxx). At the boot, the ARM7's first autoload
(0xBC bytes of code at 0x027E0000) finds that entry in the autoload list
and copies the block, its BSS cleared, to **main RAM at
0x027E00BC-0x027F979C**, noting where at 0x03809198 and its size at
0x038091A0. In melonDS's states the block lies there, byte for byte, and
not in the VRAM banks: it is parked in main RAM until the wireless is
started (*inferred*: then the banks go to the ARM7 and the block is
copied there). The crt0's own copy loop also writes it to 0x06000000 at
the boot, which lands nowhere unless the banks are the ARM7's.

## Overlays

20 ARM9 overlays, none for the ARM7, **every one compressed** (the
overlay table's flag set; the SDK's backward LZ; `rom --extract` writes
each one decompressed to exactly its RAM size). They load at **five
addresses, each one the end of another overlay**: the overlays stack.

| Load address | Overlays | Size (with BSS) | Ends at |
|---|---|---|---|
| 0x02174140 (the static BSS's end) | 0 | 0x1C00 | 0x02175D40 |
| 0x02175D40 (overlay 0's end) | 1, 2, 3, 19 | 0xFB80, 0x20, 0xFE0, 0x4340 | 0x021858C0, 0x02175D60, **0x02176D20**, 0x0217A080 |
| 0x02176D20 (overlay 3's end) | 4, 7, 8 | 0x7740, 0x1BA0, 0x52A0 | **0x0217E460**, 0x021788C0, **0x0217BFC0** |
| 0x0217BFC0 (overlay 8's end) | 9-18 | 0x18E0 to 0x125A0 | up to 0x0218E560 (overlay 14) |
| 0x0217E460 (overlay 4's end) | 5, 6 | 0x6860, 0x57E0 | 0x02184CC0, 0x02183C40 |

So 0, 3, 8 and one of 9-18 can be loaded together, or 0, 3, 4 and one of
5-6; and the larger overlays cover the others' addresses at other bases
(overlay 1 runs over everything from 0x02175D40 to 0x021858C0, overlay 19
over 3's and part of 4's). Nostalgia's overlays shared two clean slots;
here an address can belong to overlays of three bases.

Which overlays are loaded, from melonDS's states (`python -m
ndskit.melonds STATE --overlays ROM`, the share of each overlay's bytes
found in memory):

| Moment | VBlank | 0x02174140 | 0x02175D40 | 0x02176D20 | others |
|---|---|---|---|---|---|
| the opening | 5 806 | 0 (58.5%) | 19 (100%) | none | none |
| the title | 15 813 | 0 (58.5%) | (19: 30%) | 4 (100%) | none |
| Soma Temple 1F, the first dungeon | 22 827, 21 692 | 0 (58.5%) | 1 (53.45%) | 4 (100%) | none |

* **Overlay 0 is always there at 58.5%**: it is loaded at the boot and its
  code is decrypted in place when it starts (an anti-piracy module,
  `03-executables.md`); 41.5% of its bytes are not what the cartridge
  holds.
* **In the dungeon, overlay 4 lies over the middle of overlay 1**: overlay
  1's 53.45% are its bytes outside overlay 4's area (64 320 - 30 528 =
  33 792 bytes, 52.5%, the rest equal by chance). Whether the game still
  runs overlay 1's code around overlay 4 is to see in the runtime.
* *Inferred* from these three moments: 19 is the opening's, 4 the title's
  and the field's, 1 the dungeon's (or the prologue's); the rest wait for
  the towns, the battles' bosses, the menus.

## File system

26 files in 2 directories: 6 named files and the 20 overlays. No
NitroROM image is nested.

| File | Bytes | What |
|---|---|---|
| `mcd.dat` | 47 195 936 | the game's archive: 11 386 members (`02-data-formats.md`) |
| `mcd_compact.bin` | 91 144 | its index ("NLCM"): each member's size and offset |
| `mcd_path.bin` | 417 476 | its members' names |
| `file_uid.bin` | 29 620 | a file's UID to its member |
| `sound/sound_data_us.sdat` | 13 319 168 | the effects and the voices (644 streams) |
| `sound/bgm_sound_data.sdat` | 2 090 816 | the music; the same bytes are also a member of `mcd.dat` |
| the 20 overlays | 333 880 stored | |

## The save

**EEPROM, 512 Kbit (64 KiB)**, read in the code: the game's save module
passes 0x1001 (`CARD_BACKUP_TYPE_EEPROM_512KBITS`, device 1, size 2^16)
to the SDK's backup functions, from 11 places (0x0205BCEC and on,
0x02060618, 0x02081EDC, 0x020B0040, ...). Once at the boot
(0x0208A46C), it locks the card, identifies the backup as 0x0D01 (an
EEPROM of 64 Kbit) and keeps whether that succeeded in a byte at
0x02158AFC, nothing reading it directly (*inferred*: a probe, possibly
the anti-piracy's).

**melonDS gives it 8 KiB**: a new save file is 8 192 bytes, and a
64 KiB file put in its place before the launch is cut back to 8 KiB (its
game list's size wins). On ndskit's runtime a new cartridge wants
`--save-size 65536`, as Nostalgia. What melonDS's smaller chip does to
the game (an EEPROM of 64 Kbit wraps addresses at 8 KiB) is an open
question (`05-open-questions.md`).
