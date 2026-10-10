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

What the kit still lacks for this game (`06-attack-plan.md`): an ARM
interpreter in the runtime for the anti-piracy's self-modifying code;
the ARM9's module found when the program is loaded compressed; overlays'
residency by overlap, across load addresses; each overlay discovered with
the overlays below it in its stack; the voice streams heard against
melonDS. Its README's known gaps (Huffman, Thumb switches, halfword
tables) and checks are to update at the publication.
