# The recompiler: Lufia's programs to C++

ndskit's recompiler (`python -m ndskit.recomp`; pc-moon's and
pc-nostalgia's `09-recompiler.md`) turns both programs and the twenty
overlays into C++, one module each.

```sh
ROM="rom/Lufia - Curse of the Sinistrals (USA).nds"
python -m ndskit.recomp "$ROM" --out build/recomp --optest           # about 10 minutes, most of it discovery
cmake -S build/recomp -B build/recomp/b -G Ninja -DCMAKE_CXX_COMPILER=clang++ && ninja -C build/recomp/b
python -m ndskit.recomp.selftest "$ROM" --cpu 9 --auto --out build/vectors/arm9.txt
python -m ndskit.recomp.selftest "$ROM" --cpu 7 --auto --out build/vectors/arm7.txt
python -m ndskit.recomp.selftest "$ROM" --cpu 9 --overlay 1 --auto --out build/vectors/ov1.txt
python -m ndskit.recomp.selftest "$ROM" --cpu 9 --overlay 14 --auto --out build/vectors/ov14.txt
V="build/recomp/selftest/optest9.txt build/recomp/selftest/optest7.txt build/vectors/arm9.txt build/vectors/arm7.txt build/vectors/ov1.txt build/vectors/ov14.txt"
build/recomp/b/selftest $V               # the recompiled code
build/recomp/b/selftest --interp $V      # the runtime's interpreter, on the same vectors
```

## What it makes

| Module | Functions | Instructions |
|---|---|---|
| ARM9 (the program, with what its overlays reach) | 11 542 | 367 002 |
| ARM9_OV0 .. OV19 | 10, 791, 0, 59, 252, 164, 131, 56, 242, 329, 166, 256, 374, 423, 597, 271, 206, 276, 113, 365 | |
| ARM7 | 1 058 | 37 228 |
| OPTEST9 / OPTEST7 (ndskit's instruction test) | 3 750 / 3 548 | |

23 modules, about 25 000 functions and 570 000 instructions, 109 files;
the build takes a few minutes with clang.

* **One function is left to the interpreter**: overlay 0's initialiser
  at 0x021757D4, whose discovered body runs into encrypted bytes
  (`ldrb pc, [sp, #0xe81]!`, an instruction no compiler writes). The
  emitter now makes such a function a call to the runtime's interpreter
  instead of stopping (`report.txt` lists them); the interpreter runs
  whatever the bytes are when it is called.
* **The program's module carries its stored image** (kind "loaded":
  0xD3D90 bytes, compressed) beside its segments, so that the runtime
  finds it at the boot (`11-runtime.md`).
* **Each overlay function's extent and crc32** (its code and the literal
  pools it folds) replace pc-nostalgia's ranges, first instructions and
  samples: the runtime decides per function which overlay is in memory.

## What the self-test found

* **Thumb switches**: CodeWarrior's (`add r0, pc; ldrh r0, [r0, #6];
  lsls; asrs; add pc, r0`), new to the emitter with this game (session 1
  taught discovery). The emitter read `add pc, r0`'s pc as the
  word-aligned pc + 4, as Thumb's `adr` and literal loads do; the high
  register `add` reads it as it is. Every switch whose `add pc` lies at
  an address 2 mod 4 jumped two bytes short: the game's first stop
  (`returned to 0201760B, expected 02017559`, VBlank 509). The instruction
  test now has the switch at both alignments.
* **A Thumb thunk into ARM code**: CodeWarrior's this-adjusting thunks
  end `ldr r2, =f; push {r2}; mov r2, r12; pop {pc}`, which discovery
  took for a return (45 failures in the program's vectors, then a memory
  difference that ends the file). Discovery now follows a known word
  pushed alone and popped into pc as a jump there.
* **`--auto`'s choice**: a function that pops a pc its caller pushed (the
  SDK's rescheduler's tail, in the ITCM) ran in armemu from address 0 (the
  ITCM's mirror) back to the sentinel by chance, and was taken for a pure
  function. A vector may now run only code discovery found.
* **The ARM7's VRAM segment** cannot be loaded in the test's memory: it
  and its functions are left out of the ARM7's vectors (and the runtime's
  module check skips a segment where it holds no memory).

| Vectors | Functions | Vectors | Recompiled | Interpreted |
|---|---|---|---|---|
| the instruction test, both CPUs | 7 296 | 57 781 | 0 failures | 0 failures |
| the ARM9 program's functions that run alone | 4 311 | 68 018 | 0 (45 before the thunks were followed) | 0 failures |
| the ARM7's | 124 | 1 970 | 0 | 0 |
| overlay 1's (621 of 791 functions Thumb) | 328 | 5 188 | 0 | 0 |
| overlay 14's | 270 | 4 274 | 0 | 0 |
