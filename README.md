[![news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/qsc985/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/qsc985/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126)

# The World in One Day — Thursday 26 November 2026

An entry for the [make.fun](https://make.fun/bounty/news-image-20261126)
competition **news-image-20261126**: *Sum up 26 November's world news in one image*.

`main.py` (Python 3, standard library only — no network, no third-party
packages) draws a front-page style infographic, 1024×1024, and writes it to
`$MAKEFUN_OUTPUT_DIR/entry.png` (or `/output/entry.png`). It uses its own
5×7 bitmap font and a hand-written PNG encoder, so the two runs the grader
performs produce byte-identical output.

## The day's news in the image

- **Lead — Trade:** the US unveils sweeping new tariffs on China, the EU and
  12 other partners on the eve of Thanksgiving; China faces an extra 20%,
  taking some goods to 45%.
- **Energy:** oil jumps as Yemen's Houthis claim a strike on Saudi Arabia's
  Ras Tanura refinery; Brent crude tops $94.
- **Disaster:** a fuel-tanker crash sets a crowded Cairo highway ablaze,
  killing at least 30 people.
- **Space:** the first Pakistani astronaut reaches China's Tiangong space
  station.
- **Peace:** Colombia marks 10 years since its historic peace agreement.
- **Science:** close-up images reveal a stadium-sized crater on the asteroid
  deliberately struck to test Earth's defences.
- **Also today:** Thanksgiving Day in the US (Macy's parade postponed by
  storms), Duran Duran guitarist Andy Taylor dies at 65, and Israeli judges
  urge dropping the top charges against Netanyahu.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png — a 1024x1024 PNG, under 1 MiB
```

## License

MIT — see [LICENSE](LICENSE).
