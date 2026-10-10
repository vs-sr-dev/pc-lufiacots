# The porting route

## Verdict: feasible, by static recompilation, as Moon and Nostalgia

The same road as pc-moon (its `06-attack-plan.md` weighs the others) and
pc-nostalgia: both programs recompiled to C++ by ndskit, the DS's
hardware replaced at its registers by ndskit's runtime, melonDS as the
oracle. Moon took six sessions from nothing to playing with picture and
sound, Nostalgia three; most of that work is ndskit's and is reused here
as it is. This is ndskit's third game, and the first that fights back:
compressed programs, overlays stacked at five bases, and an anti-piracy
module that decrypts and rewrites its own code while it runs.

What is the same as the first two (and so already done):

* CodeWarrior's code, the SDK's crt0, threads, interrupts, IPC; the 3D in
  the SDK's G3D, the 2D in its G2D, the music sequenced on the ARM7.
* IMA-ADPCM samples, PSG and noise instruments (as Nostalgia's).
* A 512 Kbit EEPROM on AUXSPI (as Nostalgia's: `--save-size 65536`).
* 30 frames a second (as Nostalgia).
* Discovery finds every function of Ghidra's in the program (8 150 of
  8 167 as entries, the other 17 inside its functions), with no conflict
  but in the encrypted overlay.

What is new, and what it asks of ndskit (each of these goes into the
kit, not into the port):

| New here | Why it matters | In ndskit |
|---|---|---|
| **an anti-piracy overlay that decrypts itself** (overlay 0: five initialisers decrypt 27 blocks; the decrypted code is trampolines and a second decryptor run at run time) | code that rewrites itself while it runs: no static recompilation sees it; the runtime would stop at a call into it (`call to ..., not an entry`) or run stale code | **an ARM interpreter in the runtime** (ndskit's `armemu` in C++): code that no module vouches for (its bytes are not a module's) is interpreted, in step with the rest. The general answer to self-modifying and decrypted code, and to code copied at run time without `--copy`. The runtime must also answer every check the module makes as a genuine cartridge would (below). In reserve, in the port: skip the three calls with a genuine cartridge's answers (an AP patch), if the interpreter path cannot be made to agree with melonDS |
| **a compressed ARM9** (decompressed by its crt0) | the runtime finds the ARM9's module by the crc32 of its first segment in memory at the boot: memory holds the compressed program then | the recompiler records the program as it is loaded too (the crc32 of the stored image), and the runtime matches either |
| **compressed overlays**, decompressed in place by `FS_StartOverlay` | between the cartridge's data and the decompression the area holds the stored bytes | the resident check already waits for a call: to check that it follows (a crc32 over the stored image is not needed, nothing runs there before) |
| **overlays stacked at five bases**, one over another's middle (in the dungeon overlay 4 sits inside overlay 1) | an address belongs to overlays of up to three bases; Nostalgia's runtime groups overlays by base address (`core.cpp`, `Slot`) | the runtime: residency by overlap (each overlay recognised by its own code ranges, an address dispatched to the resident overlay that covers it), possibly per code range for an overlay partly overwritten. Discovery: each overlay discovered with the overlays below it in its stack loaded (0, 3, 8 under 9-18; 0, 3, 4 under 5-6), not only told their areas. Discovery already refuses a call meant for another base (this session) |
| **a newer ARM7** (SDK 5.x) with its wireless driver linked for VRAM and parked in main RAM | its halfword-offset tables (now in discovery); a VRAM segment in the ARM7's module; banks C/D for the ARM7 if the wireless ever starts | the recompiler: the ARM7's VRAM segment, which runs only once copied there; the runtime: VRAM C/D mapped to the ARM7 by VRAMCNT, its writes to unmapped VRAM dropped (as now) |
| **voices as streams** (644 STRMs, three stream players) | the ARM9 reads each stream from the cartridge into a buffer a channel loops over; the cartridge answers at once in ndskit, where the DS takes time | the runtime's cartridge time (a known gap), checked by ear; the sound unit as it is |
| **28% Thumb** | CodeWarrior's Thumb switches, Thumb's long `bl`, returns through r3 | discovery: done this session; the recompiler: Thumb switches (`add pc, rB`) and long `bl`s emitted (the emitter's part done, the self-test to cover them) |
| **Lua 5.1** inside the game | 1 121 bytecode members; the VM is in the program | nothing: it is code like the rest |

What is not here: no movies, no flash save, no nested archives, no
wireless play (*inferred*), no Mobiclip.

## The anti-piracy, in more detail

What the module checks is still to read, in the interpreter's trace once
it runs. What a genuine DS gives it and ndskit's runtime must give too:

* **the code as the cartridge has it**: checksums over the program or the
  overlays see guest memory, which recompilation keeps byte for byte;
* **the cartridge's answers**: the chip ID, the secure area as it reads
  after the boot, reads past the image's end, the timing of the card's
  commands (ndskit answers at once: a known gap that an AP may notice);
* **the backup memory's type**: the boot's probe identifies it as a 64
  Kbit EEPROM (0x0D01) and keeps the outcome (0x02158AFC); the save
  module uses 512 Kbit. melonDS gives the game an 8 KiB chip and plays;
  which answer the probe wants is to read;
* nothing should differ between melonDS and the runtime at the frames
  the module runs: its memory compared with melonDS's states at the same
  VBlank (`melonds --compare`), as always.

A failed check in such modules often does not stop the game at once: it
sabotages it later (a door that never opens, a freeze at a boss).
Comparing with melonDS's memory after the module has run, not only the
pictures, is how to know it passed.

## Where to cut

Unchanged from pc-moon's plan: everything at the hardware registers, the
BIOS's SWIs in HLE, the ARM7 recompiled and run as a coroutine, the 3D's
geometry engine in software in the DS's fixed point and its rendering on
OpenGL at the window's resolution, overlays dispatched by the resident
one. The one new cut is the interpreter's: at the dispatch, for code that
no module holds.

## A better Lufia on PC

### Resolution

The 3D (the dungeons, the towns, the field, and the battles, which are
fought in the field: *inferred*, an action RPG) drawn at the window's
resolution, as Moon's and Nostalgia's; the 2D (the HUD, the minimap on
the lower screen, the dialogue boxes and busts, the menus) at 256x192 and
scaled without blurring.

### The frame rate

The game runs at 30. An action RPG gains more from 60 than an RPG does:

1. **A steady 30**, the DS's drops in heavy rooms gone.
2. **The 3D at 60 or the display's rate** by interpolating two of the
   game's frames in the port's geometry engine (it sees every matrix and
   vertex: one frame of latency), or the game's step halved where its
   logic allows. To read first: where the frame loop waits for its two
   VBlanks.

### The two screens

The upper screen is the game; the lower one is the minimap with the
place's name, the leader's bust and level, and the SELECT and START
buttons (Soma Temple 1F). On PC: the upper screen as the main view, the
minimap as a panel beside it or as an overlay in a corner, at the
player's choice; the lower screen whole on demand (a key), with the
mouse as the stylus where the game wants touches.

### Controls

The keyboard and a gamepad as the DS's buttons, with a gamepad layout
of an action RPG; what each button does here (attack, jump, the IP
skills, the party's switch) is to read in play. The soft reset
(L+R+START+SELECT) kept. The opening (4 min 20 s, unskippable on the DS)
could be made skippable after a first viewing: a change to the game's
behaviour, so an option, off by default.

## The phases

| Phase | What | Done when |
|---|---|---|
| 1. Recognise (session 1) | the cartridge, the formats, the code, the oracle, this plan; ndskit: Huffman, discovery's Thumb forms | this document |
| 2. Recompile | the program, its overlays, the ARM7 as modules; overlay 0 as it is stored (its plain stubs and decryptor); the module found though the ARM9 is compressed; the self-test with this game's functions, Thumb switches and long `bl`s among them | everything compiles; the self-test has no difference |
| 3. Runtime | the boot (the compressed ARM9 and overlays, the ARM7's autoloads), the stacked overlays' residency by overlap, **the interpreter** for the decrypted code, the save (512 Kbit), the route through the opening to the title | its memories against melonDS's states at the same VBlank: the opening, the title |
| 4. The anti-piracy | the module's checks read in the interpreter's trace; every answer as a genuine cartridge's | the memory after the module ran equal to melonDS's; the game plays past the prologue |
| 5. Picture | the opening, the title, the prologue's ship, Soma Temple | the pictures against melonDS's at the same frames; the user's eyes |
| 6. Sound | the music (ADPCM, PSG), the effects (PSG, noise), **the voices' streams** | the channels' registers against melonDS's; the user's ears |
| 7. Publication | ndskit proven on three games: the four repositories, the ports' submodules bumped | Lufia works "until proven otherwise" |
| 8. PC | the screens' layout, 60 fps, the controls, the resolution | played by the user |

## Oracle

melonDS (`D:\Tools\melonDS-oracle`), driven by `tools/oracle.py`
(pc-nostalgia's, with `load:FILE` and `FF`, melonDS's fast forward held:
the oracle's melonDS.toml maps it to F). The route from a new cartridge
into the first controllable moment:

    python tools/oracle.py --fresh --at "1:down:FF,82:up:FF,87:A,95:A,97:A,...,169:A,175:state"

The opening plays for about 4 min 20 s (VBlank 15 700) and cannot be
skipped; held fast-forward brings the title in about 82 s (melonDS at
about 3 times the DS). A on NEW GAME starts the prologue: the
Excelion's deck, Lexis and Hector (A advances their lines), a title card,
more of their lines, then **Soma Temple 1F**, controllable at about
VBlank 21 000. States kept in `build/oracle/`: `fps/t30.ml1` (the
opening, 5 806), `fps/t84.ml1` (the title, 15 813), `r16/t200.ml1` and
`fps/t175.ml1`, `t182.ml1` (Soma Temple, 22 827, 21 273, 21 692).

Loading a state (`load:FILE`, melonDS's F1) works only when the slot's
file is there at the launch (the tool copies it first); after a load the
game took no input in two tries, which a fast-forwarded boot does not
have (`05-open-questions.md`).
