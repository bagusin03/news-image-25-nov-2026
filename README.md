# The World Today — Wednesday 25 November 2026

A make.fun news-image entry: a program that draws one newspaper front page
summing up the world's news of Wednesday 25 November 2026 and writes it to
`/output/entry.png` (1024×1024 PNG, under 1 MiB).

Stories in the image (all first reported on 25 November 2026):

- **Huawei convicted** — a US jury in Brooklyn finds Huawei guilty on 10 of
  12 counts (bank fraud, wire fraud, sanctions violations, conspiring to steal
  trade secrets); acquitted of racketeering.
- **Riyadh tower hit** — a Houthi strike hits Riyadh's tallest tower, the PIF
  Tower, for the second time in five days; 11 people injured.
- **Ukraine strikes** — Zelensky confirms Ukraine struck Russian vessels in
  the Gulf of Finland and off Benghazi, Libya.
- **Sarkozy to trial** — former French president Nicolas Sarkozy and Carla
  Bruni are ordered to trial over the Libya campaign-financing case.
- **NATO jets to Poland** — AWACS early-warning aircraft approved for Poland
  after Russian missiles landed there.
- **England level the T20 series** — an eight-wicket win over Australia,
  chasing 185, makes it 1–1.

Also today: the US blacklists Megaspeed over Nvidia chip diversion, Nvidia
reinstates Jensen Huang as chief executive, Trump pardons the Thanksgiving
turkeys Freedom and Feathers, and Rudy Giuliani receives the Presidential
Medal of Freedom.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3.13 main.py
```

Pure Python 3.13 standard library, no network, no clock, no randomness:
two runs write byte-identical output.
