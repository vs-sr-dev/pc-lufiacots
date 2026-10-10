# Next session

Session 1 read the cartridge and the code and wrote the plan
(`06-attack-plan.md`). Next, phases 2 and 3, in this order:

1. **Recompile**: `python -m ndskit.recomp ROM --out build/recomp
   --optest`. Expected to meet: the compressed ARM9 (the module records
   the program as loaded, so the runtime finds it at the boot; a kit
   change), the stacked overlays (each overlay's run with the overlays
   below it in its stack loaded; the cross-overlay pass across bases),
   overlay 0 recompiled as it is stored (its stubs and decryptor; its
   decrypted code left to the interpreter), Thumb switches and long `bl`s
   in the emitter's output. Then the self-test with this game's functions
   (`selftest --auto`, the program, the ARM7, a Thumb-heavy overlay, 1 or
   14), Thumb switches among them.
2. **The runtime's boot**: the ARM9 decompressing itself under the
   recompiled crt0, the ARM7's autoloads (its VRAM write dropped, the
   parked copy in main RAM), `FS_StartOverlay` decompressing overlays in
   place and the resident check following it, **residency by overlap**
   (core.cpp's `Slot`, generalised), the save with `--save-size 65536`.
   Measure the headless speed at once.
3. **The interpreter** (a kit change): ndskit's `armemu` in C++ in the
   runtime, for code no module holds; checked against `armemu` itself and
   by the self-test's vectors run through it. Then overlay 0's
   initialisers and the program's three calls into it run interpreted;
   trace what the module reads (the cartridge, the code, the backup).
4. **The route against melonDS**: the opening headless to VBlank 5 806
   (`build/oracle/fps/t30.ml1`) and to the title, 15 813 (`fps/t84.ml1`):
   `melonds --compare`. Then NEW GAME and the prologue's presses, into
   Soma Temple (`fps/t175.ml1`, 21 273). The presses: the oracle's times
   do not map to frames while melonDS fast-forwards; read the frames from
   the states (`--peek 027FFC3C:4`) and the pad's state.
5. Then the picture and the sound (the voice streams), by the user's eyes
   and ears in the window.

Kit changes keep the flow (`10-ndskit.md`): committed in this port's
`ndskit/`, checked on pc-moon and pc-nostalgia (the brief's scripts) and
by discovery on the five cartridges, fast-forwarded into
`D:\Homebrew6\ndskit`, the two ports' submodules bumped. ndskit's README
(its known gaps: Thumb switches and halfword tables now done, Huffman
now done; its checks) is brought up to date at the publication.

Before starting: MSYS2's tools on PATH (`/c/msys64/mingw64/bin`, SDL3.dll
at run time); the cartridge in `rom/` and extracted (`ndskit.rom
--extract build/extract`); the oracle's melonDS.toml with
`HK_FastForward = 70` (done this session; its backup
`melonDS.toml.bak-lufia`).
