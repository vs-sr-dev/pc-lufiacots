# pc-lufiacots

A native PC port, in the making, of **Lufia: Curse of the Sinistrals**
(Nintendo DS; developed by Neverland, © 2010 Square Enix, original works
© Taito; the North American release licensed to and published by
Natsume), the action-RPG remake in 3D of the SNES's *Lufia II*: Maxim,
Selena, Guy, the Sinistrals, Doom Island. Both of the cartridge's
programs are to be recompiled statically to C++ and run on a runtime that
replaces the DS's hardware, the 3D drawn by the PC's GPU at the window's
resolution.

It is the third game of [ndskit](https://github.com/vs-sr-dev/ndskit), the game-agnostic DS toolkit born
with [pc-moon](https://github.com/vs-sr-dev/pc-moon) and proven on
[pc-nostalgia](https://github.com/vs-sr-dev/pc-nostalgia); ndskit is a git
submodule at `ndskit/`: clone with `--recursive` (or run `git submodule
update --init` after a clone).

## BYOA — Bring Your Own Assets

This repository contains **documentation and tools only**. No game data,
no executables, no assets. You need your own cartridge, dumped. The work
is done on the North American release, `Lufia - Curse of the Sinistrals
(USA).nds` (game code BSDE, version 0, NitroSDK 5.3), a 64 MiB image with
its secure area decrypted, placed in `rom/`.

## Playing it

Not yet for players: the recompiled game runs from the boot through the
opening and the title into its first dungeon, headless and checked
against melonDS; the picture and the sound are next, by eye and by ear.
To try it (MSYS2's clang, CMake, Ninja and SDL3; `C:\msys64\mingw64\bin`
on PATH, at run time too):

```sh
ROM="rom/Lufia - Curse of the Sinistrals (USA).nds"
python -m ndskit.recomp "$ROM" --out build/recomp        # about 10 minutes
cmake -S build/recomp -B build/recomp/b -G Ninja -DCMAKE_CXX_COMPILER=clang++ && ninja -C build/recomp/b
build/recomp/b/ndsrun "$ROM" --window --save-size 65536 --out build/play
```

## Layout

    docs/            cartridge, format and code analysis, and the plan
    tools/           Lufia-specific tools: mcd.py (the game's archive), oracle.py (melonDS)
    ndskit/          the game-agnostic DS toolkit (a submodule)
    rom/, build/     your cartridge and everything derived from it (ignored by git)

## Tools

Python 3, no dependencies (the oracle needs PIL for its pictures, and a
copy of melonDS for itself: `ORACLE_DIR`, `tools/oracle.py`). From the
repository's root:

```sh
ROM="rom/Lufia - Curse of the Sinistrals (USA).nds"

# the cartridge: header, programs (the ARM9 compressed), autoloads, 20 compressed overlays, SDK, banner; its files
python -m ndskit.rom "$ROM" --info
python -m ndskit.rom "$ROM" --list
python -m ndskit.rom "$ROM" --extract build/extract --nested

# the game's archive (mcd.dat: 11 386 members, LZ11, RLE and Huffman inside), the sound archives
python tools/mcd.py build/extract --list
python tools/mcd.py build/extract --scan --extract build/mcd
python -m ndskit.sdat build/extract/sound/sound_data_us.sdat --list
python -m ndskit.sdat build/extract/sound/bgm_sound_data.sdat --waves

# the code: every function of the ARM9, of each overlay with it, of the ARM7
python -m ndskit.recomp.discover "$ROM" --cpu 9 --overlay all --report --out "build/disc/ov{id}.tsv"
python -m ndskit.recomp.discover "$ROM" --cpu 7 --report --out build/disc/disc7.tsv
python -m ndskit.arm build/extract/sys/arm9.dec.bin --base 02000000 --at 02107768 --count 60   # FS_StartOverlay

# the oracle: melonDS from a new cartridge (fast-forwarded through the opening) into the first dungeon
python tools/oracle.py --fresh --at "1:down:FF,82:up:FF,87:A,95:A,97:A,99:A,101:A,103:A,105:A,107:A,109:A,111:A,113:A,115:A,117:A,119:A,121:A,123:A,125:A,127:A,129:A,131:A,133:A,135:A,137:A,139:A,141:A,143:A,145:A,147:A,149:A,151:A,153:A,155:A,157:A,159:A,161:A,163:A,165:A,167:A,169:A,175:state"
python -m ndskit.melonds build/oracle/t175.ml1 --overlays "$ROM"
```

The oracle's melonDS.toml must map melonDS's fast-forward to F
(`HK_FastForward = 70`) for `down:FF`.

## Status

Session 1: feasibility. The cartridge read (a compressed ARM9, 20
compressed overlays stacked at five load addresses, a newer SDK's ARM7
that parks its wireless driver in main RAM, a 512 Kbit EEPROM save), the
formats at a glance (one archive of 11 386 named members in the SDK's 2D
and 3D formats, Lua 5.1 bytecode, UTF-16 text, every sample IMA-ADPCM,
644 voice streams), the code mapped (the ARM9 and its overlays 11 542
functions, every one of Ghidra's covered, no conflict), the frame rate
measured (30), the oracle driven through the unskippable opening into
the first dungeon, and the plan (`docs/06-attack-plan.md`). Overlay 0 is
an anti-piracy module that decrypts and rewrites its own code as it
runs: the port's hardest part, for which ndskit's runtime will need an
interpreter. ndskit gained the BIOS's Huffman and discovery of
CodeWarrior's Thumb switches, a newer ARM7's halfword tables and Thumb's
long branches, checked on pc-moon, pc-nostalgia and three more
cartridges.

Session 2: recompiled and running. Both programs and the twenty overlays
recompiled (about 25 000 functions; the self-test's 137 231 vectors pass,
recompiled and interpreted); the compressed program found at the boot;
the stacked overlays told apart function by function; the anti-piracy
module's self-decrypting code run in ndskit's new interpreter. The
opening plays headless to the title, where main RAM agrees with
melonDS's but for a stream's buffer; the prologue leads into Soma Temple.
The title's two 3D screens (display capture) now draw right.

## Documentation

* [00-sessions.md](docs/00-sessions.md) — what each session did
* [01-cartridge-layout.md](docs/01-cartridge-layout.md) — header, programs, the ARM7's autoloads, the overlays' stack, the file system, the save
* [02-data-formats.md](docs/02-data-formats.md) — mcd.dat, the 3D and 2D, Lua, text, sound and the voices
* [03-executables.md](docs/03-executables.md) — crt0 and the compressed ARM9, the overlays' loading, the anti-piracy overlay, the frame, discovery against Ghidra, the ARM7
* [04-curiosities.md](docs/04-curiosities.md) — things found on the way
* [05-open-questions.md](docs/05-open-questions.md) — what is not known yet
* [06-attack-plan.md](docs/06-attack-plan.md) — what is new against Moon and Nostalgia, a better Lufia on PC, the phases, the oracle's route
* [07-next-session.md](docs/07-next-session.md) — the next session's list
* [09-recompiler.md](docs/09-recompiler.md) — the modules, what the self-test found
* [10-ndskit.md](docs/10-ndskit.md) — what this port gave ndskit
* [11-runtime.md](docs/11-runtime.md) — the boot, overlays per function, the interpreter, against melonDS, display capture

## Licence

MIT — see [LICENSE](LICENSE). Lufia: Curse of the Sinistrals is © 2010
Square Enix; original works © Taito; this project contains none of it.
