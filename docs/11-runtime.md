# The runtime: Lufia on ndskit's machine

ndskit's runtime (pc-moon's `docs/11-runtime.md`, `12-picture.md`,
`13-sound.md`; pc-nostalgia's overlays) runs Lufia's recompiled programs.
This session it learnt what this cartridge asked for: the program found
though the cartridge loads it compressed, overlays told apart function by
function wherever they are stacked, an interpreter for the code no module
holds, and display capture from engine A's graphics whatever its display
shows.

```sh
ROM="rom/Lufia - Curse of the Sinistrals (USA).nds"
export PATH=/c/msys64/mingw64/bin:$PATH          # SDL3.dll at run time
build/recomp/b/ndsrun "$ROM" --out build/title --save-size 65536 --vblanks 15836 --shots 15835,15836
python -m ndskit.melonds build/oracle/fps/t84.ml1 --compare build/title
build/recomp/b/ndsrun "$ROM" --window --save-size 65536 --out build/play     # to play
```

## The boot

* **The compressed ARM9**: memory holds the program as the cartridge
  stores it (0xD3D90 bytes, the backward LZ) until its crt0 decompresses
  it in place. The recompiler records that image as one more segment of
  the program's module (kind "loaded": its crc32), and the boot takes the
  module whose first segment *or* loaded image is in memory. The
  recompiled crt0 then decompresses the program as the DS does
  (`MIi_UncompressBackward` is the game's own code, recompiled), and
  everything after runs as on Moon and Nostalgia.
* **The ARM7's VRAM autoload** (the wireless driver, linked for
  0x06000000): its crt0's copy there is dropped (`write to unmapped VRAM`,
  six times at the boot: banks C/D are the ARM9's), and the copy it
  parks in main RAM is what it reads back. Nothing of the ARM7 runs there
  on the route to Soma Temple.
* **The save**: `--save-size 65536` (the 512 Kbit EEPROM the save module
  uses); melonDS's own file is 8 KiB.

## Overlays: function by function

Lufia stacks its 20 overlays at five load addresses (one over the middle
of another: overlay 1 and overlay 4 are both partly resident in the
prologue and the dungeon), and overlay 0 decrypts itself after it is
loaded. Pc-nostalgia's one-overlay-per-load-address residency cannot tell
these apart; ndskit now decides per function:

* each overlay function's **extent** (its first instruction to its last,
  and the literal pools it reads constants from) and the crc32 of those
  bytes as built are in its module;
* a call into the overlays' area (0x02174100-0x0218E540 here) is
  dispatched to the overlay function at that address whose extent is in
  memory as built; none: the interpreter;
* **every store** into the overlays' area marks its 256-byte page written
  (the CPUs, DMA, the BIOS's decompressors, a test's image loads); the
  functions over a written page are checked again when next called. Data
  pages written every frame cost a check of the functions over them,
  nothing more.

On the route from a new cartridge (the log's `found in memory`):
overlay 19 at frame 23 (the opening), 4 at 9 018 (the title), 1 at
18 326 (the prologue: at overlay 3's place and under overlay 4) and
overlay 4's functions found again at 18 818, so both in use together;
overlay 0 at 501 and 13 times more along the route, each time
loaded and decrypting itself anew.

## The interpreter

Code no module vouches for runs in ndskit's interpreter (armemu's
semantics in C++, `runtime/interp.cpp`), in step with the rest (safe
points at calls and backward jumps), until it returns to the caller; a
call it makes to an entry runs recompiled. Here it runs:

* **overlay 0's decrypted code**: its five initialisers (one of them the
  emitter could not take: discovery's descent of it runs into encrypted
  bytes) and the three entries the program calls from 0x02096004
  (0x021744E0 at frame 501, 0x02174558 at 515, 0x021745D0 at 518);
* **about 25 small functions of the program and the overlays that
  discovery misses** (reached through pointers: empty `bx lr` methods in
  ARM and Thumb, getters, this-adjusting thunks), interpreted the first
  time with a line in the log; cheap, and left for discovery to find
  (`07-next-session.md`).

Checked against armemu's own vectors (`selftest --interp`): the
instruction test's 57 781 and the game's 79 450 (`09-recompiler.md`),
no failure.

## Against melonDS

| Moment | SDK VBlank | Main RAM differing | What |
|---|---|---|---|
| the logos, after the anti-piracy's first calls | 687 | 22 109 bytes | the run ahead in loading (a file loaded where melonDS still has free heap); the stream buffer |
| the opening, 3D | 5 806 | 49 174 | a texture loaded in melonDS, not yet in the run; the stream buffer; stacks |
| **the title** | 15 813 | **12 482** | **12 288 of them the voice stream's ring buffer** (0x02262440, the cartridge's time); ~200 bytes elsewhere |

The SDK's VBlank count runs 23 frames behind the runtime's (the boot's
decompression and the cartridge's first reads), so the run is compared at
the same SDK count (runtime 15 836 for the title). In the opening the
cartridge answering at once puts loads ahead of melonDS; by the title the
game waits for the player and the memories agree. The geometry commands
the SDK buffers in the DTCM (0x027E0100, `G3B`) while a DMA to the
geometry FIFO is busy are never buffered here: that DMA completes at
once.

With A pressed every 60 frames from the title, the run goes through NEW
GAME, the prologue on the Excelion's deck and into **Soma Temple 1F**
(the HUD, the minimap, Maxim at level 1) by frame 19 000, and plays on to
22 000 without a stop.

## Speed

Headless, the route to frame 22 000 (367 s of DS time) takes 66 s with
pictures on 14 frames: about 5.5 times the DS; the opening to the title
without pictures, 10 times.

## Display capture

The title draws both screens with engine A's 3D in alternate frames,
capturing each into bank C (the lower screen, engine B's direct-colour
bitmap) or bank D (the upper one, engine A's VRAM display). The capture's
source A is engine A's graphics, its BGs, OBJs and 3D, whatever its
display shows; ndskit composed it from the displayed line, here the VRAM
bank itself, and the title was noise. Now, on a line whose display is
not the graphics, the layers are composed for the capture into a line
buffer of their own (`gpu2d.cpp`). Both screens of the title as melonDS
shows them.
