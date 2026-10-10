# The code

Read with ndskit (`arm`, `armemu`, `recomp.discover`) and Ghidra 12.1.2,
and seen running in melonDS through its savestates. *Inferred* marks
what is read from the shape of the code without a run to confirm it.

```sh
ROM="rom/Lufia - Curse of the Sinistrals (USA).nds"
A9="build/extract/sys/arm9.dec.bin --base 02000000"     # the ARM9 decompressed (rom --extract)
python -m ndskit.arm $A9 --at 02000800 --count 110       # crt0
python -m ndskit.arm $A9 --at 02107768 --count 60        # FS_StartOverlay
python -m ndskit.recomp.discover "$ROM" --cpu 9 --report --out build/disc/disc9.tsv
python -m ndskit.recomp.discover "$ROM" --cpu 9 --overlay all --report --out "build/disc/ov{id}.tsv"
python -m ndskit.recomp.discover "$ROM" --cpu 7 --report --out build/disc/disc7.tsv
```

## The ARM9

* **crt0** at 0x02000800: the SDK's (CP15 and the protection unit, the
  TCMs, the stacks, clearing the DTCM, the palettes and OAM), then
  **`MIi_UncompressBackward` (0x02000950) on the program itself**, with
  ModuleParams' compressed end (0x020D3D90), then the autoloads, the BSS,
  three calls into the SDK (0x02129044, 0x02014164, 0x0212A428), and `bx`
  to `main` at **0x02000BC4** with lr = 0xFFFF0000. The decompression
  runs in place, from the end backwards, in the program's own plain head
  (0x02000000-0x02004000 is stored plain): the recompiled crt0 does it as
  the DS does, on the bytes the cartridge loaded.
* **`main`** (0x02000BC4) keeps a word of the system area (0x02FFFD9C) at
  0x02154A54, calls 0x0210FFA8 (and 0x02110F4C if it returns 0), then
  0x02110F74 with the address 0x02013C8C, then **0x02013D6C** (*inferred*:
  the game's loop, which `main` never returns from).
* **0x02013D6C** reads the buttons (KEYINPUT and the ARM7's
  X/Y/hinge word at 0x02FFFFA8) and hands them to the pad (0x020833D4,
  its state at 0x021587B4: held at +0x14, pressed at +0x18, *inferred*
  from the functions that test them). **L+R+START+SELECT** (0x30C)
  calls 0x02013F78 (*inferred*: the soft reset; the SDK's last step of
  one, in the ITCM at 0x01FFF1F8, jumps to the header's entry).
* **`FS_StartOverlay`** at **0x02107768**, SDK 5's: when the entry's
  flag has bit 1 set it calls 0x021076A8 with an entry of a table at
  0x0215484C (*inferred*: the overlay's digest checked), then undoes the backward LZ when bit 0
  is set (`MIi_UncompressBackward` again, from 0x02107810), flushes the
  cache, and calls each non-zero pointer between the entry's sinit start
  and end. The overlays are loaded compressed and decompressed **in
  place** here: before this, the area holds the stored bytes.

### The anti-piracy overlay (overlay 0)

**Overlay 0 decrypts itself.** Its five static initialisers (0x02174648,
0x02174BF0, 0x02174F78, 0x021757D4, 0x02175C8C) are stubs of three
instructions:

    orr r0, pc, #0          ; r0 = here + 8
    adds r0, r0, #4         ; the table after the stub
    bne 0x02174C60          ; the decryptor (a branch: it returns to the stub's caller)
    .word start + 0x1000, length + 0x02176D20, ...   ; blocks to decrypt, 0-terminated

The decryptor (0x02174C60) decrypts each block word by word (a running
key from 0xF0B9A2EA; a word that is a `b`/`bl`/`blx` gets its offset
mended by 0x02174C24), cleans and invalidates the caches, then **zeroes
the stub and its table** (zeros are `andeq r0, r0, r0`: no-ops). 27
blocks in all, 0x24 to 0x184 bytes each, 0x898 bytes. Run in `ndskit.armemu` with the
overlay loaded, the five initialisers take 35 429 instructions and change
619 words.

What they decrypt is itself obfuscated: trampolines (`orr r12, pc, pc;
ands r12, r12, r12; ... ldr r12, [r12, #0x14]; sub r12, r12, #0x1000;
push {r12}; ... ldm sp!, {pc}`) into other blocks, and a second decryptor
(0x02174D90) whose key comes from the addresses it is given, run by the
decrypted code at run time. **It is code that rewrites itself while it
runs**, at least two layers deep: no static recompiler sees all of it
ahead of time. Discovery finds 24 functions in the image as the
initialisers leave it.

The program calls it at three places, all in one function (0x02096004):
`bl 0x021744E0`, `bl 0x02174558`, `bl 0x021745D0` (0x02096090, 0x020961AC,
0x020965B8), the first with a function pointer (0x02095B6C) and the
result compared with the complement of an argument. In melonDS's states
overlay 0 is resident from the opening on, its bytes 58.5% the
cartridge's (the rest decrypted). *Inferred*: it is an anti-piracy
library (the AP of the scene's patch lists), checking the cartridge and
the code, which a flash cartridge or a patched program fails.

**On ndskit's runtime** (session 2, `11-runtime.md`) the overlay is
loaded 14 times on the way from a new cartridge into Soma Temple (frames
501 to 18 803), and each time its initialisers decrypt it again. An
initialiser runs recompiled while its bytes are as stored and
interpreted once the decryption has touched them (0x02175C8C, the last: *inferred*, its extent meeting a block decrypted before it)
or when the emitter could not take it (0x021757D4, whose discovered body
runs into encrypted bytes); everything they decrypt runs in the
interpreter, as do the three entries
the program calls (first at frames 501, 515 and 518). At the title, main
RAM agrees with melonDS's but for a stream's buffer and about 200 bytes.

### The frame

**30 frames a second**, measured in melonDS from pairs of savestates two
seconds apart (`tools/oracle.py`, the method of pc-moon's session 2): six
counters of the game's (0x02154A64, 0x022D1430, 0x022D14C8, 0x022D159C,
0x022D43CC, 0x022D4534) advance by half the SDK's VBlank count in every
situation:

| Moment | VBlanks | Counters |
|---|---|---|
| the opening, in 3D (melonDS fast-forwarding) | +375 | +187 |
| the title | +120 | +60 |
| Soma Temple 1F, standing | +119 | +59, +60 |
| Soma Temple 1F, UP held | +121 | +61, +60 |

No counter of the game's advanced once per VBlank. Nostalgia also runs
at 30; Moon at 60.

## Function discovery against Ghidra

Discovery with this session's ndskit (`10-ndskit.md`: CodeWarrior's
Thumb switches, halfword tables, Thumb's long `bl`; before it, 2
conflicts in the program and 118 switches):

| Program | Functions | Thumb | Switches | Conflicts |
|---|---|---|---|---|
| ARM9 alone | 11 389 | 3 232 (28%) | 164 (2 164 targets) | 0 |
| ARM9 with what its overlays reach | 11 542 | | | 0 |
| overlay 0 (encrypted) | 10 | 0 | | 4: its encrypted bytes read as code |
| overlay 1 | 791 | 621 | | 0 |
| overlay 2 | 0 (32 bytes) | | | 0 |
| overlay 3 | 59 | 31 | | 0 |
| overlays 4-19 | 252, 164, 131, 56, 242, 329, 166, 256, 374, 423, 596, 271, 206, 276, 113, 365 | 0 to 227 each | | 0 |
| ARM7 | 1 058 | 9 | 39 (674 targets) | 0 |

**Against Ghidra** (12.1.2, the decompressed ARM9's main block as a flat
binary with the entry as root, `ndskit/ghidra/ExportFuncs.java`): 8 167
functions. With what the overlays reach, discovery has **8 150 of them as
entries and the other 17 as code inside its functions**: 12 are the
targets of Thumb `bl`s that are long branches into their own function
(Ghidra takes each `bl` for a call), 5 a few bytes into a function. 3 271
of ours are not in Ghidra's (vtables' methods and thunks, as on Moon).

What discovery met here for the first time, and now handles (each rule in
ndskit, checked on the other four cartridges):

* **CodeWarrior's Thumb switch** (`cmp rI, #N; bhi default; adds rB, rI,
  rI; add rB, pc; ldrh rB, [rB, #6]; lsls rB, #16; asrs rB, #16; add pc,
  rB`), 43 of them, the known gap; with `bls ok; b default` or a long
  `bl default` before it.
* **Thumb's `bl` as a long branch**: to the function's own epilogue past
  the reach of a `b` (`bls ok; bl default` before a 109-case switch at
  0x02048148), or into a tail another function shares (0x020D9EC0's
  `bl 0x020DB120`, then `mov r8, r8` and a literal pool). The two
  conflicts of the first run.
* **Thumb's return through r3**: `push {r0-r3}; push {r3, lr}` ... `pop
  {r3}; pop {r3}; add sp, #16; bx r3` (98 sites).
* **A jump into unrolled code by steps of two instructions** in the ITCM
  (0x01FFED14: `rsb r3, r2, #8; add pc, pc, r3, lsl #3`, a copy of 0-8
  bytes).
* **A call through a conditional `movne lr, pc; bxne r12`** (a hook at
  0x02110F88, called when its pointer at 0x0217186C is set; *inferred*:
  the SDK's exception handler's user callback).
* **A call meant for another overlay** at another base over the same
  address (the program's call to 0x02180D84, a function of overlays 9 and
  14, inside overlay 1's area): refused once the descent meets data.

Left to run time (4 in the ARM9, all understood): the soft reset's
`bx r12` to the header's entry (0x01FFF2A0), an exception hook's tail
call (0x02110F20), a context's restore ending in `bx r2` (0x0212AAD4,
*inferred*: `longjmp` or a C++ exception's landing), and a thread
switch's `subs pc, lr, #4` (0x0210FF3C). 4 195 calls through registers
(virtual calls, callbacks), resolved at run time by the dispatch.

## The ARM7

The SDK's component of a newer SDK (crc32 0x3F0CD426): 1 058 functions,
**0 conflicts**, 39 switches, 36 of them the newer SDK's **tables of
halfword offsets** (`cmp rI, #N; bhi default; add r0, pc, rI, lsl #1;
ldrh r0, [r0, #4]; add pc, pc, r0`), the other known gap, now
recognised. Function by function: 460 alike Moon's and Nostalgia's
(none at the same address), 972 alike those of a 2010 cartridge built
with SDK 5.4 (3 at the same address, 502 elsewhere, 467 relocated), 86
different.

Its crt0 (0x02380000) copies the three autoloads at once, without
waiting for the ARM9: to 0x027E0000 (0xBC bytes), to the shared WRAM
(0x037F8000) and to VRAM (0x06000000), then jumps to 0x037F8000. The
first autoload is a function that copies the VRAM block again, to main
RAM at 0x027E00BC (`01-cartridge-layout.md`): the wireless driver
(*inferred* from the registers its code loads, 0x0480xxxx), parked there
until the wireless starts. Where the ARM7 runs it from, and whether this
game ever starts the wireless (it has no multiplayer, *inferred*), is to
see in the runtime.

The rest serves what Moon's served (*inferred* from the same library:
the sound, the touch screen, the RTC, the power, the backup memory), and
the streams' channels (`02-data-formats.md`).
