# Sessions

## Session 1 (2026-10-10) — the cartridge, the code, the oracle, the plan

* **The repository**: ndskit as a submodule at `ndskit/` (`../ndskit`),
  pc-moon's MIT licence, pc-nostalgia's `.gitignore`; the cartridge in
  `rom/`.
* **The cartridge** (`01-cartridge-layout.md`): the US release, BSDE,
  Natsume (E9), **NitroSDK 5.3**; on screen the Square Enix and Neverland
  logos, the staff in the opening, "© 2010 SQUARE ENIX ... Original
  Works: ©TAITO CORP. 1993,1995 ... published by Natsume Inc." on the
  title. **The ARM9 compressed** (the SDK's backward LZ, undone by its own
  crt0); **20 overlays, all compressed, stacked at five load addresses**,
  each the end of another (in the dungeon overlay 4 lies over the middle
  of overlay 1); **a newer ARM7** whose third autoload, linked for VRAM, is
  the wireless driver, copied at the boot to main RAM (0x027E00BC) and
  parked there; the save a **512 Kbit EEPROM** (0x1001 in the save module),
  which melonDS makes an 8 KiB file of.
* **The formats** (`02-data-formats.md`): one archive, `mcd.dat`, of 11 386
  named members, its index (`mcd_compact.bin`, `mcd_path.bin`,
  `file_uid.bin`) read by `tools/mcd.py`; members plain or wrapped in
  "$FAB" with LZ11, RLE, stored or **Huffman** (new in ndskit's `lz`); every
  member parses. The SDK's G3D and G2D as they are; **Lua 5.1** bytecode
  (1 121 scripts, integer numbers); text in UTF-16BE; two SDATs, every
  wave IMA-ADPCM, PSG and noise, and **644 voice streams** (23 minutes).
* **The code** (`03-executables.md`): crt0 and the self-decompression,
  `main` at 0x02000BC4, `FS_StartOverlay` at 0x02107768 (SDK 5's,
  decompressing in place). **Overlay 0 is an anti-piracy module that
  decrypts itself**: five initialiser stubs decrypt 27 blocks (run in
  `armemu`: 619 words changed), which are trampolines and a second
  decryptor run at run time; the program calls it from 0x02096004.
  Discovery: 28% of the ARM9 is Thumb; the program with its overlays
  11 542 functions, the ARM7 1 058, **0 conflicts** but in the encrypted
  overlay; all 8 167 of Ghidra's functions covered.
* **ndskit gained** (`10-ndskit.md`): Huffman in `lz`; discovery of
  CodeWarrior's Thumb switches (the known gap: 43 here; the 2008 Thumb
  cartridge's overlays gained 1 143 and 628 functions), a newer ARM7's
  halfword tables (the other known gap: 36 here, 37 on the 2010
  cartridge), Thumb's `bl` used as a long branch (the first run's two
  conflicts), Thumb's return through r3, guessed entries refused when
  their descent meets data (calls meant for an overlay at another base);
  a fix of the self-test (a slot's overlay not checked again between
  vector files: pc-nostalgia's whole self-test in one command had 17
  failures with the kit as published). Each checked on pc-moon and
  pc-nostalgia (their builds, self-tests, runs against melonDS, routes)
  and by discovery on five cartridges; ndskit fast-forwarded, both ports'
  submodules bumped and committed (not pushed).
* **The oracle**: `tools/oracle.py` (pc-nostalgia's, with `load:FILE` and
  `FF`, melonDS's fast forward). The opening is **unskippable**, 4 min 20
  s to the title; NEW GAME starts the prologue on the Excelion (Lexis and
  Hector), then **Soma Temple 1F**, controllable at about VBlank 21 000.
  States at the opening, the title and the dungeon. Overlays resident:
  0 always (decrypted), 19 in the opening, 4 at the title and in the
  dungeon, 1 under 4 in the dungeon.
* **The frame rate: 30 a second**, six counters of the game's at half the
  VBlank count in the opening, the title, the dungeon standing and
  walking.
* **The plan** (`06-attack-plan.md`): Moon's and Nostalgia's road; new
  here an interpreter in ndskit's runtime for the self-modifying
  anti-piracy code, the compressed ARM9's module found at the boot,
  residency by overlap for the stacked overlays, the ARM7's VRAM segment,
  the voice streams; on PC the 3D at the screen's resolution, 60 by
  interpolation, the minimap as a panel, an action RPG's pad layout.
