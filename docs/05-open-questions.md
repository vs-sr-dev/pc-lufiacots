# Open questions

What is not known yet, with where to look.

## The anti-piracy

* **What it checks**, and where its answer goes: the three entries the
  program calls (0x021744E0, 0x02174558, 0x021745D0, from 0x02096004;
  the first given a function pointer, 0x02095B6C, its result compared
  with an argument's complement). Session 2: the runtime runs them
  interpreted (frames 501, 515, 518 of a run from a new cartridge), and at
  the title main RAM is melonDS's but for a stream's buffer and ~200
  bytes: nothing shows a failed check. What they read (the cartridge's
  answers, the code's bytes, the backup) is still to trace in the
  interpreter, and a sabotage would show later in play. Its sabotage
  is now read (`03-executables.md`: 32 KiB leaked per failed check at each
  area load), and on the route every check passes; what it reads is
  traced (the DSi's SCFG, ROM reads at 0x8000 timed by the timers, the
  owner's settings), how it judges them is still to read.
* **What 0x02096004 is**, the program's function that calls it (it also
  clears engine B's layers in DISPCNT_B): when in the game it runs.
* **The backup probe**: at the boot the game identifies its backup as a
  64 Kbit EEPROM (0x0D01) and keeps the outcome at 0x02158AFC, which
  nothing reads directly; the save module uses 512 Kbit. Which answer a
  genuine cartridge gives (a 512 Kbit EEPROM answers the probe too:
  identification by type cannot tell the size), and who reads the flag.
* **melonDS's 8 KiB save**: melonDS's game list gives this cartridge a
  64 Kbit EEPROM (a 64 KiB file is cut back to 8 KiB). The game plays on
  it through the prologue; whether saving and loading work there, and
  whether the AP notices, is to try (a save in the first town). Session 2, on the runtime's 64 KiB
  backup: a save and LOAD GAME work; the game wrote only its first 2 KiB.

## The overlays

* **Overlay 1 under overlay 4**: in the dungeon overlay 4 lies over the
  middle of overlay 1 (53.45% of 1's bytes left). Does the game call
  overlay 1's code around it? Session 2: from frame 18 326 of the route
  (the prologue) the runtime dispatches into overlay 1's functions, with
  overlay 4 loaded since 9 018 and its functions still found in memory
  (*inferred* from the log: misses are not logged). The per-function
  residency follows either way.
* **Which overlay is which**, beyond 0 (the anti-piracy), 19 (the
  opening), 4 (the title and the field), 1 (the dungeon or the
  prologue): the towns, the menus, the bosses' (9-18), 5 and 6.

## The ARM7

* **VRAM banks C/D**: the wireless driver is parked in main RAM; whether
  the game ever starts the wireless (it has no multiplayer, *inferred*;
  the Nintendo WFC or a download play?) and so whether the ARM7 ever
  runs code at 0x06000000. The runtime's VRAMCNT trace will say.

## The sound

* **Channels 1 and 3** play PCM16 loops at 32 728 Hz, panned fully left
  and right, during the opening: a stereo buffer filled by the ARM9
  (*inferred*), but the SDAT's stream players use channels 6, 7 and 8.
  Which code fills it (the voices? the game's own mixer?).
* **The `_S` variants** of the 47 pieces of music.

## The code

* **Where the frame loop waits for its two VBlanks** (30 fps), and
  whether a heavier place drops to 20.
* **The Lua VM**: where it is in the program, how scripts are loaded and
  run (by member UID?).
* **The threads** of both CPUs: to list from the runtime's trace.
* **Headless speed**: Nostalgia runs headless at 15 times the DS, Moon at
  210; Lufia 10 times through the opening, 5.5 with pictures on (session
  2). Where the time goes is to profile.

## The oracle

* **Input after a loaded state**: twice, after melonDS loaded a state
  (F1), the game took no button (A, START, a touch) at the title, where a
  fast-forwarded boot takes them. Whether melonDS's state loading or the
  states themselves (taken while fast-forwarding) are the cause.

## Play

* **The controls**: what each button does in this action RPG (attack,
  jump, the IP skills, the party), and what the touch screen does.
