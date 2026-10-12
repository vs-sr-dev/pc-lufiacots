# What this port gave ndskit

ndskit is the game-agnostic DS toolkit born with pc-moon and proven on
pc-nostalgia. This port is its third game. It is a git submodule at
`ndskit/` (URL `../ndskit`, its own repository beside this one); pc-moon
and pc-nostalgia take the same repository.

The flow of a change: committed in this port's `ndskit/` ("ndskit: ...",
the kit's files only), checked on pc-moon (its build from the recompiler,
the self-test's 81 555 vectors with no failure, its run of 466 VBlanks
against melonDS's state at frame 464: 74 bytes of main RAM, its route
into the first room), on pc-nostalgia (its build, its whole self-test in
one command: 115 393 vectors with no failure, its route into the first
dungeon with three changes of overlay, about 2 000 bytes of main RAM) and
by discovery on five cartridges, both CPUs, overlays included (Moon,
Nostalgia, a 2010 cartridge with a compressed ARM9 and 366 overlays, a
2008 one mostly in Thumb, this one: 0 conflicts, no function lost or
split, the lists diffed before and after); then fast-forwarded into
`D:\Homebrew6\ndskit` and taken by both other ports' submodules, each
with a commit and its `10-ndskit.md`. Nothing is pushed until this game
is playable.

## Session 1

| Commit | What | Checked by |
|---|---|---|
| `b2c3fd6` | `lz`: the BIOS's Huffman (types 0x24 and 0x28: the tree, the bits in words from their top bit, 4-bit units low nibble first) | the 406 Huffman members of this game's archive decode to their size within their records; the 38 G2D files among them carry their own size fields equal to what came out |
| `49a3de7` | discovery: CodeWarrior's Thumb switches and a newer SDK ARM7's halfword tables (one rule for both, the bound through `bls ok; b default` or a long `bl default`); Thumb's `bl` as a long branch (its target inside its own function, or a literal pool after it), walked as a `b` and emitted as a goto or a tail call; Thumb's return through a popped register; a call through a conditional `movne lr, pc`; a jump into code unrolled by two instructions; an entry guessed from a pointer, a prologue or a crossing refused when its descent meets data once the rest is known, and the discovery done again without it | this cartridge: 164 switches (118 before), its ARM7 39 (2), 0 conflicts but in the encrypted overlay (2 before in the program, 5 in overlay 1); Moon's and Nostalgia's lists identical; the 2010 cartridge's ARM9 identical, its ARM7 23 functions more; the 2008 one 103, 1 143, 628 and 66 functions more (its program and three overlays); every function no longer listed a long `bl`'s target inside its function or another overlay's function; pc-moon and pc-nostalgia as above |
| `6eda9f5` | the self-test moves the overlay epoch on after loading an image, so a slot is checked again between vector files | pc-nostalgia's whole self-test in one command: 115 393 vectors, no failure (with the kit as published, 17 failures: overlay 1's first function ran overlay 0's code, both opening with the same instruction); pc-moon's 81 555, no failure |

`D:\Homebrew6\ndskit` is at `6eda9f5`; pc-moon's submodule bumped in its
commit `0dfb858`, pc-nostalgia's in `0fa3b4b` (both local).

## Session 2

| Commit | What | Checked by |
|---|---|---|
| `08ba0d2` | **an ARM interpreter in the runtime** (`runtime/interp.cpp`, armemu's semantics in C++: code no module holds runs from memory until it returns to its caller, its calls to entries run recompiled; a call to a non-entry is interpreted instead of stopping; a function the emitter cannot take becomes a call to it; the self-test's `--interp`); **overlays told apart function by function** (each function's extent, its code and folded literal pools, with its crc32; a call into the overlays' area goes to the function whose bytes are in memory as built; every store marks its 256-byte page; the slots, the cartridge's epoch, the samples and the first instructions gone); a compressed program's stored image as a segment of kind "loaded", which the boot matches; the emitter's Thumb `add pc, rB` read unaligned (switches at 2 mod 4 went two bytes short; the instruction test has the switch at both alignments); discovery: a known word pushed alone and popped into pc is a jump there (CodeWarrior's Thumb thunks into ARM); `--auto` keeps a vector only if it runs discovered code, and leaves out segments outside the test's memory (the ARM7's VRAM autoload); display capture's source A is engine A's graphics whatever its display shows; VRAM in the run's dump | this game: 137 231 vectors, no failure, recompiled and interpreted; the opening, the title (12 482 bytes of main RAM apart from melonDS, 12 288 of them a stream's buffer) and the route into Soma Temple to frame 22 000; pc-moon: 81 587 vectors both ways, 74 bytes at frame 464, its route to frame 3 644; pc-nostalgia: 115 425 vectors both ways, its route into the first dungeon, 2 047 bytes apart as before; discovery on the five cartridges, both CPUs and their overlays: the lists identical, conflicts unchanged |
| `720c636` | the overlay log tells each change of hands (a module found takes those whose area meets its own out of the found list) | pc-nostalgia's route: overlays 0, 1, and 0 again at 2 792, as the slots told; this game's route: 19, 4, 1, 4 again, no repetition |

| `5ee24af` | the README for publication with its third game: the ports table, the layers, the checks behind each module, the known gaps | - |

At the publication (2026-10-11) ndskit was pushed at `5ee24af`, and both
other ports' submodules bumped to it and pushed.

What the kit still lacks for this game: discovery of the small methods
reached through pointers that the interpreter now runs; each overlay
discovered with the overlays below it in its stack (not needed so far:
the per-function residency follows the stacks as they are); the voice
streams heard against melonDS. Its README's known gaps (Huffman, Thumb
switches, halfword tables, now the interpreter and the overlays) and
checks are to update at the publication.

## From pc-finalfantasy12revenantwings

Changes of the kit made for the fourth game, Final Fantasy XII: Revenant
Wings, each checked here as above before it was taken:

| Commit | What | Here |
|---|---|---|
| `ad61a11` | a thread switch takes the rest of the CPU's quantum: the other CPU runs before the woken thread (the fourth game's frame start read the ARM7's VBlank count before the ARM7 had stored it, and ran at 60 frames a second instead of 30) | 137 231 vectors, no failure, recompiled and interpreted; the title 12 428 bytes apart from melonDS's state (12 482 before, 12 288 of them the stream's buffer); the route into Soma Temple to frame 22 000, overlays 19, 0 (at 502, then 13 times more), 4, 1 and 4 at the same frames as before but for one |

The submodule is at `ad61a11`.
