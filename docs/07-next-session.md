# Next session

Session 2 recompiled both programs and the overlays, booted them on
ndskit's runtime, ran the anti-piracy module in the new interpreter and
followed the opening, the title and the prologue into Soma Temple 1F
(`00-sessions.md`, `09-recompiler.md`, `11-runtime.md`). Next:

1. **The user's eyes and ears**: the window
   (`build/recomp/b/ndsrun "$ROM" --window --save-size 65536 --out
   build/play`, in the background, MSYS2 on PATH), from a new cartridge:
   the opening, the title, NEW GAME, the prologue, Soma Temple. What is
   wrong in the picture or the sound goes into `12-picture.md` and
   `13-sound.md` (the voices are streams the ARM9 refills from the
   cartridge: check them by ear first; the cartridge answers at once,
   a known gap).
2. **The route against melonDS past the title**: the prologue's presses
   timed as the oracle's (read the frames from the states,
   `--peek 027FFC3C:4`, and the pad's state at 0x021587B4), so that the
   run and `fps/t175.ml1` (21 273) are at the same moment; compare the
   memories there and in Soma Temple. The anti-piracy's checks pass at
   the title as far as memory shows; a sabotage would show later (a door,
   a boss): play on.
3. **Saving and loading**: a save in the first save point, the backup's
   bytes against melonDS's (whose file is 8 KiB: check that the game
   writes inside it), then LOAD GAME.
4. **Discovery's misses** (about 25, interpreted, logged as
   `interpreted (lr ...)`): empty `bx lr` methods in ARM and Thumb,
   getters, thunks reached through pointers (0x0212AFA8/AC,
   0x0206B9F0, 0x0200637C, ...). Cheap as they are; recompiled is
   better: find what points at them and the rule discovery lacks, as
   pc-nostalgia did.
5. **Speed**: 5.5 to 10 times the DS headless; Nostalgia's was 15, Moon's
   210. Where the time goes (the overlays' page marks on every store,
   the interpreter's share, the 2D/3D): a profile before the window's
   real time is judged.
6. Then the PC side (`06-attack-plan.md`): the screens' layout, 60 fps,
   the controls.

Kit changes keep the flow (`10-ndskit.md`); `720c636` is in this port's
`ndskit/`, pc-moon's and pc-nostalgia's (checked, local), and
`D:\Homebrew6\ndskit`. Nothing is pushed until the game plays.

Before starting: MSYS2's tools on PATH; the cartridge in `rom/` and
extracted; `build/recomp` built (the recompiler takes about 10 minutes,
most of it discovering the twenty overlays twice).
