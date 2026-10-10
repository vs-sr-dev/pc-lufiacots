# Curiosities

Things found on the way that the port does not need.

* **The header's title is `ESTPOLIS DS`**, the series' Japanese name
  (*Estpolis Denki*), in the US release; the banner says "Lufia: Curse of
  the Sinistrals" in all six languages.
* **The music's archive is on the cartridge twice**: as the file
  `sound/bgm_sound_data.sdat` and as member 11 383 of `mcd.dat`, the same
  2 090 816 bytes.
* **The archive's index remembers where it was built**: `mcd_compact.bin`
  carries the path `..\..\rom\mcd.dat`, the developers' relative path.
* **The text was signed**: both text files open with "TEXT RESOURCE
  2009/11/09 23:50", the date their tool wrote them.
* **The Japanese text is gone**: `text/ResourceText.bin` is empty in this
  release; `text/ResourceText_us.bin` holds the English.
* **A Lua with integers**: the scripts' bytecode declares 4-byte integral
  numbers, a Lua 5.1.4 built without floating point (the DS has no FPU).
* **The voices' names** are the characters' internal names: MAXIM,
  SELENA, GUY, TEAR, ARTY, HEIDEGGER, IRIS, GADES, IDURA, AMON, DIOS,
  GEMINE, JIMMY, MILKA, LEXUS, JJ (*inferred*: TEAR and ARTY are the
  English Tia and Artea).
* **Every piece of music twice**: 47 sequences `SEQ_BGM01`-`47` and a
  `SEQ_BGMnn_S` beside each, on the same bank, a little different in size
  (*inferred*: a variant for another situation, a quieter mix or a
  shorter loop).
* **The anti-piracy's addresses are offset**: the blocks its stubs list
  are written 0x1000 bytes above where they are, and their lengths as
  addresses past the overlay's end (0x02176D20 + length): no word in the
  table points into the code it hides (*inferred*: that is the point).
* **The opening cannot be skipped**, on the first boot as on later ones:
  4 minutes 20 seconds of 3D with the staff's names before the title.
* **L+R+START+SELECT** is checked in the game's loop: the soft reset.
