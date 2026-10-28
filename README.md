# Inky Claude/Codex Usage Display

Claude and Codex usage, turned into a little desk artwork.

A Raspberry Pi Zero 2 W and a seven-colour e-ink display show your remaining
allowance and reset times. The numbers live inside the illustration: speech
balloons, tentacle coils, reactor tanks, shop signs, moth wings, and a pinball playfield.

| Budget Kraken | Pop Comic |
| --- | --- |
| [![Budget Kraken mockup: usage balances woven into an engraved octopus illustration.](designs/integrated-v2/02-budget-kraken-concept.png)](designs/integrated-v2/02-budget-kraken-concept.png) | [![Pop Comic mockup: usage balances inside the thought balloons of a colourful comic portrait.](designs/integrated-v2/01-pop-comic-concept.png)](designs/integrated-v2/01-pop-comic-concept.png) |
| **Reactor Room** | **Night Market** |
| [![Reactor Room mockup: balances painted onto two enormous industrial tanks.](designs/integrated-v2/03-reactor-room-concept.png)](designs/integrated-v2/03-reactor-room-concept.png) | [![Night Market mockup: balances and reset times on the signs of a rainy street.](designs/integrated-v2/04-night-market-concept.png)](designs/integrated-v2/04-night-market-concept.png) |
| **Quota Moth** | **Cosmic Pinball** |
| [![Quota Moth mockup: balances integrated into the wings of a botanical moth illustration.](designs/integrated-v2/05-quota-moth-concept.png)](designs/integrated-v2/05-quota-moth-concept.png) | [![Cosmic Pinball mockup: balances and reset details in a psychedelic pinball playfield.](designs/integrated-v2/06-cosmic-pinball-concept.png)](designs/integrated-v2/06-cosmic-pinball-concept.png) |

*Digital concept mockups with frozen example readings; click any image for the full
600 × 448 view. The live display draws current values into matching clean artwork
plates. Physical e-ink colours differ from these RGB previews.*

## On the desk

- **Real usage at a glance.** Claude and Codex remaining allowance, session and scoped
  limits, reset times, and Codex reset-credit availability.
- **Six artworks to cycle through.** Original ImageGen compositions with live text
  drawn into the artwork's own shapes and surfaces.
- **A slower kind of screen.** The Pi polls usage every ten minutes. A full refresh takes
  about 34 seconds, and the image stays visible when the display loses power.
- **Honest about freshness.** Old observations are marked stale; missing data stays
  missing. Collection and button controls run on the Pi, independently of the Mac.

The four buttons on the side of the display choose the artwork:

| A | B | C | D |
| --- | --- | --- | --- |
| Previous | Next | Random | Budget Kraken |

Presses during a refresh select what appears next. The latest selection is kept,
and the chosen artwork survives a restart.

## Make one

The tested hardware is a **Raspberry Pi Zero 2 W** and the original **Pimoroni Inky
Impression 5.7-inch, seven-colour, 600 × 448** display. This particular panel is
discontinued; the code checks its identity before driving it.

The Pi collects usage directly from CLIProxyAPI over HTTPS, renders the artwork,
and drives the display. A systemd timer runs every ten minutes; the Mac is only
needed for initial setup. Vendor OAuth tokens stay on the proxy. The Pi stores
its management credential in protected configuration outside the repository.

**[Hardware, installation, and operations →](docs/hardware-and-operations.md)**

You can try image generation locally without hardware or an account:

```sh
uv sync
uv run python -m inky_frame sample /tmp/inky-preview.png
```

## The artwork

The project began with twelve illustration studies and evolved into these six
full-screen compositions. The original mockups, higher-resolution masters, clean
plates, seven-colour proofs, and exact generation prompts are all preserved.

- [Six integrated compositions and prompts](designs/integrated-v2/README.md)
- [Clean artwork plates used by the live renderer](assets/live/README.md)
- [Earlier design study and rendering notes](docs/hardware-and-operations.md#usage-display-design-study)

## License

Project code is [MIT licensed](LICENSE). Fonts retain their OFL licenses, and
manufacturer references retain their original rights. See [third-party notices](THIRD_PARTY.md).
