"""Command-line interface:  leadsheet build | ls | demo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import engine


def _default_root() -> Path:
    data = Path("data")
    return data if data.is_dir() else Path(".")


def _regenerate_gallery(root: Path, *, open_browser: bool = False) -> None:
    """(Re)build the HTML gallery and print a clickable file:// link to it."""
    from . import gallery

    landing = gallery.build_gallery(root, open_browser=open_browser)
    print(f"  gallery -> {landing.resolve().as_uri()}")


def cmd_ls(args: argparse.Namespace) -> int:
    root = args.dir or _default_root()
    songs = engine.discover_songs(root)
    if not songs:
        print(f"no songs in {root}/")
        return 0
    for ly in songs:
        print(ly.stem)
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    root = args.dir or _default_root()
    songs = (
        [engine.resolve_song(s, root) for s in args.songs]
        if args.songs
        else engine.discover_songs(root)
    )
    if not songs:
        raise engine.BuildError(f"no .ly songs found in {root}/")

    soundfont = args.soundfont or (engine.find_soundfont() if args.audio else None)
    if args.audio and soundfont:
        print(f"soundfont: {soundfont}")

    for ly in songs:
        print(f"building {ly.name} ...")
        outputs = engine.build_one(
            ly,
            soundfont=soundfont,
            audio=args.audio,
            png=args.png,
            open_pdf=args.open_pdf,
        )
        print("  -> " + ", ".join(v.name for v in outputs.values()))

    # The gallery is regenerated automatically so the HTML always reflects the
    # latest build (disable with --no-gallery).
    if args.gallery:
        print("refreshing gallery ...")
        _regenerate_gallery(root)
    return 0


def cmd_corpus(args: argparse.Namespace) -> int:
    """Engrave the .ly songs to ground-truth MIDI + synthesized WAV pairs."""
    from . import corpus

    root = args.dir or _default_root()
    songs = engine.discover_songs(root)
    if not songs:
        raise engine.BuildError(f"no .ly songs found in {root}/")

    soundfont = args.soundfont or engine.find_soundfont()
    if soundfont:
        print(f"soundfont: {soundfont}")

    out = root / "corpus"
    print(f"building reference corpus in {out}/ ...")
    items = corpus.build_corpus(songs, out, soundfont=soundfont)
    print(f"  -> {len(items)} piece(s)")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Transcribe corpus audio back to notes and score against the ground truth."""
    from . import corpus, verify

    root = args.dir or _default_root()
    corpus_dir = root / "corpus"
    items = corpus.load_corpus(corpus_dir)
    if not items:
        raise engine.BuildError(
            f"no corpus in {corpus_dir}/ — run 'leadsheet corpus' first"
        )

    if args.engine == "piano":
        transcriber: verify.Transcriber = verify.PianoTranscriber(device=args.device)
    else:
        transcriber = verify.OracleTranscriber()

    print(f"verifying {len(items)} piece(s) with {transcriber.name} ...")
    verify.verify_corpus(items, transcriber, est_dir=corpus_dir / "est")
    return 0


def cmd_gallery(args: argparse.Namespace) -> int:
    """Generate a self-contained HTML gallery (with falling-notes piano viz)."""
    root = args.dir or _default_root()
    if not engine.discover_songs(root):
        raise engine.BuildError(f"no .ly songs found in {root}/")

    print(f"building gallery from {root}/ ...")
    _regenerate_gallery(root, open_browser=args.open_browser)
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    """Build a song in Python with music21, then render it through the engine."""
    from .compose import demo_song

    root = args.dir or _default_root()
    root.mkdir(parents=True, exist_ok=True)
    song = demo_song()
    print("notes:", " ".join(song.note_names))

    midi = song.to_midi(root / "demo.mid")
    print(f"  -> {midi.name}")

    if args.audio:
        soundfont = args.soundfont or engine.find_soundfont()
        if soundfont:
            mp3 = engine.midi_to_mp3(midi, root / "demo.mp3", soundfont, what="demo")
            print(f"  -> {mp3.name}")
        else:
            print("  note: no soundfont — skipping audio")

    try:
        pdf = song.render_pdf(root / "demo")
        print(f"  -> {Path(pdf).name}")
    except Exception as exc:  # music21's LilyPond export is best-effort
        print(f"  note: PDF render via music21 skipped ({exc})")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="leadsheet",
        description="Render LilyPond lead sheets to PDF + audio; compose with music21.",
    )
    parser.add_argument(
        "--dir", type=Path, default=None,
        help="songs directory (default: ./data if present, else .)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    pb = sub.add_parser("build", help="render songs to PDF + MP3")
    pb.add_argument("songs", nargs="*", help="song name(s) or .ly path(s)")
    pb.add_argument("--no-audio", dest="audio", action="store_false",
                    help="PDF only, skip MP3")
    pb.add_argument("--png", action="store_true", help="also write a page-1 PNG")
    pb.add_argument("--no-gallery", dest="gallery", action="store_false",
                    help="skip the automatic HTML gallery refresh")
    pb.add_argument("--open", dest="open_pdf", action="store_true",
                    help="open each PDF (macOS)")
    pb.add_argument("--soundfont", help="path to a .sf2 soundfont")
    pb.set_defaults(func=cmd_build)

    pl = sub.add_parser("ls", help="list songs in the songs directory")
    pl.set_defaults(func=cmd_ls)

    pc = sub.add_parser(
        "corpus", help="build reference MIDI+WAV pairs from the .ly songs"
    )
    pc.add_argument("--soundfont", help="path to a .sf2 soundfont")
    pc.set_defaults(func=cmd_corpus)

    pv = sub.add_parser(
        "verify", help="transcribe corpus audio and score it against the ground truth"
    )
    pv.add_argument(
        "--engine", choices=["oracle", "piano"], default="oracle",
        help="transcription engine (default: oracle — no ML deps)",
    )
    pv.add_argument("--device", default="cpu", help="torch device for the piano engine")
    pv.set_defaults(func=cmd_verify)

    pg = sub.add_parser(
        "gallery", help="generate an HTML gallery with a falling-notes piano viz"
    )
    pg.add_argument("--open", dest="open_browser", action="store_true",
                    help="open the gallery in a browser when done")
    pg.set_defaults(func=cmd_gallery)

    pd = sub.add_parser("demo", help="compose a song with music21 and render it")
    pd.add_argument("--no-audio", dest="audio", action="store_false",
                    help="skip MP3")
    pd.add_argument("--soundfont", help="path to a .sf2 soundfont")
    pd.set_defaults(func=cmd_demo)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except engine.BuildError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
