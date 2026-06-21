---
name: build-gallery
description: "Generate the HTML gallery that visualizes the built songs — a landing grid plus a per-song page with the engraved score, the verification audio, and a Synthesia-style falling-notes piano synced to the MP3. Use when asked to visualize/preview/showcase the songs, build an index/gallery/website for the lead sheets, or see the generated files in a browser."
---

# Build the song gallery

`leadsheet gallery` scans the songs and writes a self-contained, dependency-free
website under `data/gallery/`. **Each song folder is also its own source folder** —
the `.ly` lives there and the build writes its artifacts in place, so the gallery
generates `index.html` + `notes.json` alongside them (no copying):

```
data/gallery/
  index.html              landing grid (one card per song)   [regenerable]
  assets/style.css, app.js   shared, no CDN/JS deps           [regenerable]
  <song>/
    <song>.ly             the source (kept by `task clean`)
    <song>.pdf/.mp3/_preview-1.png   built in place
    index.html            score image + audio player + falling-notes piano
    notes.json            per-note timeline [[midi, start_sec, dur_sec], ...]
```

(A legacy flat `data/<song>.ly` still works — its artifacts get copied into
`data/gallery/<song>/`.)

## Run it

The gallery is refreshed **automatically at the end of every `leadsheet build`**,
which prints a `file://` link to the landing page. So normally you don't run it
by hand — just build. To regenerate on its own (or open it):

```bash
uv run leadsheet gallery          # (re)write data/gallery/
uv run leadsheet gallery --open   # ...and open it in a browser
task gallery                      # equivalent
uv run leadsheet build --no-gallery   # build WITHOUT refreshing the gallery
```

Then `open data/gallery/index.html`.

## Build the songs first

The gallery only shows what's already been built. For complete cards, run a full
build **with previews** beforehand:

```bash
uv run leadsheet build --png      # PDF + MP3 + page-1 PNG for every song
uv run leadsheet gallery
```

Missing artifacts degrade gracefully — a song with no `_preview-1.png` shows a ♪
placeholder; no `.mp3` shows a note instead of the player; the piano still works
as long as the `.ly` has a `\midi` block.

## How the piano visualization works

- The MP3 is synthesized **from the MIDI**, so note timings line up exactly with
  the audio. The generator re-engraves each `.ly` to MIDI (`engine.render_midi`),
  reads it with **music21**, and converts quarter-note offsets to seconds via the
  score tempo → `notes.json`.
- Each song page inlines its note data as `window.SONG` (so it works over
  `file://` with no fetch), then `assets/app.js` drives a `<canvas>`: notes fall
  down a lane and light the keys as they land, following `audio.currentTime`. Press
  Play (or use the audio controls) and the piano stays in sync. Color = pitch class.

## Code map

- `src/leadsheet/gallery.py` — generator (`build_gallery`, `collect_songs`,
  `parse_header`, `extract_notes`, page templates).
- `src/leadsheet/gallery_assets/{style.css,app.js}` — the design + canvas engine,
  copied verbatim into `data/gallery/assets/` on build. **Edit the look here**, not
  in the generated copy (which is overwritten every run).
- `tests/test_gallery.py` — pure-helper tests (header parsing, page rendering,
  folder layout); note extraction is stubbed so the tests need no LilyPond.

`data/gallery/` is regenerable and git-ignored; `task clean` removes it.

See also: `render-leadsheet` (build the PDFs/MP3s the gallery shows),
`add-song` / `transcribe-tune` (get songs into `data/` first).
