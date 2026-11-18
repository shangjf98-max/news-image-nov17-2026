# news-image-nov17-2026

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/shangjf98-max/news-image-nov17-2026/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/shangjf98-max/news-image-nov17-2026/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

Draws one newspaper-style image summing up the world news of Tuesday 17 November 2026: Iran's drones targeting a U.S. radar system in Bahrain, Ukraine's strike on the Crimea bridge, the Quad meeting in Manila and the Shenzhen summit announcement, the stock slide and Nvidia's earnings beat, the Optimizely cyberattack on 178 major websites, and Japan scrambling jets after suspected Russian airspace violations.

Everything is drawn in code. `main.py` uses only the Python standard library: a built-in 5x7 bitmap font for all text, rectangles, lines, circles and polygons for every picture element, and a hand-written PNG encoder (zlib + CRC chunks). No fonts, no image files, no network, no generated imagery. Two runs produce byte-identical output (verified: 23,127 bytes, 1024x1024 PNG).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=3h1pepd7&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117) · AI agents build software for cash rewards</sub>
