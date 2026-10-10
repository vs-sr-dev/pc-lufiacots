# The data formats, at a glance

Read from the extracted files (`build/extract`, `build/mcd`) with
`tools/mcd.py` and ndskit; what is only a guess is marked *inferred*.

```sh
python tools/mcd.py build/extract --list                 # every member: index, UID, offset, size, wrapper, name
python tools/mcd.py build/extract --scan --extract build/mcd
python -m ndskit.sdat build/extract/sound/sound_data_us.sdat --list
python -m ndskit.sdat build/extract/sound/bgm_sound_data.sdat --waves
```

## mcd.dat, the game's archive

Nearly everything is one archive of 11 386 members, `mcd.dat`, with its
index in two other files (`tools/mcd.py` reads them; its docstring has
the layouts):

* `mcd_compact.bin`, "NLCM": the members' sizes and their offsets in
  `mcd.dat` (32-byte aligned, in order, none overlapping), and the
  archive's path on the developers' machine, `..\..\rom\mcd.dat`.
* `mcd_path.bin`: the members' names, in the same order, with their
  directories (`2d/bustup/talk_f_albert_angry.ncer`, `model/map/
  MAP_D01_12/objarrange.arrange`, `scr/txt/mclua/MAP_VOID.scr`).
* `file_uid.bin`: a table of 14 810 halfwords from a UID to a member
  (0xFFFF where a UID has no file); 11 386 UIDs used, each member once.

**Every member parses**: 11 386, none failed; 351 are empty (size 0: the
ending's staff pictures in `2d/ending/`, the Japanese
`text/ResourceText.bin`, some textures). A member is stored plain (6 552)
or wrapped (4 483): "$FAB", then a BIOS compression header (type in the
low byte, size in the top 24 bits), then the data:

| Wrapper type | Members | |
|---|---|---|
| 0x11, LZ11 | 3 091 | |
| 0x30, RLE | 517 | |
| 0x00, stored | 469 | the size, then the bytes as they are |
| **0x28, Huffman of bytes** | 406 | new in ndskit's `lz` this session |

Checked: each wrapped member decodes to its stated size within its record,
and each of the 7 168 SDK files among the members (G2D, G3D, SDAT) has its
own size field equal to its length after unwrapping.

What the members are, by name and by their first bytes once unwrapped
(`--scan`):

| Kind | Members | Magic | What |
|---|---|---|---|
| `.nsbmd` | 968 | BMD0 | models (NSBMD) |
| `.nsbtx` | 795 (+25 empty) | BTX0 | textures |
| `.nsbca` | 2 733 | BCA0 | skeletal animations |
| `.nsbta`, `.nsbma`, `.nsbva` | 295, 238, 8 | BTA0, BMA0, BVA0 | texture SRT, material and visibility animations |
| `.ncgr`, `.nclr`, `.ncer`, `.nscr`, `.nanr` | 846, 408, 697, 152, 20 (+318 empty) | RGCN, RLCN, RECN, RCSN, RNAN | the SDK's G2D: the busts of the dialogues (`2d/bustup`, 687), the menus, the minimap, the world map, the ending, the tutorials |
| `.nftr` | 4 (+1 empty) | RTFN | fonts |
| `.bpc` | 229 | BMEA | effects (*inferred*: particle emitters; with 622 textures and models in `effect/`) |
| `.xab` | 33 | XAF0 | cameras of the events (`camera/CAM_SCN03_01_01.xab`, `INTRO_C01_01_01.xab`) |
| `.scr` (911), `.man` (130), `.mobaselua` (79), `.luab` (1) | 1 121 | `\x1bLuaQ` | **Lua 5.1 bytecode** (below) |
| `.dat` | 1 666 | - | tables (enemies, attacks, missiles, map data) |
| `.mot`, `.cambin`, `.modatabin`, `.arrange`, `.mevdatabin`, `.medatabin`, `.sanim`, ... | ~700 | - | the maps' objects, events and cameras, motion lists, screen animations |
| `.bin` | 141 | "PACK", "icon", "text", "face", "back", ... | the menus' layouts (`data/menu/`), the character list |
| `.sdat` | 1 | SDAT | `sound/bgm_sound_data.sdat`, the same bytes as the cartridge's file |

By directory: `model/` 4 522 members (`model/map/` 4 123: 251 map
folders such as `MAP_D01_12`), `2d/` 2 541, `motion/` 2 463, `scr/` 889,
`effect/` 622, `data/` 173, `cg/` 134, `camera/` 31, `font/` 5. The 3D is
the SDK's G3D as it is, not wrapped: a renderer that implements the DS's
geometry and rendering engines draws it without knowing the game's
formats, as with Moon and Nostalgia.

## Lua

The game's logic is partly **Lua 5.1**: 1 121 members are bytecode
("\x1bLuaQ", format 0, little-endian, 4-byte int, size_t and instruction,
**4-byte integral numbers**: a Lua built with `lua_Number` an int32), and
`scr/lua_copyright.dat` is the string "$Lua: Lua 5.1.4 Copyright (C)
1994-2008 Lua.org, PUC-Rio $". The scripts are the maps (`scr/txt/
mclua/MAP_*.scr`, `scr/map/`), the scenes (`scr/scene/`, 363, with
`SceneDef.bin`), the bosses (`scr/boss/`), the enemies' action
definitions (`data/enemy/ActionDef.scr`). *Inferred*: the Lua VM is in the
ARM9 program (its strings and tables to find); for the port it is just
code that the recompiler translates with the rest.

## Text

`text/ResourceText_us.bin` (70 359 bytes) and `scr/scenariotext_us.bin`
(936 551) are big-endian "FORM" files ("SIGN" "TEXT RESOURCE 2009/11/09
23:50", then "SLST", "RLST", "DIAG" chunks, an offset table) whose strings
are **UTF-16 big-endian** ("Are you going to the Three Towers? Yes, there
is no other way to..."). The Japanese `text/ResourceText.bin` is empty in
this release; `2d/localize/us/` holds the English pictures (the staff
roll among them) and `localize/filelist.bin` a list (*inferred*: of what
the localisation replaces).

## Sound

Two SDATs (`python -m ndskit.sdat FILE --list`, `--waves`):

| Archive | Records | Waves | Instruments |
|---|---|---|---|
| `bgm_sound_data.sdat` (2.1 MB, the music) | 94 sequences (`SEQ_BGM01`-`47` and a `_S` variant of each), 46 banks, 1 wave archive, 1 player | **133, all IMA-ADPCM** (87 looped); rates 32 000, 32 768, 32 728, 33 573, 44 100 Hz... | 249 PCM programs, 39 key splits, 32 drum sets, **10 PSG**: 978 sampled and 10 PSG instruments |
| `sound_data_us.sdat` (13.3 MB, the effects and the voices) | 194 sequences, 1 sequence archive (`SEQ_SE`, 9), 164 banks, 6 wave archives, 1 group, players `PLAYER_BGM`, `PLAYER_SE` (5 sequences), `PLAYER_SEQ_VOICE`; **3 stream players** (`PLAYER_STRM1`-`3`, on channels 6, 7, 8) and **644 streams** | 192, all IMA-ADPCM (16 364 Hz mostly) | 316 PCM, **7 PSG, 1 noise** |

**The voices are streams**: 644 STRMs, mono, 23 min 26 s in all:

| Name | Streams | What (*inferred* from the names) |
|---|---|---|
| `evt###_NAME` | 354 | the events' lines |
| `btl_XXXn_NAME` | 140 | battle cries (ATK1-5, CA, CHEER, CHG, CWS, DMG, EX, GUTS, JUMP, SP, WEAK, WS) for each party member |
| `talk##_n_NAME` | 92 | the party's talks |
| `se###` | 44 | effects as streams |
| `wmap##_LEXUS` | 14 | Lexis on the world map |

By speaker: MAXIM 107, TEAR 81, SELENA 70, GUY 64, IRIS 50, HEIDEGGER
47, GADES 33, ARTY 31, IDURA 26, LEXUS and GEMINE 19, JIMMY 18, DIOS and
AMON 13, MILKA 5. Formats: 584 IMA-ADPCM at 12 467 Hz, 16 ADPCM at
32 728 Hz, 38 PCM8 at 16 364 or 32 728 Hz (6 of them looped).

Moon and Nostalgia had no streams: the SDK's stream player (on the ARM9
it reads the stream from the cartridge into a buffer that a channel
plays in a loop) is new for ndskit's runtime, and its timing depends on
the cartridge's time (`06-attack-plan.md`). In melonDS's state during
the opening (VBlank 5 806, Gades speaking), channels 1 and 3 play PCM16 in
a loop at 32 728 Hz, one panned fully left and one fully right, over
0x600 words: *inferred*, a stereo buffer the ARM9 fills.

## Movies

None: no Mobiclip or other video file. The opening is the game's own 3D
with G2D overlays.
